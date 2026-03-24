from django import forms
from django.contrib.auth.models import User
from .models import Agencia, Ticket


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
            # Prellenar desde perfil
            if self.user.first_name:
                self.fields['nombre'].initial = self.user.first_name
            if self.user.last_name:
                self.fields['apellido'].initial = self.user.last_name
            if self.user.email:
                self.fields['correo'].initial = self.user.email

            # Prellenar con datos del último ticket creado por el usuario
            ultimo_ticket = Ticket.objects.filter(usuario_crea=self.user).order_by('-fecha_creacion').first()
            if ultimo_ticket:
                if ultimo_ticket.telefono:
                    self.fields['telefono'].initial = ultimo_ticket.telefono
                if ultimo_ticket.agencia:
                    self.fields['agencia'].initial = ultimo_ticket.agencia_id

            # Bloquear campos de identidad precargados para evitar edición manual
            if self.user.first_name:
                self._lock_prefilled_field('nombre')
            if self.user.last_name:
                self._lock_prefilled_field('apellido')
            if self.user.email:
                self._lock_prefilled_field('correo')

    def _lock_prefilled_field(self, field_name):
        """Bloquea visual y funcionalmente un campo precargado."""
        field = self.fields[field_name]
        field.disabled = True
        field.widget.attrs['readonly'] = 'readonly'
        field.widget.attrs['class'] += ' bg-gray-100 cursor-not-allowed'
    
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

            # Asegurar consistencia de identidad con el perfil autenticado
            if self.user.first_name:
                ticket.nombre = self.user.first_name
            if self.user.last_name:
                ticket.apellido = self.user.last_name
            if self.user.email:
                ticket.correo = self.user.email
        
        # Estado inicial
        ticket.estado = 'pendiente'
        
        if commit:
            ticket.save()  # La auditoría se registra automáticamente con el signal
            
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
            ticket.save()  # La auditoría se registra automáticamente con el signal
            
        return ticket