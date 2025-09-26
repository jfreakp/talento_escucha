from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('usuarios/', views.administracion_usuarios, name='administracion_usuarios'),
    path('usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/resetear-password/', views.resetear_password, name='resetear_password'),
    path('usuarios/resetear-password/<int:user_id>/', views.resetear_password_usuario, name='resetear_password_usuario'),
    # URLs para tickets
    path('buscar-ticket/', views.buscar_ticket, name='buscar_ticket'),
    path('ticket/<str:codigo>/', views.view_ticket, name='view_ticket'),
    path('tickets/pendientes/', views.tickets_pendientes, name='tickets_pendientes'),
    path('tickets/asignados/', views.tickets_asignados, name='tickets_asignados'),
    path('tickets/asignar-a-mi/<int:ticket_id>/', views.asignar_ticket_a_mi, name='asignar_ticket_a_mi'),
    path('tickets/formulario-solucion/<int:ticket_id>/', views.formulario_solucion, name='formulario_solucion'),
    path('tickets/resolver/<int:ticket_id>/', views.resolver_ticket, name='resolver_ticket'),
    # URLs para reportería
    path('reportes/tickets/', views.reporte_tickets, name='reporte_tickets'),
]