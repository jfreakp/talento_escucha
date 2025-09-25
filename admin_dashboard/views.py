from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from tickets.models import Ticket, Agencia, TicketAuditoria
from .decorators import require_role, user_can_manage_users


@login_required
def dashboard_view(request):
    """Vista principal del dashboard"""
    # Obtener estadísticas básicas
    total_tickets = Ticket.objects.count()
    total_usuarios = User.objects.count()
    total_agencias = Agencia.objects.count()
    
    # Estadísticas por tipo de petición
    peticiones = Ticket.objects.filter(tipo_solicitud='P').count()
    quejas = Ticket.objects.filter(tipo_solicitud='Q').count()
    reclamos = Ticket.objects.filter(tipo_solicitud='R').count()
    solicitudes = Ticket.objects.filter(tipo_solicitud='S').count()
    
    # Estadísticas por severidad
    severidad_alta = Ticket.objects.filter(severidad='A').count()
    severidad_media = Ticket.objects.filter(severidad='M').count()
    severidad_baja = Ticket.objects.filter(severidad='B').count()
    
    # Últimos tickets creados
    ultimos_tickets = Ticket.objects.order_by('-fecha_creacion')[:5]
    
    context = {
        'total_tickets': total_tickets,
        'total_usuarios': total_usuarios,
        'total_agencias': total_agencias,
        'peticiones': peticiones,
        'quejas': quejas,
        'reclamos': reclamos,
        'solicitudes': solicitudes,
        'severidad_alta': severidad_alta,
        'severidad_media': severidad_media,
        'severidad_baja': severidad_baja,
        'ultimos_tickets': ultimos_tickets,
        'user': request.user,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)


@login_required
def administracion_usuarios(request):
    """Vista para administrar usuarios"""
    # Verificar permisos
    if not user_can_manage_users(request.user):
        raise PermissionDenied("No tienes permisos para gestionar usuarios")
    
    # Obtener todos los usuarios
    usuarios = User.objects.all().order_by('-date_joined')
    
    context = {
        'usuarios': usuarios,
        'total_usuarios': usuarios.count(),
    }
    
    return render(request, 'admin_dashboard/administracion_usuarios.html', context)


@login_required
def agregar_usuario(request):
    """Vista para agregar nuevos usuarios"""
    # Verificar permisos
    if not user_can_manage_users(request.user):
        raise PermissionDenied("No tienes permisos para agregar usuarios")
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Agregar información adicional si se proporciona
            if request.POST.get('first_name'):
                user.first_name = request.POST.get('first_name')
            if request.POST.get('last_name'):
                user.last_name = request.POST.get('last_name')
            if request.POST.get('email'):
                user.email = request.POST.get('email')
            user.save()
            
            # Asignar rol seleccionado
            role_name = request.POST.get('role')
            if role_name:
                try:
                    role_group = Group.objects.get(name=role_name)
                    user.groups.add(role_group)
                    messages.success(request, f'Usuario {user.username} creado exitosamente con rol {role_name}.')
                except Group.DoesNotExist:
                    messages.warning(request, f'Usuario {user.username} creado, pero el rol {role_name} no existe.')
            else:
                messages.success(request, f'Usuario {user.username} creado exitosamente.')
            
            return redirect('admin_dashboard:administracion_usuarios')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UserCreationForm()
    
    # Obtener todos los roles disponibles
    roles = Group.objects.all()
    
    context = {
        'form': form,
        'roles': roles,
    }
    
    return render(request, 'admin_dashboard/agregar_usuario.html', context)


@login_required
def eliminar_usuario(request, user_id):
    """Vista para eliminar usuarios"""
    # Verificar permisos
    if not user_can_manage_users(request.user):
        raise PermissionDenied("No tienes permisos para eliminar usuarios")
    
    usuario = get_object_or_404(User, id=user_id)
    
    # Verificar que no se está tratando de eliminar a sí mismo
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('admin_dashboard:administracion_usuarios')
    
    # Verificar que no es el superusuario
    if usuario.is_superuser:
        messages.error(request, 'No se puede eliminar una cuenta de superusuario.')
        return redirect('admin_dashboard:administracion_usuarios')
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{username}" eliminado exitosamente.')
        return redirect('admin_dashboard:administracion_usuarios')
    
    # Si es GET, mostrar confirmación
    context = {
        'usuario': usuario,
    }
    
    return render(request, 'admin_dashboard/confirmar_eliminacion.html', context)


@login_required
def editar_usuario(request, user_id):
    """Vista para editar usuarios existentes"""
    # Verificar permisos
    if not user_can_manage_users(request.user):
        raise PermissionDenied("No tienes permisos para editar usuarios")
    
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Actualizar información del usuario
        usuario.first_name = request.POST.get('first_name', '')
        usuario.last_name = request.POST.get('last_name', '')
        usuario.email = request.POST.get('email', '')
        
        # Cambiar estado activo/inactivo
        usuario.is_active = 'is_active' in request.POST
        
        # Actualizar rol
        role_name = request.POST.get('role')
        if role_name:
            # Remover todos los roles actuales
            usuario.groups.clear()
            # Asignar nuevo rol
            try:
                role_group = Group.objects.get(name=role_name)
                usuario.groups.add(role_group)
            except Group.DoesNotExist:
                messages.warning(request, f'El rol {role_name} no existe.')
        
        usuario.save()
        messages.success(request, f'Usuario {usuario.username} actualizado exitosamente.')
        return redirect('admin_dashboard:administracion_usuarios')
    
    # Obtener todos los roles disponibles
    roles = Group.objects.all()
    # Obtener rol actual del usuario
    current_role = usuario.groups.first()
    
    context = {
        'usuario': usuario,
        'roles': roles,
        'current_role': current_role,
    }
    
    return render(request, 'admin_dashboard/editar_usuario.html', context)


@login_required
@require_role('ADMIN')
def resetear_password(request):
    """Vista para mostrar la lista de usuarios para resetear password"""
    usuarios = User.objects.all().exclude(id=request.user.id)  # Excluir al usuario actual
    
    context = {
        'usuarios': usuarios,
    }
    
    return render(request, 'admin_dashboard/resetear_password.html', context)


@login_required
@require_role('ADMIN')
def resetear_password_usuario(request, user_id):
    """Vista para resetear la password de un usuario específico"""
    usuario = get_object_or_404(User, id=user_id)
    
    # No permitir resetear la password del propio usuario
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes resetear tu propia contraseña.')
        return redirect('admin_dashboard:resetear_password')
    
    if request.method == 'POST':
        form = SetPasswordForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contraseña reseteada exitosamente para el usuario {usuario.username}.')
            return redirect('admin_dashboard:resetear_password')
        else:
            # Si hay errores en el formulario, se mostrarán en el template
            pass
    else:
        form = SetPasswordForm(usuario)
    
    context = {
        'usuario': usuario,
        'form': form,
    }
    
    return render(request, 'admin_dashboard/resetear_password_usuario.html', context)


@login_required
def buscar_ticket(request):
    """Vista para buscar tickets por código"""
    ticket = None
    codigo_buscado = None
    error_message = None
    
    if request.method == 'POST':
        codigo_buscado = request.POST.get('codigo', '').strip().upper()
        
        if codigo_buscado:
            try:
                # Buscar el ticket por código
                ticket = Ticket.objects.get(codigo=codigo_buscado)
                # Redirigir a la vista del ticket
                return redirect('admin_dashboard:view_ticket', codigo=codigo_buscado)
            except Ticket.DoesNotExist:
                error_message = f'No se encontró ningún ticket con el código "{codigo_buscado}"'
        else:
            error_message = 'Por favor ingresa un código de ticket'
    
    context = {
        'ticket': ticket,
        'codigo_buscado': codigo_buscado,
        'error_message': error_message,
    }
    
    return render(request, 'admin_dashboard/buscar_ticket.html', context)


@login_required
def view_ticket(request, codigo):
    """Vista para mostrar el detalle del ticket con tabs"""
    ticket = get_object_or_404(Ticket, codigo=codigo)
    
    # Obtener el historial de auditoría del ticket
    historial = ticket.auditorias.all().order_by('-fecha_cambio')
    
    context = {
        'ticket': ticket,
        'historial': historial,
    }
    
    return render(request, 'admin_dashboard/view_ticket.html', context)
