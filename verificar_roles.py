#!/usr/bin/env python
"""
Script para verificar los roles del usuario revisor1
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talento_escucha.settings')
django.setup()

from django.contrib.auth.models import User, Group

def main():
    print("🔍 VERIFICANDO ROLES DEL USUARIO")
    print("=" * 50)
    
    try:
        # Buscar el usuario revisor1
        usuario = User.objects.get(username='revisor1')
        print(f"✅ Usuario encontrado: {usuario.username}")
        print(f"   - Nombre completo: {usuario.get_full_name()}")
        print(f"   - Email: {usuario.email}")
        print(f"   - Es superusuario: {usuario.is_superuser}")
        print(f"   - Está activo: {usuario.is_active}")
        
        # Verificar roles/grupos
        grupos = usuario.groups.all()
        print(f"\n👥 GRUPOS/ROLES ASIGNADOS:")
        if grupos.exists():
            for grupo in grupos:
                print(f"   - {grupo.name}")
        else:
            print("   ❌ El usuario NO tiene grupos asignados")
        
        # Verificar si tiene el rol REVISOR específicamente
        tiene_revisor = usuario.groups.filter(name='REVISOR').exists()
        print(f"\n🎯 VERIFICACIÓN ESPECÍFICA:")
        print(f"   - ¿Tiene rol REVISOR?: {tiene_revisor}")
        
        # Mostrar todos los grupos disponibles
        print(f"\n📋 GRUPOS DISPONIBLES EN EL SISTEMA:")
        todos_grupos = Group.objects.all()
        for grupo in todos_grupos:
            print(f"   - {grupo.name}")
            
        # Sugerencias
        if not tiene_revisor:
            print(f"\n🔧 SOLUCIÓN:")
            print(f"   El usuario 'revisor1' NO tiene el rol 'REVISOR' asignado.")
            print(f"   Debes asignarle el rol desde el panel de administración.")
            
    except User.DoesNotExist:
        print("❌ Usuario 'revisor1' no encontrado")
        print("\n👥 USUARIOS DISPONIBLES:")
        usuarios = User.objects.all()
        for user in usuarios:
            grupos_usuario = ", ".join([g.name for g in user.groups.all()])
            print(f"   - {user.username} (grupos: {grupos_usuario or 'sin grupos'})")

if __name__ == '__main__':
    main()