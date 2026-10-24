from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from common.models import BaseModel, SoftDeleteModel


class School(SoftDeleteModel):
    TYPES = [("school", "School"), ("college", "College")]
    STATUSES = [("active", "Active"), ("suspended", "Suspended"), ("inactive", "Inactive")]

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPES)
    code = models.CharField(max_length=30, unique=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default="active")
    registered_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    registered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "schools"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin, SoftDeleteModel):
    STATUSES = [
        ("pending_approval", "Pending approval"),
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("rejected", "Rejected"),
    ]

    school = models.ForeignKey(
        School, null=True, blank=True, on_delete=models.PROTECT, related_name="users"
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default="active")
    must_change_password = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    roles = models.ManyToManyField(
        "Role", through="UserRole", through_fields=("user", "role"), related_name="users"
    )

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"

    @property
    def is_active(self):
        return self.status == "active" and self.deleted_at is None


class Role(BaseModel):
    SCOPES = [("platform", "Platform"), ("school", "School/College")]

    scope = models.CharField(max_length=10, choices=SCOPES)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        "Permission", db_table="role_permissions", related_name="roles", blank=True
    )

    class Meta:
        db_table = "roles"
        unique_together = [("scope", "code")]


class Permission(BaseModel):
    code = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "permissions"


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_users")
    assigned_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_roles"
        unique_together = [("user", "role")]


class CredentialDelivery(BaseModel):
    METHODS = [("email", "Email"), ("paper", "Paper")]
    STATUSES = [("sent", "Sent"), ("failed", "Failed"), ("printed", "Printed")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credential_deliveries")
    method = models.CharField(max_length=10, choices=METHODS)
    sent_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    sent_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUSES, default="sent")

    class Meta:
        db_table = "credential_deliveries"


class ApprovalRequest(BaseModel):
    TYPES = [
        ("hr_account", "HR account"),
        ("associate_account", "Associate account"),
        ("coordinator_account", "Coordinator account"),
    ]
    STATUSES = [("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")]

    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.PROTECT)
    request_type = models.CharField(max_length=30, choices=TYPES)
    subject_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="approval_requests"
    )
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    approver_role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="+")
    status = models.CharField(max_length=10, choices=STATUSES, default="pending")
    decided_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    decision_note = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "approval_requests"


class AuditLog(BaseModel):
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=50)
    table_name = models.CharField(max_length=100)
    record_id = models.CharField(max_length=64)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "audit_logs"