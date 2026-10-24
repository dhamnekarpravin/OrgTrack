from django.core.mail import send_mail

from .models import AuditLog, Permission


def permission_codes(user):
    """All permission codes this user has, from all their roles."""
    return set(
        Permission.objects.filter(roles__role_users__user=user)
        .values_list("code", flat=True)
        .distinct()
    )


def role_codes(user):
    """The role codes this user has."""
    return list(user.user_roles.order_by("role__code").values_list("role__code", flat=True))


def write_audit(actor, action, table_name, record_id, old=None, new=None, school=None):
    """Save who did what, and when."""
    AuditLog.objects.create(
        user=actor,
        school=school,
        action=action,
        table_name=table_name,
        record_id=str(record_id),
        old_values=old,
        new_values=new,
    )


def send_credentials_email(user, temp_password):
    send_mail(
        subject="Your OrgTracker account",
        message=(
            f"Hello {user.full_name},\n\n"
            "Your OrgTracker account is ready.\n"
            f"Email: {user.email}\n"
            f"Temporary password: {temp_password}\n\n"
            "You must change this password when you sign in.\n"
        ),
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )