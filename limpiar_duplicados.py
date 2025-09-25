#!/usr/bin/env python
"""
Script para limpiar auditorías duplicadas y problemas
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talento_escucha.settings')
django.setup()

from tickets.models import TicketAuditoria

def limpiar_auditorias_duplicadas():
    """Elimina registros duplicados y problemáticos"""
    
    print("🔍 Identificando registros problemáticos...")
    
    # Eliminar registros automáticos duplicados (los que tienen "automáticamente" en el comentario)
    registros_automaticos = TicketAuditoria.objects.filter(
        comentario__contains="automáticamente"
    )
    
    # Eliminar registros sin usuario (tickets creados de forma automática sin contexto)
    registros_sin_usuario = TicketAuditoria.objects.filter(
        usuario__isnull=True,
        operacion='CREATE'
    )
    
    count_automaticos = registros_automaticos.count()
    count_sin_usuario = registros_sin_usuario.count()
    
    print(f"📊 Registros encontrados:")
    print(f"   - Registros automáticos duplicados: {count_automaticos}")
    print(f"   - Registros CREATE sin usuario: {count_sin_usuario}")
    
    total_a_eliminar = count_automaticos + count_sin_usuario
    
    if total_a_eliminar > 0:
        confirmacion = input(f"\n❓ ¿Deseas eliminar {total_a_eliminar} registros problemáticos? (s/n): ")
        
        if confirmacion.lower() in ['s', 'si', 'yes', 'y']:
            print("\n🗑️ Eliminando registros problemáticos...")
            
            # Eliminar registros automáticos
            if count_automaticos > 0:
                registros_automaticos.delete()
                print(f"   ✅ Eliminados {count_automaticos} registros automáticos duplicados")
            
            # Eliminar registros sin usuario
            if count_sin_usuario > 0:
                registros_sin_usuario.delete() 
                print(f"   ✅ Eliminados {count_sin_usuario} registros CREATE sin usuario")
            
            print(f"\n🎉 Limpieza completada! Se eliminaron {total_a_eliminar} registros problemáticos.")
        else:
            print("\n❌ Limpieza cancelada.")
    else:
        print("\n✅ No se encontraron registros problemáticos para eliminar.")
    
    # Mostrar estadísticas finales
    total_restantes = TicketAuditoria.objects.count()
    print(f"\n📈 Registros de auditoría restantes: {total_restantes}")
    
    # Mostrar estadísticas por operación después de la limpieza
    print("\n📈 Estadísticas por operación después de la limpieza:")
    from collections import Counter
    operaciones = TicketAuditoria.objects.values_list('operacion', flat=True)
    counter = Counter(operaciones)
    for operacion, count in counter.items():
        print(f"   - {operacion}: {count} registros")

if __name__ == "__main__":
    limpiar_auditorias_duplicadas()