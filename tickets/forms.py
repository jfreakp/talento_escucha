from django import forms
from django.contrib.auth.models import User
from .models import Agencia, Ticket, crear_auditoria_ticket


class TicketForm(forms.ModelForm):
    """
    Formulario para crear tickets de solicitudes
    """
    
    class Meta:
        model = Ticket
        fields = [
            'nombre',
            'apellido', 
            'correo',
            'telefono',
            'agencia',
            'tipo_solicitud',
            'severidad',
            'descripcion'
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingresa tu nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingresa tu apellido'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'tu@email.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '0985297123'
            }),
            'agencia': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'tipo_solicitud': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'severidad': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Describe detalladamente tu solicitud...'
            })
        }
        
        labels = {
            'nombre': 'Nombre *',
            'apellido': 'Apellido *',
            'correo': 'Correo Electrónico *',
            'telefono': 'Teléfono *',
            'agencia': 'Agencia *',
            'tipo_solicitud': 'Tipo de Solicitud *',
            'severidad': 'Severidad *',
            'descripcion': 'Descripción de la Solicitud *'
        }
        
        help_texts = {
            'nombre': 'Tu nombre completo',
            'apellido': 'Tu apellido',
            'correo': 'Email donde te contactaremos',
            'telefono': 'Número de contacto requerido',
            'agencia': 'Selecciona tu agencia o empresa',
            'tipo_solicitud': 'Selecciona el tipo de servicio que necesitas',
            'severidad': 'Selecciona qué tan urgente es tu solicitud',
            'descripcion': 'Explica en detalle qué necesitas'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Si hay un usuario autenticado, pre-llenar algunos campos
        if self.user and self.user.is_authenticated:
            if self.user.first_name:
                self.fields['nombre'].initial = self.user.first_name
            if self.user.last_name:
                self.fields['apellido'].initial = self.user.last_name
            if self.user.email:
                self.fields['correo'].initial = self.user.email
    
    def clean_correo(self):
        """Validación personalizada para el correo"""
        correo = self.cleaned_data.get('correo')
        if correo:
            correo = correo.lower().strip()
        return correo
    
    def clean_telefono(self):
        """Validación personalizada para el teléfono"""
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Limpiar caracteres especiales pero mantener números, espacios, + y ()
            telefono = ''.join(char for char in telefono if char.isdigit() or char in ' +()-')
            telefono = telefono.strip()
        return telefono
    
    def save(self, commit=True):
        """Override del save para asignar usuario automáticamente"""
        ticket = super().save(commit=False)
        
        # Asignar usuario de creación si está autenticado
        if self.user and self.user.is_authenticated:
            ticket.usuario_crea = self.user
            ticket.usuario_actualiza = self.user
        
        # Estado inicial
        ticket.estado = 'pendiente'
        
        if commit:
            ticket.save()
            
            # Crear registro de auditoría para la creación
            datos_ticket = {
                'id': ticket.id,
                'codigo': ticket.codigo,
                'nombre': ticket.nombre,
                'apellido': ticket.apellido,
                'correo': ticket.correo,
                'agencia_nombre': ticket.agencia.nombre if ticket.agencia else None,
                'telefono': ticket.telefono,
                'tipo_solicitud': ticket.tipo_solicitud,
                'estado': ticket.estado,
                'descripcion': ticket.descripcion,
            }
            
            crear_auditoria_ticket(
                ticket=ticket,
                operacion='CREATE',
                datos_nuevos=datos_ticket,
                usuario=self.user if self.user and self.user.is_authenticated else None,
                comentario=f'Ticket creado por {self.user.get_full_name() or self.user.username if self.user and self.user.is_authenticated else "Usuario anónimo"}'
            )
            
        return ticket


class TicketAnonimForm(forms.ModelForm):
    """
    Formulario para usuarios anónimos (sin login) - Solo campos básicos
    """
    
    class Meta:
        model = Ticket
        fields = [
            'agencia',
            'tipo_solicitud',
            'severidad',
            'descripcion'
        ]
        
        widgets = {
            'agencia': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'tipo_solicitud': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'severidad': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Describe detalladamente tu solicitud...'
            })
        }
        
        labels = {
            'agencia': 'Agencia *',
            'tipo_solicitud': 'Tipo de Solicitud *',
            'severidad': 'Severidad *',
            'descripcion': 'Descripción de la Solicitud *'
        }
        
        help_texts = {
            'agencia': 'Selecciona la agencia relacionada',
            'tipo_solicitud': 'Selecciona el tipo de servicio que necesitas',
            'severidad': 'Selecciona qué tan urgente es tu solicitud',
            'descripcion': 'Explica en detalle qué necesitas'
        }
    
    def save(self, commit=True):
        """Override del save para usuarios anónimos"""
        ticket = super().save(commit=False)
        
        # Para solicitudes anónimas, establecer valores por defecto
        ticket.nombre = 'Anónimo'
        ticket.apellido = 'Anónimo'
        ticket.correo = 'anonimo@example.com'
        ticket.telefono = 'N/A'
        
        # Estado inicial para usuarios anónimos
        ticket.estado = 'pendiente'
        
        if commit:
            ticket.save()
            
            # Crear registro de auditoría para la creación anónima
            datos_ticket = {
                'id': ticket.id,
                'codigo': ticket.codigo,
                'nombre': ticket.nombre,
                'apellido': ticket.apellido,
                'correo': ticket.correo,
                'telefono': ticket.telefono,
                'tipo_solicitud': ticket.tipo_solicitud,
                'estado': ticket.estado,
                'descripcion': ticket.descripcion,
            }
            
            crear_auditoria_ticket(
                ticket=ticket,
                operacion='CREATE',
                datos_nuevos=datos_ticket,
                usuario=None,  # Usuario anónimo
                comentario='Ticket creado por usuario anónimo'
            )
            
        return ticket