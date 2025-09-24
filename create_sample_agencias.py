#!/usr/bin/env python
"""
Script para crear agencias de ejemplo
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talento_escucha.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import Agencia

def create_sample_agencias():
    """Crear agencias de ejemplo"""
    
    # Obtener o crear usuario admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@talento-escucha.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Lista de agencias de ejemplo
    agencias_data = [
        {
            'codigo_faces': '1',
            'nombre': 'Loja'
        },
        {
            'codigo_faces': '2',
            'nombre': 'Zamora'
        }
        ]
    
    # Crear las agencias
    created_count = 0
    for agencia_data in agencias_data:
        agencia, created = Agencia.objects.get_or_create(
            codigo_faces=agencia_data['codigo_faces'],
            defaults={
                'nombre': agencia_data['nombre'],
                'usuario_creacion': admin_user,
                'usuario_actualizacion': admin_user
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Creada agencia: {agencia.codigo_faces} - {agencia.nombre}")
        else:
            print(f"ℹ️  Ya existe agencia: {agencia.codigo_faces} - {agencia.nombre}")
    
    print(f"\n🎉 Proceso completado. Se crearon {created_count} nuevas agencias.")
    print(f"📊 Total de agencias en el sistema: {Agencia.objects.count()}")

if __name__ == '__main__':
    create_sample_agencias()