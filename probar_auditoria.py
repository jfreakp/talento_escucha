#!/usr/bin/env python
"""
Script para probar el sistema de auditoría automática
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talento_escucha.settings')
django.setup()

from tickets.models import Ticket, Agencia, TicketAuditoria
from django.contrib.auth.models import User

def probar_auditoria():
    """Prueba las 3 acciones de auditoría automática"""
    
    print("🧪 Probando sistema de auditoría automática...")
    
    # Limpiar auditorías anteriores para la prueba
    TicketAuditoria.objects.all().delete()
    print("🗑️ Auditorías anteriores eliminadas")
    
    # Obtener datos necesarios
    try:
        agencia = Agencia.objects.first()
        if not agencia:
            print("❌ No hay agencias disponibles. Crea una primero.")
            return
            
        usuario = User.objects.filter(groups__name='REVISOR').first()
        if not usuario:
            usuario = User.objects.first()
            if not usuario:
                print("❌ No hay usuarios disponibles. Crea uno primero.")
                return
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
        return
    
    # PRUEBA 1: CREACIÓN
    print("\n📝 PRUEBA 1: Creación de ticket")
    ticket = Ticket.objects.create(
        nombre="Juan",
        apellido="Pérez",
        correo="juan@test.com",
        agencia=agencia,
        telefono="123456789",
        tipo_solicitud="P",
        descripcion="Esta es una prueba de auditoría automática",
        usuario_crea=usuario
    )
    print(f"✅ Ticket creado: {ticket.codigo}")
    
    # Verificar auditoría de creación
    auditoria_create = TicketAuditoria.objects.filter(ticket=ticket, operacion='CREATE').first()
    if auditoria_create:
        print(f"✅ Auditoría CREATE registrada: {auditoria_create.comentario}")
    else:
        print("❌ No se registró auditoría de creación")
    
    # PRUEBA 2: ASIGNACIÓN
    print("\n👤 PRUEBA 2: Asignación de ticket")
    ticket.usuario_asignado = usuario
    ticket.estado = 'en_proceso'
    ticket.usuario_actualiza = usuario
    ticket.save()
    print(f"✅ Ticket asignado a: {usuario.username}")
    
    # Verificar auditoría de asignación
    auditoria_assign = TicketAuditoria.objects.filter(ticket=ticket, operacion='ASSIGN').first()
    if auditoria_assign:
        print(f"✅ Auditoría ASSIGN registrada: {auditoria_assign.comentario}")
    else:
        print("❌ No se registró auditoría de asignación")
    
    # PRUEBA 3: RESOLUCIÓN
    print("\n✅ PRUEBA 3: Resolución de ticket")
    ticket.solucion = "Esta es la solución de prueba para el ticket de auditoría automática"
    ticket.estado = 'resuelto'
    ticket.usuario_actualiza = usuario
    ticket.save()
    print(f"✅ Ticket resuelto con solución")
    
    # Verificar auditoría de resolución
    auditoria_resolve = TicketAuditoria.objects.filter(ticket=ticket, operacion='RESOLVE').first()
    if auditoria_resolve:
        print(f"✅ Auditoría RESOLVE registrada: {auditoria_resolve.comentario}")
    else:
        print("❌ No se registró auditoría de resolución")
    
    # RESUMEN FINAL
    print("\n📊 RESUMEN DE AUDITORÍAS")
    total_auditorias = TicketAuditoria.objects.filter(ticket=ticket).count()
    print(f"Total de auditorías para el ticket {ticket.codigo}: {total_auditorias}")
    
    auditorias = TicketAuditoria.objects.filter(ticket=ticket).order_by('fecha_cambio')
    for i, auditoria in enumerate(auditorias, 1):
        print(f"{i}. {auditoria.get_operacion_display()}: {auditoria.comentario}")
        print(f"   Usuario: {auditoria.usuario.username if auditoria.usuario else 'Sistema'}")
        print(f"   Fecha: {auditoria.fecha_cambio}")
        print()
    
    if total_auditorias == 3:
        print("🎉 ¡ÉXITO! El sistema de auditoría automática está funcionando correctamente")
        print("✅ Se registraron las 3 acciones: CREATE, ASSIGN, RESOLVE")
    else:
        print(f"⚠️  Se esperaban 3 auditorías pero se registraron {total_auditorias}")
    
    # Limpiar el ticket de prueba
    print(f"\n🗑️ Eliminando ticket de prueba {ticket.codigo}...")
    ticket.delete()
    print("✅ Ticket de prueba eliminado")

if __name__ == "__main__":
    probar_auditoria()