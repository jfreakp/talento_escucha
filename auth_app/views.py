from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import random
import string

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {user.get_full_name() or user.username}!')
                
                # Redirigir a la página solicitada o al dashboard
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('/dashboard/')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'auth_app/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.get_full_name() or request.user.username
        logout(request)
        messages.success(request, f'¡Hasta luego, {username}!')
    
    return redirect('homepage:home')

def generate_temporary_password(length=8):
    """Genera una contraseña temporal aleatoria"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def forgot_password_view(request):
    """Vista para recuperar contraseña olvidada"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if email:
            try:
                # Buscar usuario por email
                user = User.objects.get(email=email)
                
                # Generar contraseña temporal
                temp_password = generate_temporary_password()
                
                # Actualizar contraseña del usuario
                user.set_password(temp_password)
                user.save()
                
                # Enviar email con contraseña temporal
                subject = 'Contraseña Temporal - Talento Escucha'
                message = f'''
Hola {user.get_full_name() or user.username},

Hemos recibido una solicitud para restablecer tu contraseña.

Tu contraseña temporal es: {temp_password}

Por favor, inicia sesión con esta contraseña temporal y cámbiala por una nueva desde tu perfil.

Si no solicitaste este cambio, por favor contacta con nuestro equipo de soporte.

Saludos,
Equipo de Talento Escucha
                '''
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    messages.success(request, f'Se ha enviado una contraseña temporal a {email}. Revisa tu correo.')
                    return redirect('auth_app:login')
                except Exception as e:
                    messages.error(request, 'Error al enviar el correo. Inténtalo de nuevo más tarde.')
                    
            except User.DoesNotExist:
                # No mostrar que el usuario no existe por seguridad
                messages.success(request, f'Si el correo {email} está registrado, recibirás una contraseña temporal.')
                return redirect('auth_app:login')
        else:
            messages.error(request, 'Por favor, ingresa tu dirección de correo electrónico.')
    
    return render(request, 'auth_app/forgot_password.html')
