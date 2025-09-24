#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talento_escucha.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import Ticket, Agencia

def crear_datos_prueba():
    """Crear algunos datos de prueba para el dashboard"""
    
    # Crear algunas agencias si no existen
    if not Agencia.objects.exists():
        print("Creando agencias de prueba...")
        agencias_data = [
            {"codigo_faces": "AG001", "nombre": "Agencia Central"},
            {"codigo_faces": "AG002", "nombre": "Agencia Norte"},
            {"codigo_faces": "AG003", "nombre": "Agencia Sur"},
        ]
        
        for data in agencias_data:
            agencia, created = Agencia.objects.get_or_create(
                codigo_faces=data["codigo_faces"],
                defaults={
                    "nombre": data["nombre"],
                    "usuario_creacion": User.objects.get(username="jfreakp"),
                    "usuario_actualizacion": User.objects.get(username="jfreakp"),
                }
            )
            if created:
                print(f"Agencia creada: {agencia.nombre}")
    
    # Crear algunos tickets de prueba si no existen
    if Ticket.objects.count() < 5:
        print("Creando tickets de prueba...")
        tickets_data = [
            {
                "tipo_solicitud": "P",
                "descripcion": "Solicitud de información sobre servicios - Necesito información detallada sobre los servicios disponibles",
                "nombre": "Juan",
                "apellido": "Pérez",
                "telefono": "3001234567",
                "correo": "juan.perez@email.com",
            },
            {
                "tipo_solicitud": "Q",
                "descripcion": "Queja por mal servicio - El servicio recibido no cumplió con las expectativas",
                "nombre": "María",
                "apellido": "González",
                "telefono": "3009876543",
                "correo": "maria.gonzalez@email.com",
            },
            {
                "tipo_solicitud": "R",
                "descripcion": "Reclamo por facturación incorrecta - La factura presenta errores en los conceptos cobrados",
                "nombre": "Carlos",
                "apellido": "Rodríguez",
                "telefono": "3005555555",
                "correo": "carlos.rodriguez@email.com",
            },
            {
                "tipo_solicitud": "S",
                "descripcion": "Solicitud de reunión - Solicito una reunión para discutir temas importantes",
                "nombre": "Ana",
                "apellido": "López",
                "telefono": "3007777777",
                "correo": "ana.lopez@email.com",
            },
        ]
        
        usuario = User.objects.get(username="jfreakp")
        agencia = Agencia.objects.first()
        
        for data in tickets_data:
            ticket = Ticket.objects.create(
                **data,
                agencia=agencia,
                usuario_crea=usuario,
                usuario_actualiza=usuario,
            )
            print(f"Ticket creado: {ticket.codigo} - {ticket.nombre_completo}")
    
    print("\n=== RESUMEN ===")
    print(f"Total Usuarios: {User.objects.count()}")
    print(f"Total Agencias: {Agencia.objects.count()}")
    print(f"Total Tickets: {Ticket.objects.count()}")
    print(f"- Peticiones (P): {Ticket.objects.filter(tipo_solicitud='P').count()}")
    print(f"- Quejas (Q): {Ticket.objects.filter(tipo_solicitud='Q').count()}")
    print(f"- Reclamos (R): {Ticket.objects.filter(tipo_solicitud='R').count()}")
    print(f"- Solicitudes (S): {Ticket.objects.filter(tipo_solicitud='S').count()}")

if __name__ == "__main__":
    crear_datos_prueba()