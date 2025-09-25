from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from functools import wraps


def user_has_role(role_name):
    """
    Decorador para verificar si un usuario tiene un rol específico
    """
    def check_role(user):
        if user.is_authenticated:
            return user.groups.filter(name=role_name).exists() or user.is_superuser
        return False
    
    return user_passes_test(check_role)


def user_has_any_role(roles):
    """
    Decorador para verificar si un usuario tiene cualquiera de los roles especificados
    """
    def check_roles(user):
        if user.is_authenticated:
            if user.is_superuser:
                return True
            return user.groups.filter(name__in=roles).exists()
        return False
    
    return user_passes_test(check_roles)


def require_role(role_name):
    """
    Decorador que requiere un rol específico para acceder a una vista
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not request.user.groups.filter(name=role_name).exists():
                raise PermissionDenied(f"Se requiere el rol '{role_name}' para acceder a esta página")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_user_role(user):
    """
    Obtiene el rol principal del usuario
    """
    if user.is_superuser:
        return 'SUPERUSER'
    
    role = user.groups.first()
    return role.name if role else None


def user_can_manage_users(user):
    """
    Verifica si el usuario puede gestionar otros usuarios
    """
    if user.is_superuser:
        return True
    return user.groups.filter(name='ADMIN').exists()


def user_can_manage_tickets(user):
    """
    Verifica si el usuario puede gestionar tickets
    """
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=['ADMIN', 'REVISOR']).exists()


def user_can_view_tickets(user):
    """
    Verifica si el usuario puede ver tickets
    """
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=['ADMIN', 'REVISOR', 'USER']).exists()