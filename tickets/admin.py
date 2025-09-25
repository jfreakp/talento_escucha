from django.contrib import admin
from .models import Agencia, Ticket, TicketAuditoria


@admin.register(Agencia)
class AgenciaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Agencia
    """
    list_display = [
        'codigo_faces',
        'nombre',
        'usuario_creacion',
        'fecha_creacion',
        'fecha_actualizacion'
    ]
    
    list_filter = [
        'fecha_creacion',
        'fecha_actualizacion',
        'usuario_creacion'
    ]
    
    search_fields = [
        'codigo_faces',
        'nombre'
    ]
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('codigo_faces', 'nombre')
        }),
        ('Auditoría', {
            'fields': ('usuario_creacion', 'usuario_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def save_model(self, request, obj, form, change):
        """Override para manejar auditoría automática"""
        if not obj.pk:  # Nuevo objeto
            obj.usuario_creacion = request.user
        obj.usuario_actualizacion = request.user
        super().save_model(request, obj, form, change)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Ticket
    """
    list_display = [
        'id',
        'nombre_completo', 
        'correo',
        'agencia',
        'tipo_solicitud',
        'severidad',
        'estado',
        'usuario_asignado',
        'fecha_creacion',
        'fecha_actualizacion'
    ]
    
    list_filter = [
        'estado',
        'tipo_solicitud',
        'severidad',
        'fecha_creacion',
        'fecha_actualizacion',
        'usuario_asignado'
    ]
    
    search_fields = [
        'nombre',
        'apellido', 
        'correo',
        'agencia',
        'descripcion'
    ]
    
    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información del Solicitante', {
            'fields': ('nombre', 'apellido', 'correo', 'telefono', 'agencia')
        }),
        ('Detalles de la Solicitud', {
            'fields': ('tipo_solicitud', 'severidad', 'descripcion', 'estado')
        }),
        ('Asignación y Solución', {
            'fields': ('usuario_asignado', 'solucion')
        }),
        ('Auditoría', {
            'fields': ('usuario_crea', 'usuario_actualiza', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    def nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"
    nombre_completo.short_description = "Nombre Completo"
    
    def save_model(self, request, obj, form, change):
        """Asignar usuario que crea/actualiza automáticamente"""
        if not change:  # Si es una creación nueva
            obj.usuario_crea = request.user
        obj.usuario_actualiza = request.user
        super().save_model(request, obj, form, change)


@admin.register(TicketAuditoria)
class TicketAuditoriaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo TicketAuditoria
    """
    list_display = [
        'id',
        'ticket',
        'operacion',
        'usuario',
        'fecha_cambio',
        'ip_usuario'
    ]
    
    list_filter = [
        'operacion',
        'fecha_cambio',
        'usuario'
    ]
    
    search_fields = [
        'ticket__nombre',
        'ticket__apellido',
        'ticket__correo',
        'comentario'
    ]
    
    readonly_fields = [
        'ticket',
        'operacion',
        'datos_anteriores',
        'datos_nuevos',
        'campos_modificados',
        'usuario',
        'fecha_cambio',
        'ip_usuario',
        'comentario'
    ]
    
    # Solo lectura - no permitir editar auditorías
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
