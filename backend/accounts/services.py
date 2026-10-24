from .models import Permission


def permission_codes(user):
    """All permission codes this user has, from all their roles."""
    return set(
        Permission.objects.filter(roles__role_users__user=user)
        .values_list("code", flat=True)
        .distinct()
    )


def role_codes(user):
    """The role codes this user has."""
    return list(user.user_roles.values_list("role__code", flat=True))