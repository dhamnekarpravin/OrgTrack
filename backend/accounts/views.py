from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsPlatformPortal, IsSchoolPortal, PasswordChanged, require
from .serializers import ChangePasswordSerializer, LoginSerializer, ProfileSerializer
from .services import permission_codes, role_codes


def user_info(user, portal):
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "school_id": str(user.school_id) if user.school_id else None,
        "portal": portal,
        "roles": role_codes(user),
        "permissions": sorted(permission_codes(user)),
        "must_change_password": user.must_change_password,
    }


class BaseLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    portal = None  # "platform" or "school"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data["email"].strip(),
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response({"detail": "Wrong email or password."}, status=401)

        is_platform_user = user.school_id is None
        if (self.portal == "platform") != is_platform_user:
            return Response(
                {"detail": "This account cannot sign in on this website."}, status=403
            )

        if user.school_id and user.school.status != "active":
            return Response(
                {"detail": "This school or college is not active."}, status=403
            )

        refresh = RefreshToken.for_user(user)
        refresh["portal"] = self.portal
        if user.school_id:
            refresh["school_id"] = str(user.school_id)

        update_last_login(None, user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_info(user, self.portal),
            }
        )


class PlatformLoginView(BaseLoginView):
    portal = "platform"


class SchoolLoginView(BaseLoginView):
    portal = "school"


class ChangePasswordView(APIView):
    allow_password_change_pending = True

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": ["Old password is wrong."]}, status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.must_change_password = False
        user.save(update_fields=["password", "must_change_password", "updated_at"])
        return Response({"detail": "Password changed."})


class MeView(APIView):
    allow_password_change_pending = True

    def get(self, request):
        return Response(user_info(request.user, request.auth.get("portal")))

    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(user_info(request.user, request.auth.get("portal")))


# ---- Test pages. We remove these later. ----

class PlatformPingView(APIView):
    permission_classes = [IsAuthenticated, PasswordChanged, IsPlatformPortal]

    def get(self, request):
        return Response({"detail": "Platform website access is OK."})


class SchoolPingView(APIView):
    permission_classes = [IsAuthenticated, PasswordChanged, IsSchoolPortal]

    def get(self, request):
        return Response({"detail": "School/College website access is OK."})


class FinanceCheckView(APIView):
    permission_classes = [
        IsAuthenticated,
        PasswordChanged,
        IsPlatformPortal,
        require("finance.view"),
    ]

    def get(self, request):
        return Response({"detail": "You can view finance."})


class MarksCheckView(APIView):
    permission_classes = [
        IsAuthenticated,
        PasswordChanged,
        require("student_marks.create"),
    ]

    def get(self, request):
        return Response({"detail": "You can add marks."})