from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Role, School, User, UserRole

PASSWORD = "Strong#Pass123"


def make_user(email, role_code=None, school=None, must_change=False, scope="platform"):
    user = User.objects.create_user(
        email=email,
        password=PASSWORD,
        full_name="Test User",
        school=school,
        must_change_password=must_change,
    )
    if role_code:
        role = Role.objects.get(scope=scope, code=role_code)
        UserRole.objects.create(user=user, role=role)
    return user


def login(client, email, portal, password=PASSWORD):
    return client.post(
        f"/api/auth/{portal}/login/",
        {"email": email, "password": password},
        format="json",
    )


def sign_in(client, email, portal):
    response = login(client, email, portal)
    client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
    return response


class AuthTests(TestCase):
    def setUp(self):
        call_command("seed_roles", verbosity=0)
        self.client = APIClient()
        self.school = School.objects.create(name="Test School", type="school", code="T1")

    def test_platform_login_works(self):
        make_user("md@test.com", "committee_member")
        response = login(self.client, "md@test.com", "platform")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["portal"], "platform")

    def test_wrong_password_is_refused(self):
        make_user("md@test.com", "committee_member")
        response = login(self.client, "md@test.com", "platform", password="wrong")
        self.assertEqual(response.status_code, 401)

    def test_platform_user_cannot_use_school_login(self):
        make_user("md@test.com", "committee_member")
        response = login(self.client, "md@test.com", "school")
        self.assertEqual(response.status_code, 403)

    def test_school_user_cannot_use_platform_login(self):
        make_user("t@test.com", "teacher", school=self.school, scope="school")
        response = login(self.client, "t@test.com", "platform")
        self.assertEqual(response.status_code, 403)

    def test_school_token_cannot_open_platform_page(self):
        make_user("t@test.com", "teacher", school=self.school, scope="school")
        sign_in(self.client, "t@test.com", "school")
        self.assertEqual(self.client.get("/api/auth/school/ping/").status_code, 200)
        self.assertEqual(self.client.get("/api/auth/platform/ping/").status_code, 403)

    def test_no_token_is_refused(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)

    def test_temporary_password_blocks_pages_until_changed(self):
        make_user("md@test.com", "committee_member", must_change=True)
        sign_in(self.client, "md@test.com", "platform")

        self.assertEqual(self.client.get("/api/auth/finance-check/").status_code, 403)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)

        response = self.client.post(
            "/api/auth/change-password/",
            {"old_password": PASSWORD, "new_password": "New#Strong456pass"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/auth/finance-check/").status_code, 200)

    def test_weak_new_password_is_refused(self):
        make_user("md@test.com", "committee_member", must_change=True)
        sign_in(self.client, "md@test.com", "platform")
        response = self.client.post(
            "/api/auth/change-password/",
            {"old_password": PASSWORD, "new_password": "12345678"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_permission_check_follows_role(self):
        make_user("md@test.com", "committee_member")
        sign_in(self.client, "md@test.com", "platform")
        self.assertEqual(self.client.get("/api/auth/finance-check/").status_code, 200)
        self.assertEqual(self.client.get("/api/auth/marks-check/").status_code, 403)

    def test_user_can_update_own_profile(self):
        make_user("md@test.com", "committee_member")
        sign_in(self.client, "md@test.com", "platform")
        response = self.client.patch(
            "/api/auth/me/", {"full_name": "New Name"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "New Name")