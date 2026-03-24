from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


ROLE_PERMISSION_CODENAMES = {
    'ADMIN': [
        'view_ticket',
        'add_ticket',
        'change_ticket',
        'delete_ticket',
        'view_user',
        'add_user',
        'change_user',
        'delete_user',
    ],
    'REVISOR': [
        'view_ticket',
        'add_ticket',
        'change_ticket',
        'delete_ticket',
    ],
    'USER': [
        'view_ticket',
    ],
}


@receiver(post_migrate)
def ensure_default_roles(sender, **kwargs):
    required_codenames = {
        codename
        for codenames in ROLE_PERMISSION_CODENAMES.values()
        for codename in codenames
    }

    permissions = Permission.objects.filter(codename__in=required_codenames)
    permissions_by_codename = {permission.codename: permission for permission in permissions}

    # During early migration steps some permissions may not exist yet.
    # The signal runs multiple times, so we skip until all required ones are present.
    if len(permissions_by_codename) < len(required_codenames):
        return

    for role_name, permission_codenames in ROLE_PERMISSION_CODENAMES.items():
        group, _ = Group.objects.get_or_create(name=role_name)
        group.permissions.set([permissions_by_codename[codename] for codename in permission_codenames])
