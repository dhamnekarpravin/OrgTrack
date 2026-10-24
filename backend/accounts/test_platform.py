from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from .models import ApprovalRequest, AuditLog, CredentialDelivery, Role, School, User, UserRole
from .tests import PASSWORD, login, make_user, sign_in


def platform_user(email, *role_codes):
    user = User.objects.create_user(
        email=email, password=PASSWORD, full_name="Test User", must_change_password=False
    )
    for code in role_codes:
        UserRole.objects.create(user=user, role=Role.objects.get(scope="platform", code=code))
    return user


class PlatformAccountTests(TestCase):
    def setUp(self):
        call_command("seed_roles", verbosity=0)
        self.client = APIClient()

    def as_user(self, email, *role_codes):
        platform_user(email, *role_codes)
        sign_in(self.client, email, "platform")

    def new_account(self, address, email, **extra):
        body = {"full_name": "New Person", "email": email}
        body.update(extra)
        return self.client.post(address, body, format="json")

    def test_md_can_add_committee_member(self):
        self.as_user("md@t.com", "md", "committee_member")
        r = self.new_account("/api/platform/committee/", "m1@t.com")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["roles"], ["committee_member"])
        self.assertEqual(r.data["status"], "active")
        self.assertTrue(r.data["temporary_password"])

    def test_committee_member_cannot_add_committee_member(self):
        self.as_user("c@t.com", "committee_member")
        r = self.new_account("/api/platform/committee/", "m1@t.com")
        self.assertEqual(r.status_code, 403)

    def test_owner_adds_admin_with_allowed_role_only(self):
        self.as_user("o@t.com", "owner")
        ok = self.new_account("/api/platform/admins/", "a1@t.com", roles=["onboarding_admin"])
        self.assertEqual(ok.status_code, 201)
        bad = self.new_account("/api/platform/admins/", "a2@t.com", roles=["owner"])
        self.assertEqual(bad.status_code, 400)
        missing = self.new_account("/api/platform/admins/", "a3@t.com")
        self.assertEqual(missing.status_code, 400)

    def test_only_onboarding_admin_can_add_hr(self):
        self.as_user("s@t.com", "system_admin")
        refused = self.new_account("/api/platform/hrs/", "h@t.com", roles=["marketing_hr"])
        self.assertEqual(refused.status_code, 403)

        self.as_user("ob@t.com", "onboarding_admin")
        r = self.new_account("/api/platform/hrs/", "h@t.com", roles=["marketing_hr"])
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["status"], "pending_approval")

    def test_pending_hr_cannot_log_in_until_approved(self):
        self.as_user("ob@t.com", "onboarding_admin")
        r = self.new_account("/api/platform/hrs/", "h@t.com", roles=["associate_manager_hr"])
        temp = r.data["temporary_password"]
        anon = APIClient()
        self.assertEqual(login(anon, "h@t.com", "platform", password=temp).status_code, 401)

        self.as_user("ap@t.com", "approvals_admin")
        pending = self.client.get("/api/platform/approvals/")
        self.assertEqual(len(pending.data), 1)
        decide = self.client.post(
            f"/api/platform/approvals/{pending.data[0]['id']}/decide/",
            {"decision": "accept"},
            format="json",
        )
        self.assertEqual(decide.status_code, 200)

        ok = login(anon, "h@t.com", "platform", password=temp)
        self.assertEqual(ok.status_code, 200)
        self.assertTrue(ok.data["user"]["must_change_password"])

    def test_rejected_associate_cannot_log_in(self):
        self.as_user("am@t.com", "associate_manager_hr")
        r = self.new_account("/api/platform/associates/", "x@t.com", roles=["support_associate"])
        temp = r.data["temporary_password"]

        self.as_user("ap@t.com", "approvals_admin")
        pending = self.client.get("/api/platform/approvals/")
        self.client.post(
            f"/api/platform/approvals/{pending.data[0]['id']}/decide/",
            {"decision": "reject", "note": "Not needed"},
            format="json",
        )
        self.assertEqual(
            login(APIClient(), "x@t.com", "platform", password=temp).status_code, 401
        )

    def test_only_approvals_admin_can_decide(self):
        self.as_user("ob@t.com", "onboarding_admin")
        self.new_account("/api/platform/hrs/", "h@t.com", roles=["marketing_hr"])
        approval_id = ApprovalRequest.objects.get().id
        r = self.client.post(
            f"/api/platform/approvals/{approval_id}/decide/",
            {"decision": "accept"},
            format="json",
        )
        self.assertEqual(r.status_code, 403)

    def test_request_cannot_be_decided_twice(self):
        self.as_user("ob@t.com", "onboarding_admin")
        self.new_account("/api/platform/hrs/", "h@t.com", roles=["marketing_hr"])
        approval_id = ApprovalRequest.objects.get().id

        self.as_user("ap@t.com", "approvals_admin")
        address = f"/api/platform/approvals/{approval_id}/decide/"
        first = self.client.post(address, {"decision": "accept"}, format="json")
        second = self.client.post(address, {"decision": "reject"}, format="json")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 400)

    def test_new_owner_replaces_old_owner(self):
        self.as_user("md@t.com", "md", "committee_member")
        self.new_account("/api/platform/owner/", "o1@t.com")
        self.new_account("/api/platform/owner/", "o2@t.com")
        listing = self.client.get("/api/platform/owner/")
        self.assertEqual([u["email"] for u in listing.data], ["o2@t.com"])
        self.assertIsNotNone(User.objects.get(email="o1@t.com").deleted_at)

    def test_delete_hides_the_account(self):
        self.as_user("o@t.com", "owner")
        r = self.new_account("/api/platform/admins/", "a@t.com", roles=["system_admin"])
        deleted = self.client.delete(f"/api/platform/admins/{r.data['id']}/")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(self.client.get("/api/platform/admins/").data, [])
        self.assertIsNotNone(User.objects.get(email="a@t.com").deleted_at)

    def test_md_cannot_be_deleted(self):
        self.as_user("md@t.com", "md", "committee_member")
        md = User.objects.get(email="md@t.com")
        r = self.client.delete(f"/api/platform/committee/{md.id}/")
        self.assertEqual(r.status_code, 400)

    def test_update_changes_name_and_roles(self):
        self.as_user("o@t.com", "owner")
        r = self.new_account("/api/platform/admins/", "a@t.com", roles=["system_admin"])
        updated = self.client.patch(
            f"/api/platform/admins/{r.data['id']}/",
            {"full_name": "Renamed", "roles": ["approvals_admin"]},
            format="json",
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["full_name"], "Renamed")
        self.assertEqual(updated.data["roles"], ["approvals_admin"])

    def test_duplicate_email_is_refused(self):
        self.as_user("o@t.com", "owner")
        self.new_account("/api/platform/admins/", "a@t.com", roles=["system_admin"])
        again = self.new_account("/api/platform/admins/", "a@t.com", roles=["system_admin"])
        self.assertEqual(again.status_code, 400)

    def test_credentials_and_audit_are_saved(self):
        self.as_user("o@t.com", "owner")
        self.new_account(
            "/api/platform/admins/", "a@t.com", roles=["system_admin"], send_email=True
        )
        self.assertEqual(len(mail.outbox), 1)
        methods = set(
            CredentialDelivery.objects.filter(user__email="a@t.com").values_list(
                "method", flat=True
            )
        )
        self.assertEqual(methods, {"paper", "email"})
        self.assertTrue(AuditLog.objects.filter(table_name="users", action="create").exists())

    def test_school_user_cannot_use_platform_accounts(self):
        school = School.objects.create(name="S", type="school", code="S1")
        make_user("t@t.com", "teacher", school=school, scope="school")
        sign_in(self.client, "t@t.com", "school")
        self.assertEqual(self.client.get("/api/platform/admins/").status_code, 403)