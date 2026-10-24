import secrets

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import CredentialDelivery, Role, User, UserRole


class Command(BaseCommand):
    help = "Create the first Platform MD and committee members"

    def add_arguments(self, parser):
        parser.add_argument("--md-name", required=True)
        parser.add_argument("--md-email", required=True)
        parser.add_argument(
            "--member",
            action="append",
            default=[],
            help='Another committee member, written as "Name,email"',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        committee_role = Role.objects.filter(scope="platform", code="committee_member").first()
        md_role = Role.objects.filter(scope="platform", code="md").first()
        if not committee_role or not md_role:
            raise CommandError("Roles are missing. Run: python manage.py seed_roles")

        people = [(options["md_name"], options["md_email"], True)]
        for item in options["member"]:
            parts = [x.strip() for x in item.split(",", 1)]
            if len(parts) != 2:
                raise CommandError(f'Wrong format: "{item}". Use "Name,email".')
            people.append((parts[0], parts[1], False))

        for name, email, is_md in people:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                self.stdout.write(f"Skipped (already exists): {email}")
                continue

            temp_password = secrets.token_urlsafe(9)
            user = User.objects.create_user(
                email=email,
                password=temp_password,
                full_name=name,
                status="active",
                must_change_password=True,
            )
            UserRole.objects.create(user=user, role=committee_role)
            if is_md:
                UserRole.objects.create(user=user, role=md_role)
            CredentialDelivery.objects.create(user=user, method="paper", status="printed")

            label = "MD" if is_md else "Member"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {label}: {email}   temporary password: {temp_password}"
                )
            )

        self.stdout.write("Save the temporary passwords now. They are shown only once.")