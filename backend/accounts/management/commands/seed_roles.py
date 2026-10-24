from django.core.management.base import BaseCommand

from accounts.models import Permission, Role

CRUD = ("create", "update", "delete", "view")


def p(entity, *actions):
    return [f"{entity}.{a}" for a in actions]


# (scope, code): name
ROLES = {
    ("platform", "owner"): "Owner / CEO",
    ("platform", "md"): "Platform MD",
    ("platform", "committee_member"): "Platform Committee Member",
    ("platform", "onboarding_admin"): "Onboarding Admin",
    ("platform", "system_admin"): "System Admin",
    ("platform", "operations_admin"): "Operations Admin",
    ("platform", "approvals_admin"): "Approvals Admin",
    ("platform", "associate_manager_hr"): "Associate Manager HR",
    ("platform", "marketing_hr"): "Marketing HR",
    ("platform", "support_associate"): "Support Associate",
    ("platform", "reports_associate"): "Reports Associate",
    ("school", "md"): "School/College MD",
    ("school", "chairman"): "Chairman",
    ("school", "committee_member"): "School/College Committee Member",
    ("school", "principal"): "Principal",
    ("school", "coordinator"): "Coordinator",
    ("school", "staff_info_admin"): "Staff & Info Admin",
    ("school", "technical_admin"): "Technical Admin",
    ("school", "student_admin"): "Student Admin",
    ("school", "parent_admin"): "Parent Admin",
    ("school", "teacher"): "Teacher",
    ("school", "student"): "Student",
    ("school", "parent"): "Parent",
}

# What each role can do. "view" on student data means own data only (checked in code later).
ACCESS = {
    ("platform", "owner"): p("committee_member", "view") + p("platform_admin", *CRUD)
    + p("school", "view") + p("finance", "view") + p("report", "view"),
    ("platform", "md"): p("committee_member", *CRUD) + p("owner_account", *CRUD),
    ("platform", "committee_member"): p("committee_member", "view")
    + p("finance", "view") + p("report", "view"),
    ("platform", "onboarding_admin"): p("platform_hr", *CRUD),
    ("platform", "system_admin"): p("system_health", "update", "view"),
    ("platform", "operations_admin"): p("school", "create", "update", "view"),
    ("platform", "approvals_admin"): p("approval_request", "update", "view")
    + p("platform_hr", "view") + p("platform_associate", "view"),
    ("platform", "associate_manager_hr"): p("platform_associate", *CRUD),
    ("platform", "marketing_hr"): p("marketing_promotion", "view"),
    ("platform", "support_associate"): p("support_ticket", "update", "view"),
    ("platform", "reports_associate"): p("report", "create", "view"),
    ("school", "md"): p("school_leadership", *CRUD),
    ("school", "chairman"): p("school_leadership", "view") + p("principal", *CRUD)
    + p("coordinator", "view") + p("approval_request", "update", "view"),
    ("school", "committee_member"): p("school_leadership", "view"),
    ("school", "principal"): p("coordinator", *CRUD) + p("event_request", "update", "view"),
    ("school", "coordinator"): p("school_admin", *CRUD) + p("event_request", "create", "view"),
    ("school", "staff_info_admin"): p("teacher", *CRUD) + p("announcement", *CRUD)
    + p("meeting_request", "update", "view"),
    ("school", "technical_admin"): p("academic_structure", *CRUD)
    + p("school_setup", "create", "update", "view"),
    ("school", "student_admin"): p("student_account", *CRUD),
    ("school", "parent_admin"): p("parent_account", *CRUD),
    ("school", "teacher"): p("student_marks", *CRUD) + p("progress", "view")
    + p("academic_structure", "view") + p("announcement", "view")
    + p("helpdesk", "create", "view"),
    ("school", "student"): p("student_marks", "view") + p("progress", "view")
    + p("announcement", "view") + p("helpdesk", "create", "view"),
    ("school", "parent"): p("student_marks", "view") + p("progress", "view")
    + p("announcement", "view") + p("helpdesk", "create", "view")
    + p("meeting_request", "create", "view"),
}

# Every role can see and update their own profile.
EVERYONE = p("profile", "update", "view")

# Roles that can use the AI chatbot.
CHATBOT_ROLES = {key for key in ROLES if key[0] == "platform"} | {
    ("school", code)
    for code in ["chairman", "committee_member", "principal", "teacher", "student", "parent"]
}


class Command(BaseCommand):
    help = "Add the starting roles and permissions"

    def handle(self, *args, **options):
        for (scope, code), name in ROLES.items():
            codes = set(ACCESS.get((scope, code), []) + EVERYONE)
            if (scope, code) in CHATBOT_ROLES:
                codes.add("chatbot.use")

            role, _ = Role.objects.update_or_create(
                scope=scope, code=code, defaults={"name": name}
            )
            permissions = [Permission.objects.get_or_create(code=c)[0] for c in sorted(codes)]
            role.permissions.set(permissions)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Roles: {Role.objects.count()}, Permissions: {Permission.objects.count()}"
            )
        )