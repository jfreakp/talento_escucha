#!/usr/bin/env python
"""
Script para revisar registros de auditoría existentes
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talento_escucha.settings')
django.setup()

from tickets.models import TicketAuditoria

def revisar_auditorias():
    """Revisa y muestra el estado de los registros de auditoría"""
    
    print("🔍 Revisando registros de auditoría...")
    
    # Obtener todos los registros
    auditorias = TicketAuditoria.objects.all().order_by('-fecha_cambio')[:10]
    
    print(f"\n📊 Total de registros: {TicketAuditoria.objects.count()}")
    print(f"📋 Últimos 10 registros:")
    print("-" * 100)
    
    for auditoria in auditorias:
        print(f"ID: {auditoria.id}")
        print(f"Ticket: {auditoria.ticket.codigo}")
        print(f"Operación: {auditoria.operacion}")
        print(f"Usuario: {auditoria.usuario.username if auditoria.usuario else 'None'}")
        print(f"Fecha: {auditoria.fecha_cambio}")
        print(f"Comentario: {auditoria.comentario or 'None'}")
        print(f"Datos anteriores: {auditoria.datos_anteriores is not None}")
        print(f"Datos nuevos: {auditoria.datos_nuevos is not None}")
        print(f"Campos modificados: {auditoria.campos_modificados is not None}")
        print("-" * 50)
    
    # Estadísticas por operación
    print("\n📈 Estadísticas por operación:")
    operaciones = TicketAuditoria.objects.values('operacion').distinct()
    for op in operaciones:
        count = TicketAuditoria.objects.filter(operacion=op['operacion']).count()
        print(f"   - {op['operacion']}: {count} registros")
    
    # Registros sin usuario
    sin_usuario = TicketAuditoria.objects.filter(usuario__isnull=True).count()
    print(f"\n👤 Registros sin usuario: {sin_usuario}")
    
    # Registros sin comentario
    sin_comentario = TicketAuditoria.objects.filter(comentario__isnull=True).count()
    print(f"💬 Registros sin comentario: {sin_comentario}")

if __name__ == "__main__":
    revisar_auditorias()