from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm


class UserProfileForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'Ingresa tu nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'Ingresa tu apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'placeholder': 'correo@ejemplo.com'
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
        }

    def clean_email(self):
        """Validar que el email no esté en uso por otro usuario"""
        email = self.cleaned_data.get('email')
        if self.instance and email:
            # Verificar si otro usuario ya tiene este email
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError('Este email ya está siendo utilizado por otro usuario.')
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulario personalizado para cambio de contraseña"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar los widgets
        self.fields['old_password'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
            'placeholder': 'Contraseña actual'
        })
        
        self.fields['new_password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
            'placeholder': 'Nueva contraseña'
        })
        
        self.fields['new_password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
            'placeholder': 'Confirmar nueva contraseña'
        })
        
        # Personalizar las etiquetas
        self.fields['old_password'].label = 'Contraseña Actual'
        self.fields['new_password1'].label = 'Nueva Contraseña'
        self.fields['new_password2'].label = 'Confirmar Nueva Contraseña'