import secrets

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from .models import ApprovalRequest, CredentialDelivery, Role, User, UserRole
from .permissions import IsPlatformPortal, PasswordChanged, require
from .platform_serializers import (
    AccountCreateSerializer,
    AccountUpdateSerializer,
    DecisionSerializer,
)
from .services import role_codes, send_credentials_email, write_audit


def account_data(user):
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "status": user.status,
        "roles": role_codes(user),
        "created_at": user.created_at.isoformat(),
        "created_by": str(user.created_by_id) if user.created_by_id else None,
    }


def approval_data(approval):
    subject = approval.subject_user
    return {
        "id": str(approval.id),
        "request_type": approval.request_type,
        "status": approval.status,
        "subject": {
            "id": str(subject.id),
            "full_name": subject.full_name,
            "email": subject.email,
            "roles": role_codes(subject),
        },
        "requested_by": {
            "id": str(approval.requested_by_id),
            "full_name": approval.requested_by.full_name,
        },
        "created_at": approval.created_at.isoformat(),
        "decided_by": approval.decided_by.full_name if approval.decided_by_id else None,
        "decided_at": approval.decided_at.isoformat() if approval.decided_at else None,
        "decision_note": approval.decision_note,
    }


class PlatformAccountViewSet(ViewSet):
    """Add, edit, delete, and view one kind of platform account."""

    entity = None  # permission name, like "platform_hr"
    allowed_roles = []  # role codes that can be given to this kind of account
    default_roles = []  # used when the form sends no roles
    protected_roles = []  # accounts with these roles cannot be deleted here
    needs_approval = False
    request_type = None

    lookup_value_regex = "[0-9a-fA-F-]{36}"

    ACTION_PERMISSION = {
        "list": "view",
        "retrieve": "view",
        "create": "create",
        "partial_update": "update",
        "destroy": "delete",
    }

    def get_permissions(self):
        action = self.ACTION_PERMISSION.get(self.action, "view")
        return [
            IsAuthenticated(),
            PasswordChanged(),
            IsPlatformPortal(),
            require(f"{self.entity}.{action}")(),
        ]

    # ---- helpers ----

    def accounts(self):
        return (
            User.objects.filter(
                school__isnull=True,
                deleted_at__isnull=True,
                user_roles__role__scope="platform",
                user_roles__role__code__in=self.allowed_roles,
            )
            .distinct()
            .order_by("-created_at")
        )

    def get_user(self, pk):
        try:
            return self.accounts().get(pk=pk)
        except (User.DoesNotExist, DjangoValidationError, ValueError):
            raise NotFound("Account not found.")

    def check_roles(self, codes):
        codes = list(dict.fromkeys(codes))
        bad = [c for c in codes if c not in self.allowed_roles]
        if not codes or bad:
            raise ValidationError(
                {"roles": f"Choose from: {', '.join(self.allowed_roles)}"}
            )
        return codes

    def before_create(self, request):
        """Subclasses can do extra work here."""

    # ---- actions ----

    def list(self, request):
        return Response([account_data(u) for u in self.accounts()])

    def retrieve(self, request, pk=None):
        return Response(account_data(self.get_user(pk)))

    @transaction.atomic
    def create(self, request):
        serializer = AccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        codes = self.check_roles(data.get("roles") or self.default_roles)
        roles = list(Role.objects.filter(scope="platform", code__in=codes))

        self.before_create(request)

        temp_password = secrets.token_urlsafe(9)
        user = User.objects.create_user(
            email=data["email"],
            password=temp_password,
            full_name=data["full_name"],
            phone=data.get("phone", ""),
            status="pending_approval" if self.needs_approval else "active",
            must_change_password=True,
            created_by=request.user,
        )
        for role in roles:
            UserRole.objects.create(user=user, role=role, assigned_by=request.user)

        if self.needs_approval:
            approver = Role.objects.get(scope="platform", code="approvals_admin")
            ApprovalRequest.objects.create(
                request_type=self.request_type,
                subject_user=user,
                requested_by=request.user,
                approver_role=approver,
            )

        CredentialDelivery.objects.create(
            user=user, method="paper", sent_by=request.user, status="printed"
        )
        email_status = "not_requested"
        if data["send_email"]:
            try:
                send_credentials_email(user, temp_password)
                email_status = "sent"
            except Exception:
                email_status = "failed"
            CredentialDelivery.objects.create(
                user=user, method="email", sent_by=request.user, status=email_status
            )

        write_audit(
            request.user, "create", "users", user.id, None,
            {"email": user.email, "roles": codes, "status": user.status},
        )

        result = account_data(user)
        result["temporary_password"] = temp_password
        result["email_status"] = email_status
        return Response(result, status=201)

    @transaction.atomic
    def partial_update(self, request, pk=None):
        user = self.get_user(pk)
        serializer = AccountUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        old = account_data(user)
        if "full_name" in data:
            user.full_name = data["full_name"]
        if "phone" in data:
            user.phone = data["phone"]
        user.save()

        if "roles" in data:
            codes = self.check_roles(data["roles"])
            UserRole.objects.filter(
                user=user, role__scope="platform", role__code__in=self.allowed_roles
            ).delete()
            for role in Role.objects.filter(scope="platform", code__in=codes):
                UserRole.objects.create(user=user, role=role, assigned_by=request.user)

        new = account_data(user)
        write_audit(request.user, "update", "users", user.id, old, new)
        return Response(new)

    @transaction.atomic
    def destroy(self, request, pk=None):
        user = self.get_user(pk)
        if user.pk == request.user.pk:
            raise ValidationError({"detail": "You cannot delete your own account."})
        if set(role_codes(user)) & set(self.protected_roles):
            raise ValidationError({"detail": "This account cannot be deleted here."})

        old = account_data(user)
        user.status = "inactive"
        user.deleted_at = timezone.now()
        user.save(update_fields=["status", "deleted_at", "updated_at"])
        write_audit(request.user, "delete", "users", user.id, old, {"status": "inactive"})
        return Response(status=204)


class CommitteeViewSet(PlatformAccountViewSet):
    entity = "committee_member"
    allowed_roles = ["committee_member"]
    default_roles = ["committee_member"]
    protected_roles = ["md"]


class OwnerViewSet(PlatformAccountViewSet):
    entity = "owner_account"
    allowed_roles = ["owner"]
    default_roles = ["owner"]

    def before_create(self, request):
        # A new Owner replaces the old Owner.
        for old in list(self.accounts()):
            old.status = "inactive"
            old.deleted_at = timezone.now()
            old.save(update_fields=["status", "deleted_at", "updated_at"])
            write_audit(
                request.user, "replace_owner", "users", old.id,
                {"status": "active"}, {"status": "inactive"},
            )


class AdminViewSet(PlatformAccountViewSet):
    entity = "platform_admin"
    allowed_roles = ["onboarding_admin", "system_admin", "operations_admin", "approvals_admin"]


class HRViewSet(PlatformAccountViewSet):
    entity = "platform_hr"
    allowed_roles = ["associate_manager_hr", "marketing_hr"]
    needs_approval = True
    request_type = "hr_account"


class AssociateViewSet(PlatformAccountViewSet):
    entity = "platform_associate"
    allowed_roles = ["support_associate", "reports_associate"]
    needs_approval = True
    request_type = "associate_account"


class ApprovalListView(APIView):
    permission_classes = [
        IsAuthenticated, PasswordChanged, IsPlatformPortal, require("approval_request.view"),
    ]

    def get(self, request):
        wanted = request.query_params.get("status", "pending")
        if wanted not in ("pending", "accepted", "rejected"):
            raise ValidationError({"status": "Use pending, accepted, or rejected."})
        requests = (
            ApprovalRequest.objects.filter(school__isnull=True, status=wanted)
            .select_related("subject_user", "requested_by", "decided_by")
            .order_by("-created_at")
        )
        return Response([approval_data(a) for a in requests])


class ApprovalDecisionView(APIView):
    permission_classes = [
        IsAuthenticated, PasswordChanged, IsPlatformPortal, require("approval_request.update"),
    ]

    @transaction.atomic
    def post(self, request, pk):
        try:
            approval = (
                ApprovalRequest.objects.select_for_update()
                .select_related("subject_user", "requested_by", "decided_by")
                .get(pk=pk, school__isnull=True)
            )
        except (ApprovalRequest.DoesNotExist, DjangoValidationError, ValueError):
            raise NotFound("Request not found.")

        if approval.status != "pending":
            raise ValidationError({"detail": "This request is already decided."})
        if approval.requested_by_id == request.user.id:
            raise ValidationError({"detail": "You cannot decide your own request."})

        serializer = DecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        accept = serializer.validated_data["decision"] == "accept"

        approval.status = "accepted" if accept else "rejected"
        approval.decided_by = request.user
        approval.decided_at = timezone.now()
        approval.decision_note = serializer.validated_data.get("note", "")
        approval.save()

        subject = approval.subject_user
        subject.status = "active" if accept else "rejected"
        subject.save(update_fields=["status", "updated_at"])

        write_audit(
            request.user, "accept" if accept else "reject", "approval_requests", approval.id,
            {"status": "pending"}, {"status": approval.status, "user": subject.email},
        )
        return Response(approval_data(approval))