#!/usr/bin/env python
"""
Script para probar la nueva funcionalidad de reportes de tickets
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talento_escucha.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import Ticket, Agencia

def main():
    print("🧪 PROBANDO FUNCIONALIDAD DE REPORTES")
    print("=" * 50)
    
    # Verificar que existan tickets en la base de datos
    total_tickets = Ticket.objects.count()
    print(f"📊 Total de tickets en la base de datos: {total_tickets}")
    
    if total_tickets == 0:
        print("⚠️  No hay tickets en la base de datos para generar reportes")
        return
    
    # Mostrar distribución por estado
    print("\n📈 DISTRIBUCIÓN POR ESTADO:")
    estados = ['pendiente', 'en_proceso', 'resuelto', 'cerrado']
    for estado in estados:
        count = Ticket.objects.filter(estado=estado).count()
        print(f"   {estado.title()}: {count} tickets")
    
    # Mostrar distribución por tipo
    print("\n📋 DISTRIBUCIÓN POR TIPO:")
    tipos = [('P', 'Petición'), ('Q', 'Queja'), ('R', 'Reclamo'), ('S', 'Sugerencia')]
    for tipo_code, tipo_name in tipos:
        count = Ticket.objects.filter(tipo_solicitud=tipo_code).count()
        print(f"   {tipo_name}: {count} tickets")
    
    # Mostrar tickets recientes
    print("\n🕒 ÚLTIMOS 5 TICKETS CREADOS:")
    ultimos = Ticket.objects.order_by('-fecha_creacion')[:5]
    for ticket in ultimos:
        fecha = ticket.fecha_creacion.strftime("%d/%m/%Y %H:%M")
        tipo_display = dict(Ticket.TIPO_SOLICITUD_CHOICES).get(ticket.tipo_solicitud, ticket.tipo_solicitud)
        estado_display = dict(Ticket.ESTADO_CHOICES).get(ticket.estado, ticket.estado)
        print(f"   #{ticket.codigo} - {tipo_display} - {estado_display} - {fecha}")
    
    print("\n✅ FUNCIONALIDAD DE REPORTES LISTA")
    print("💡 Para probar:")
    print("   1. Inicia sesión con un usuario REVISOR o ADMIN")
    print("   2. Ve al menú 'Reportería' > 'Reporte Tickets'")
    print("   3. Selecciona filtros y genera el PDF")
    print(f"   4. Servidor corriendo en: http://127.0.0.1:8000")

if __name__ == '__main__':
    main()