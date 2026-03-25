from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import logging

# Configurar logger para notificaciones
logger = logging.getLogger('tickets.notifications')


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
    
    provincia = models.CharField(
        max_length=100,
        verbose_name="Provincia",
        help_text="Provincia donde se ubica la agencia",
        blank=True,
        null=True
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
            models.Index(fields=['provincia']),
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

    motivo_rechazo = models.TextField(
        verbose_name="Motivo de Rechazo",
        help_text="Razón registrada cuando el ticket es rechazado o cancelado",
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
            
            # Enviar notificación a revisores cuando se crea un nuevo ticket
            enviar_notificacion_nuevo_ticket(self)
            # Enviar confirmación al solicitante cuando se crea un nuevo ticket
            enviar_confirmacion_creacion_ticket(self)


class TicketAuditoria(models.Model):
    """
    Tabla de auditoría para el modelo Ticket
    Registra todos los cambios realizados en los tickets
    """
    
    # Tipos de operación
    OPERACION_CHOICES = [
        ('CREATE', 'Creación'),
        ('ASSIGN', 'Asignación'),
        ('REJECT', 'Rechazo'),
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
                'solucion': ticket_anterior.solucion,
                'motivo_rechazo': ticket_anterior.motivo_rechazo,
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

            usuario_asignado_anterior = estado_anterior['usuario_asignado']
            usuario_asignado_actual = instance.usuario_asignado

            # 2. ASIGNACIÓN / REASIGNACIÓN: cuando cambia el responsable del ticket
            if (
                usuario_asignado_actual is not None and
                (
                    usuario_asignado_anterior is None or
                    usuario_asignado_anterior.pk != usuario_asignado_actual.pk
                )
            ):

                datos_anteriores = {
                    'usuario_asignado': (
                        usuario_asignado_anterior.username if usuario_asignado_anterior else None
                    ),
                    'estado': estado_anterior['estado']
                }

                datos_nuevos = {
                    'usuario_asignado': usuario_asignado_actual.username,
                    'estado': instance.estado
                }

                campos_modificados = ['usuario_asignado']
                if estado_anterior['estado'] != instance.estado:
                    campos_modificados.append('estado')

                if usuario_asignado_anterior is None:
                    comentario = (
                        f'Ticket asignado a '
                        f'{usuario_asignado_actual.get_full_name() or usuario_asignado_actual.username}'
                    )
                else:
                    comentario = (
                        f'Ticket reasignado de '
                        f'{usuario_asignado_anterior.get_full_name() or usuario_asignado_anterior.username} '
                        f'a {usuario_asignado_actual.get_full_name() or usuario_asignado_actual.username}'
                    )

                TicketAuditoria.crear_auditoria(
                    ticket=instance,
                    operacion='ASSIGN',
                    datos_anteriores=datos_anteriores,
                    datos_nuevos=datos_nuevos,
                    campos_modificados=campos_modificados,
                    usuario=instance.usuario_actualiza,
                    comentario=comentario
                )

                # Enviar notificación al usuario que creó el ticket (excepto si ya se maneja explícitamente en la vista)
                if not getattr(instance, '_skip_assignment_email_signal', False):
                    enviar_notificacion_asignacion_ticket(instance)
            
            # 3. RECHAZO: Cuando se marca el ticket como cancelado/rechazado
            elif (estado_anterior['estado'] != 'cancelado' and
                  instance.estado == 'cancelado'):

                datos_anteriores = {
                    'estado': estado_anterior['estado'],
                    'motivo_rechazo': estado_anterior['motivo_rechazo'] or "",
                }

                datos_nuevos = {
                    'estado': instance.estado,
                    'motivo_rechazo': instance.motivo_rechazo or "",
                }

                TicketAuditoria.crear_auditoria(
                    ticket=instance,
                    operacion='REJECT',
                    datos_anteriores=datos_anteriores,
                    datos_nuevos=datos_nuevos,
                    campos_modificados=['estado', 'motivo_rechazo'],
                    usuario=instance.usuario_actualiza,
                    comentario=(
                        f"Ticket rechazado por "
                        f"{instance.usuario_actualiza.get_full_name() or instance.usuario_actualiza.username if instance.usuario_actualiza else 'Sistema'}"
                        f". Motivo: {instance.motivo_rechazo or 'No especificado'}"
                    )
                )

                if not getattr(instance, '_skip_rejection_email_signal', False):
                    enviar_notificacion_rechazo_ticket(instance)

            # 4. RESOLUCIÓN: Cuando se resuelve un ticket (estado cambió a "resuelto")
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
                
                # Enviar notificación al usuario que creó el ticket
                enviar_notificacion_solucion_ticket(instance)
            
            # Limpiar el estado anterior después de usarlo
            del _ticket_estados_anteriores[instance.pk]
    
    except Exception as e:
        logger.error(f"Error en auditoría automática para ticket {instance.pk}: {str(e)}")


def enviar_notificacion_nuevo_ticket(ticket):
    """
    Envía notificación por correo a todos los usuarios con rol REVISOR y ADMIN
    cuando se crea un nuevo ticket.
    """
    try:
        usuarios_internos = User.objects.filter(
            groups__name__in=['REVISOR', 'ADMIN'],
            is_active=True,
            email__isnull=False,
        ).exclude(email='').distinct()

        if not usuarios_internos.exists():
            logger.warning("No hay usuarios REVISOR o ADMIN activos con email configurado")
            return
        
        # Preparar el contenido del correo
        asunto = f"Nuevo Ticket Creado - {ticket.codigo}"
        
        tipo_solicitud_display = dict(ticket.TIPO_SOLICITUD_CHOICES).get(ticket.tipo_solicitud, ticket.tipo_solicitud)
        
        mensaje = f"""
Estimado/a equipo de gestión,

Se ha creado un nuevo ticket en el sistema PQRS - Talento Escucha.

DETALLES DEL TICKET:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Código: {ticket.codigo}
• Tipo: {tipo_solicitud_display}
• Solicitante: {ticket.nombre_completo}
• Email: {ticket.correo}
• Teléfono: {ticket.telefono}
• Agencia: {ticket.agencia.nombre}
• Provincia: {ticket.agencia.provincia or 'No especificada'}
• Fecha de creación: {ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M')}

DESCRIPCIÓN:
{ticket.descripcion}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Por favor, revise este ticket y proceda con la asignación correspondiente.

Para acceder al sistema y gestionar el ticket, visite:
http://localhost:8000/dashboard/

Saludos cordiales,
Sistema PQRS - Talento Escucha
        """.strip()
        
        # Obtener emails de revisores y administradores
        emails_internos = list(usuarios_internos.values_list('email', flat=True))

        if ticket.usuario_crea and ticket.usuario_crea.email:
            emails_internos.append(ticket.usuario_crea.email)

        recipient_list = list(dict.fromkeys(emails_internos))
        
        # Enviar correo
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        logger.info(f"Notificación enviada a {len(recipient_list)} destinatarios internos para el ticket {ticket.codigo}")
        
    except Exception as e:
        logger.error(f"Error al enviar notificación para ticket {ticket.codigo}: {str(e)}")
        # No lanzar la excepción para evitar que falle la creación del ticket


def enviar_confirmacion_creacion_ticket(ticket):
    """
    Envía confirmación de creación al solicitante del ticket.
    Se notifica al correo de la cuenta (si existe) y al correo ingresado en la solicitud.
    """
    try:
        if not ticket.usuario_crea:
            logger.info(f"Ticket {ticket.codigo} anónimo: no se envía confirmación al solicitante")
            return

        recipient_list = []
        if ticket.usuario_crea and ticket.usuario_crea.email:
            recipient_list.append(ticket.usuario_crea.email)
        if ticket.correo:
            recipient_list.append(ticket.correo)

        recipient_list = list(dict.fromkeys(recipient_list))
        if not recipient_list:
            logger.warning(f"Ticket {ticket.codigo} no tiene correo de destinatario para confirmación de creación")
            return

        destinatario_nombre = ticket.nombre_completo
        tipo_solicitud_display = dict(ticket.TIPO_SOLICITUD_CHOICES).get(ticket.tipo_solicitud, ticket.tipo_solicitud)

        asunto = f"Hemos recibido tu solicitud {ticket.codigo}"
        mensaje = f"""
Estimado/a {destinatario_nombre},

Tu solicitud ha sido registrada correctamente en el sistema PQRS - Talento Escucha.

DETALLES DE TU SOLICITUD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Código: {ticket.codigo}
• Tipo: {tipo_solicitud_display}
• Estado: {dict(ticket.ESTADO_CHOICES).get(ticket.estado, ticket.estado)}
• Fecha de creación: {ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M')}

DESCRIPCIÓN:
{ticket.descripcion}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Conserva este código para hacer seguimiento a tu solicitud.

Saludos cordiales,
Equipo PQRS - Talento Escucha
        """.strip()

        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        logger.info(f"Confirmación de creación enviada a {', '.join(recipient_list)} para el ticket {ticket.codigo}")

    except Exception as e:
        logger.error(f"Error al enviar confirmación de creación para ticket {ticket.codigo}: {str(e)}")


def enviar_notificacion_asignacion_ticket(ticket):
    """
    Envía notificación por correo al solicitante del ticket
    cuando se asigna a un revisor.
    """
    try:
        # Notificar a ambas partes: solicitante y revisor asignado.
        recipient_list = []
        if ticket.usuario_crea and ticket.usuario_crea.email:
            recipient_list.append(ticket.usuario_crea.email)
        if ticket.correo:
            recipient_list.append(ticket.correo)
        if ticket.usuario_asignado and ticket.usuario_asignado.email:
            recipient_list.append(ticket.usuario_asignado.email)

        recipient_list = list(dict.fromkeys(recipient_list))
        destinatario_nombre = ticket.nombre_completo

        if not recipient_list:
            logger.warning(f"Ticket {ticket.codigo} no tiene correo de destinatario para notificación de asignación")
            return
        
        # Preparar el contenido del correo
        asunto = f"Tu solicitud {ticket.codigo} ha sido asignada para revisión"
        
        tipo_solicitud_display = dict(ticket.TIPO_SOLICITUD_CHOICES).get(ticket.tipo_solicitud, ticket.tipo_solicitud)
        revisor_nombre = ticket.usuario_asignado.get_full_name() or ticket.usuario_asignado.username
        
        mensaje = f"""
Estimado/a {destinatario_nombre},

Tu solicitud ha sido asignada para revisión en el sistema PQRS - Talento Escucha.

DETALLES DE TU SOLICITUD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Código: {ticket.codigo}
• Tipo: {tipo_solicitud_display}
• Estado: En Proceso de Revisión
• Asignado a: {revisor_nombre}
• Fecha de asignación: {ticket.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')}

DESCRIPCIÓN ORIGINAL:
{ticket.descripcion}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hemos iniciado el proceso de revisión de tu solicitud. Te mantendremos informado sobre el progreso y te notificaremos cuando tengamos una respuesta.

Si tienes alguna pregunta adicional, puedes contactarnos respondiendo a este correo.

Saludos cordiales,
Equipo PQRS - Talento Escucha
        """.strip()
        
        # Enviar correo
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f"Notificación de asignación enviada a {', '.join(recipient_list)} para el ticket {ticket.codigo}")
        
    except Exception as e:
        logger.error(f"Error al enviar notificación de asignación para ticket {ticket.codigo}: {str(e)}")


def enviar_notificacion_solucion_ticket(ticket):
    """
    Envía notificación por correo al solicitante del ticket
    cuando se proporciona una solución.
    """
    try:
        # Notificar a ambas partes: solicitante y revisor asignado.
        recipient_list = []
        if ticket.usuario_crea and ticket.usuario_crea.email:
            recipient_list.append(ticket.usuario_crea.email)
        if ticket.correo:
            recipient_list.append(ticket.correo)
        if ticket.usuario_asignado and ticket.usuario_asignado.email:
            recipient_list.append(ticket.usuario_asignado.email)

        recipient_list = list(dict.fromkeys(recipient_list))
        destinatario_nombre = ticket.nombre_completo

        if not recipient_list:
            logger.warning(f"Ticket {ticket.codigo} no tiene correo de destinatario para notificación de solución")
            return
        
        # Preparar el contenido del correo
        asunto = f"Solución disponible para tu solicitud {ticket.codigo}"
        
        tipo_solicitud_display = dict(ticket.TIPO_SOLICITUD_CHOICES).get(ticket.tipo_solicitud, ticket.tipo_solicitud)
        estado_display = dict(ticket.ESTADO_CHOICES).get(ticket.estado, ticket.estado)
        revisor_nombre = ticket.usuario_asignado.get_full_name() or ticket.usuario_asignado.username if ticket.usuario_asignado else "Equipo de Revisión"
        
        mensaje = f"""
    Estimado/a {destinatario_nombre},

Tenemos una respuesta para tu solicitud en el sistema PQRS - Talento Escucha.

DETALLES DE TU SOLICITUD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Código: {ticket.codigo}
• Tipo: {tipo_solicitud_display}
• Estado: {estado_display}
• Atendido por: {revisor_nombre}
• Fecha de solución: {ticket.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')}

DESCRIPCIÓN ORIGINAL:
{ticket.descripcion}

SOLUCIÓN PROPORCIONADA:
{ticket.solucion or 'No se proporcionó descripción de la solución.'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tu solicitud ha sido atendida. Si consideras que la solución no resuelve completamente tu consulta o tienes preguntas adicionales, no dudes en contactarnos.

Gracias por usar nuestro sistema PQRS.

Saludos cordiales,
Equipo PQRS - Talento Escucha
        """.strip()
        
        # Enviar correo
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f"Notificación de solución enviada a {', '.join(recipient_list)} para el ticket {ticket.codigo}")
        
    except Exception as e:
        logger.error(f"Error al enviar notificación de solución para ticket {ticket.codigo}: {str(e)}")


def enviar_notificacion_rechazo_ticket(ticket):
    """
    Envía notificación por correo a las personas involucradas cuando un ticket es rechazado.
    """
    try:
        recipient_list = []
        if ticket.usuario_crea and ticket.usuario_crea.email:
            recipient_list.append(ticket.usuario_crea.email)
        if ticket.correo:
            recipient_list.append(ticket.correo)
        if ticket.usuario_asignado and ticket.usuario_asignado.email:
            recipient_list.append(ticket.usuario_asignado.email)

        recipient_list = list(dict.fromkeys(recipient_list))
        destinatario_nombre = ticket.nombre_completo

        if not recipient_list:
            logger.warning(f"Ticket {ticket.codigo} no tiene correos para notificación de rechazo")
            return

        asunto = f"Tu solicitud {ticket.codigo} ha sido rechazada"
        tipo_solicitud_display = dict(ticket.TIPO_SOLICITUD_CHOICES).get(ticket.tipo_solicitud, ticket.tipo_solicitud)
        motivo_rechazo = ticket.motivo_rechazo or 'No se proporcionó un motivo adicional.'

        mensaje = f"""
Estimado/a {destinatario_nombre},

Tu solicitud ha sido rechazada en el sistema PQRS - Talento Escucha.

DETALLES DE TU SOLICITUD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Código: {ticket.codigo}
• Tipo: {tipo_solicitud_display}
• Estado: {dict(ticket.ESTADO_CHOICES).get(ticket.estado, ticket.estado)}
• Fecha de actualización: {ticket.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')}

MOTIVO DEL RECHAZO:
{motivo_rechazo}

DESCRIPCIÓN ORIGINAL:
{ticket.descripcion}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Si necesitas más información, puedes comunicarte con nuestro equipo indicando el código del ticket.

Saludos cordiales,
Equipo PQRS - Talento Escucha
        """.strip()

        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        logger.info(f"Notificación de rechazo enviada a {', '.join(recipient_list)} para el ticket {ticket.codigo}")

    except Exception as e:
        logger.error(f"Error al enviar notificación de rechazo para ticket {ticket.codigo}: {str(e)}")
            
    except Exception as e:
        # En caso de error, no afectar el guardado del ticket
        print(f"Error en auditoría automática: {e}")
        pass
