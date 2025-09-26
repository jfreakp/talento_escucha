from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Agencia(models.Model):
    """
    Modelo para gestionar agencias/empresas
    """
    
    codigo_faces = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código FACES",
        help_text="Código único de identificación FACES"
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre de la Agencia",
        help_text="Nombre completo de la empresa o agencia"
    )
    
    # Campos de auditoría
    usuario_creacion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='agencias_creadas',
        verbose_name="Usuario de Creación",
        help_text="Usuario que creó esta agencia"
    )
    
    usuario_actualizacion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='agencias_actualizadas',
        verbose_name="Usuario de Actualización",
        help_text="Usuario que actualizó por última vez esta agencia"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación",
        help_text="Fecha y hora de creación del registro"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización",
        help_text="Fecha y hora de la última actualización"
    )
    
    class Meta:
        verbose_name = "Agencia"
        verbose_name_plural = "Agencias"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo_faces']),
            models.Index(fields=['nombre']),
        ]
    
    def __str__(self):
        return f"{self.codigo_faces} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """Override save para manejar auditoría"""
        # La auditoría se maneja desde las vistas/formularios
        super().save(*args, **kwargs)


class Ticket(models.Model):
    """
    Modelo para gestionar tickets de solicitudes
    """
    
    # Opciones para tipo de solicitud
    TIPO_SOLICITUD_CHOICES = [
        ('P', 'Peticiones'),
        ('Q', 'Quejas'),
        ('R', 'Reclamos'),
        ('S', 'Solicitudes'),
    ]
    
    # Opciones para estado
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Opciones para severidad
    SEVERIDAD_CHOICES = [
        ('A', 'Alto'),
        ('M', 'Medio'),
        ('B', 'Bajo'),
    ]
    
    # Campos principales
    codigo = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        verbose_name="Código",
        help_text="Código único del ticket (FAC + ID)"
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        help_text="Nombre del solicitante"
    )
    
    apellido = models.CharField(
        max_length=100,
        verbose_name="Apellido",
        help_text="Apellido del solicitante"
    )
    
    correo = models.EmailField(
        verbose_name="Correo Electrónico",
        help_text="Email de contacto del solicitante"
    )
    
    agencia = models.ForeignKey(
        Agencia,
        on_delete=models.PROTECT,
        verbose_name="Agencia",
        help_text="Agencia o empresa asociada al ticket"
    )
    
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono",
        help_text="Número de teléfono de contacto"
    )
    
    tipo_solicitud = models.CharField(
        max_length=50,
        choices=TIPO_SOLICITUD_CHOICES,
        verbose_name="Tipo de Solicitud",
        help_text="Categoría de la solicitud"
    )
    
    severidad = models.CharField(
        max_length=1,
        choices=SEVERIDAD_CHOICES,
        default='M',
        verbose_name="Severidad",
        help_text="Nivel de severidad del ticket"
    )
    
    # Usuario asignado (referencia a User de Django, puede ser nulo)
    usuario_asignado = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_asignados',
        verbose_name="Usuario Asignado",
        help_text="Usuario responsable de atender el ticket"
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación",
        help_text="Fecha y hora de creación del ticket"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización",
        help_text="Fecha y hora de la última actualización"
    )
    
    usuario_crea = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='tickets_creados',
        verbose_name="Usuario que Crea",
        help_text="Usuario que creó el ticket",
        null=True,
        blank=True
    )
    
    usuario_actualiza = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='tickets_actualizados',
        verbose_name="Usuario que Actualiza",
        help_text="Usuario que realizó la última actualización",
        null=True,
        blank=True
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado",
        help_text="Estado actual del ticket"
    )
    
    # Campos adicionales útiles
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción detallada de la solicitud"
    )
    
    solucion = models.TextField(
        verbose_name="Solución",
        help_text="Descripción de la solución implementada",
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-fecha_creacion']
        db_table = 'tickets_ticket'
    
    def __str__(self):
        codigo_display = self.codigo or f"#{self.id}"
        return f"Ticket {codigo_display} - {self.nombre} {self.apellido} ({self.get_estado_display()})"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del solicitante"""
        return f"{self.nombre} {self.apellido}"
    
    def save(self, *args, **kwargs):
        """Override del método save para generar código y auditoría"""
        is_new = not self.pk
        
        if is_new:  # Si es una creación nueva
            if not self.fecha_creacion:
                self.fecha_creacion = timezone.now()
        
        self.fecha_actualizacion = timezone.now()
        super().save(*args, **kwargs)
        
        # Generar código después de guardar (cuando ya tenemos el ID)
        if is_new and not self.codigo:
            self.codigo = f"FAC{self.id}"
            # Guardar nuevamente solo el campo código para evitar recursión infinita
            super().save(update_fields=['codigo'])


class TicketAuditoria(models.Model):
    """
    Tabla de auditoría para el modelo Ticket
    Registra todos los cambios realizados en los tickets
    """
    
    # Tipos de operación
    OPERACION_CHOICES = [
        ('CREATE', 'Creación'),
        ('ASSIGN', 'Asignación'),
        ('RESOLVE', 'Resolución'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
    ]
    
    # Referencia al ticket original
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='auditorias',
        verbose_name="Ticket",
        help_text="Ticket al que pertenece esta auditoría"
    )
    
    # Tipo de operación realizada
    operacion = models.CharField(
        max_length=20,
        choices=OPERACION_CHOICES,
        verbose_name="Operación",
        help_text="Tipo de operación realizada"
    )
    
    # Datos antes del cambio (JSON)
    datos_anteriores = models.JSONField(
        verbose_name="Datos Anteriores",
        help_text="Estado del ticket antes del cambio",
        null=True,
        blank=True
    )
    
    # Datos después del cambio (JSON)
    datos_nuevos = models.JSONField(
        verbose_name="Datos Nuevos",
        help_text="Estado del ticket después del cambio",
        null=True,
        blank=True
    )
    
    # Campos específicos que cambiaron
    campos_modificados = models.JSONField(
        verbose_name="Campos Modificados",
        help_text="Lista de campos que fueron modificados",
        null=True,
        blank=True
    )
    
    # Usuario que realizó el cambio
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Usuario",
        help_text="Usuario que realizó la operación",
        null=True,
        blank=True
    )
    
    # Fecha y hora del cambio
    fecha_cambio = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del Cambio",
        help_text="Fecha y hora cuando se realizó la operación"
    )
    
    # IP del usuario (opcional)
    ip_usuario = models.GenericIPAddressField(
        verbose_name="IP del Usuario",
        help_text="Dirección IP desde donde se realizó el cambio",
        null=True,
        blank=True
    )
    
    # Comentario adicional
    comentario = models.TextField(
        verbose_name="Comentario",
        help_text="Comentario adicional sobre el cambio realizado",
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = "Auditoría de Ticket"
        verbose_name_plural = "Auditorías de Tickets"
        ordering = ['-fecha_cambio']
        db_table = 'tickets_ticket_auditoria'
    
    def __str__(self):
        return f"Auditoría #{self.id} - Ticket #{self.ticket.id} - {self.get_operacion_display()}"
    
    @classmethod
    def crear_auditoria(cls, ticket, operacion, datos_anteriores=None, datos_nuevos=None, 
                       campos_modificados=None, usuario=None, ip_usuario=None, comentario=None):
        """
        Método de clase para crear registros de auditoría fácilmente
        """
        return cls.objects.create(
            ticket=ticket,
            operacion=operacion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            campos_modificados=campos_modificados,
            usuario=usuario,
            ip_usuario=ip_usuario,
            comentario=comentario
        )


# Sistema de Auditoría Automática
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import json

# Variable para almacenar el estado anterior del ticket
_ticket_estados_anteriores = {}

@receiver(pre_save, sender=Ticket)
def guardar_estado_anterior(sender, instance, **kwargs):
    """
    Guarda el estado anterior del ticket antes de guardarlo
    """
    if instance.pk:  # Solo si el ticket ya existe
        try:
            ticket_anterior = Ticket.objects.get(pk=instance.pk)
            _ticket_estados_anteriores[instance.pk] = {
                'usuario_asignado': ticket_anterior.usuario_asignado,
                'estado': ticket_anterior.estado,
                'solucion': ticket_anterior.solucion
            }
        except Ticket.DoesNotExist:
            pass

@receiver(post_save, sender=Ticket)
def auditoria_automatica_ticket(sender, instance, created, **kwargs):
    """
    Signal que registra automáticamente las 3 acciones principales:
    1. Creación del ticket
    2. Asignación del ticket  
    3. Resolución del ticket
    """
    try:
        # 1. CREACIÓN: Cuando se crea un ticket nuevo
        if created:
            datos_ticket = {
                'codigo': instance.codigo,
                'nombre': instance.nombre,
                'apellido': instance.apellido,
                'correo': instance.correo,
                'agencia': instance.agencia.nombre if instance.agencia else None,
                'tipo_solicitud': instance.tipo_solicitud,
                'estado': instance.estado,
                'descripcion': instance.descripcion[:100] + '...' if len(instance.descripcion) > 100 else instance.descripcion,
            }
            
            TicketAuditoria.crear_auditoria(
                ticket=instance,
                operacion='CREATE',
                datos_nuevos=datos_ticket,
                usuario=instance.usuario_crea,
                comentario=f'Ticket creado por {instance.usuario_crea.get_full_name() or instance.usuario_crea.username if instance.usuario_crea else "Sistema"}'
            )
            return
        
        # Para tickets existentes, verificar cambios usando el estado anterior guardado
        estado_anterior = _ticket_estados_anteriores.get(instance.pk)
        if estado_anterior:
            
            # 2. ASIGNACIÓN: Cuando se asigna un ticket (cambió usuario_asignado de None a algún usuario)
            if (estado_anterior['usuario_asignado'] is None and 
                instance.usuario_asignado is not None):
                
                datos_anteriores = {
                    'usuario_asignado': None,
                    'estado': estado_anterior['estado']
                }
                
                datos_nuevos = {
                    'usuario_asignado': instance.usuario_asignado.username,
                    'estado': instance.estado
                }
                
                TicketAuditoria.crear_auditoria(
                    ticket=instance,
                    operacion='ASSIGN',
                    datos_anteriores=datos_anteriores,
                    datos_nuevos=datos_nuevos,
                    campos_modificados=['usuario_asignado', 'estado'],
                    usuario=instance.usuario_actualiza,
                    comentario=f'Ticket asignado a {instance.usuario_asignado.get_full_name() or instance.usuario_asignado.username}'
                )
            
            # 3. RESOLUCIÓN: Cuando se resuelve un ticket (estado cambió a "resuelto")
            elif (estado_anterior['estado'] != 'resuelto' and 
                  instance.estado == 'resuelto'):
                
                datos_anteriores = {
                    'estado': estado_anterior['estado'],
                    'solucion': estado_anterior['solucion'] or ""
                }
                
                datos_nuevos = {
                    'estado': instance.estado,
                    'solucion': instance.solucion or ""
                }
                
                TicketAuditoria.crear_auditoria(
                    ticket=instance,
                    operacion='RESOLVE',
                    datos_anteriores=datos_anteriores,
                    datos_nuevos=datos_nuevos,
                    campos_modificados=['estado', 'solucion'],
                    usuario=instance.usuario_actualiza,
                    comentario=f'Ticket resuelto por {instance.usuario_actualiza.get_full_name() or instance.usuario_actualiza.username if instance.usuario_actualiza else "Sistema"}'
                )
            
            # Limpiar el estado anterior después de usarlo
            del _ticket_estados_anteriores[instance.pk]
            
    except Exception as e:
        # En caso de error, no afectar el guardado del ticket
        print(f"Error en auditoría automática: {e}")
        pass
