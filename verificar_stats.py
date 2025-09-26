import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talento_escucha.settings')
django.setup()

from tickets.models import Ticket
from django.contrib.auth.models import User

# Consultar datos para usuario revisor específico
user = User.objects.filter(username='revisor').first()
if user:
    print(f'=== ESTADÍSTICAS PARA {user.username} ===')
    tickets_asignados = Ticket.objects.filter(usuario_asignado=user)
    
    stats = {
        'total': tickets_asignados.count(),
        'pendiente': tickets_asignados.filter(estado='pendiente').count(),
        'en_proceso': tickets_asignados.filter(estado='en_proceso').count(),
        'resuelto': tickets_asignados.filter(estado='resuelto').count(),
        'cerrado': tickets_asignados.filter(estado='cerrado').count(),
        'cancelado': tickets_asignados.filter(estado='cancelado').count(),
    }
    
    print(f'Total asignados: {stats["total"]}')
    print(f'Pendientes: {stats["pendiente"]}')
    print(f'En proceso: {stats["en_proceso"]}')
    print(f'Resueltos: {stats["resuelto"]}')
    print(f'Cerrados: {stats["cerrado"]}')
    print(f'Cancelados: {stats["cancelado"]}')
    
    print('\n=== TICKETS SIN ASIGNAR ===')
    sin_asignar = Ticket.objects.filter(usuario_asignado=None)
    stats_sin_asignar = {
        'total': sin_asignar.count(),
        'pendiente': sin_asignar.filter(estado='pendiente').count(),
        'en_proceso': sin_asignar.filter(estado='en_proceso').count(),
        'resuelto': sin_asignar.filter(estado='resuelto').count(),
        'cerrado': sin_asignar.filter(estado='cerrado').count(),
        'cancelado': sin_asignar.filter(estado='cancelado').count(),
    }
    
    print(f'Total sin asignar: {stats_sin_asignar["total"]}')
    print(f'Pendientes: {stats_sin_asignar["pendiente"]}')
    print(f'En proceso: {stats_sin_asignar["en_proceso"]}')
    print(f'Resueltos: {stats_sin_asignar["resuelto"]}')
    print(f'Cerrados: {stats_sin_asignar["cerrado"]}')
    print(f'Cancelados: {stats_sin_asignar["cancelado"]}')
else:
    print('Usuario revisor no encontrado')