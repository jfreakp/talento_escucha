from django import template
from admin_dashboard.decorators import user_can_manage_users, user_can_manage_tickets, get_user_role

register = template.Library()


@register.filter
def can_manage_users(user):
    """Verifica si el usuario puede gestionar otros usuarios"""
    return user_can_manage_users(user)


@register.filter
def can_manage_tickets(user):
    """Verifica si el usuario puede gestionar tickets"""
    return user_can_manage_tickets(user)


@register.filter
def user_role(user):
    """Obtiene el rol del usuario"""
    return get_user_role(user)


@register.filter
def has_role(user, role_name):
    """Verifica si el usuario tiene un rol específico"""
    if user.is_superuser:
        return True
    return user.groups.filter(name=role_name).exists()