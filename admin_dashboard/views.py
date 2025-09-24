from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from tickets.models import Ticket, Agencia


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
