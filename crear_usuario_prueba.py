#!/usr/bin/env python
import os
import sys
import django

# Agregar el directorio del proyecto al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talento_escucha.settings')
django.setup()

from django.contrib.auth.models import User

# Crear usuario de prueba
def crear_usuario_prueba():
    try:
        # Verificar si el usuario ya existe
        if User.objects.filter(username='testuser').exists():
            print("El usuario 'testuser' ya existe.")
        else:
            # Crear usuario de prueba
            user = User.objects.create_user(
                username='testuser',
                email='test@ejemplo.com',
                password='testpassword123',
                first_name='Usuario',
                last_name='Prueba'
            )
            print(f"Usuario creado: {user.username} ({user.email})")
            
        # Mostrar usuarios existentes
        print("\nUsuarios existentes:")
        for user in User.objects.all():
            print(f"- {user.username} ({user.email}) - Activo: {user.is_active}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    crear_usuario_prueba()