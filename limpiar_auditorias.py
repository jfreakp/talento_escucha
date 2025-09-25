#!/usr/bin/env python
"""
Script para limpiar registros de auditoría con datos nulos o vacíos
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talento_escucha.settings')
django.setup()

from tickets.models import TicketAuditoria

def limpiar_auditorias():
    """Elimina registros de auditoría con datos nulos o vacíos"""
    
    print("🔍 Buscando registros de auditoría con problemas...")
    
    # Buscar registros problemáticos
    registros_nulos = TicketAuditoria.objects.filter(
        datos_anteriores__isnull=True,
        datos_nuevos__isnull=True,
        campos_modificados__isnull=True
    )
    
    registros_vacios = TicketAuditoria.objects.filter(
        datos_anteriores={},
        datos_nuevos={},
        campos_modificados=[]
    )
    
    registros_sin_usuario = TicketAuditoria.objects.filter(
        usuario__isnull=True,
        comentario__isnull=True
    )
    
    total_nulos = registros_nulos.count()
    total_vacios = registros_vacios.count() 
    total_sin_usuario = registros_sin_usuario.count()
    
    print(f"📊 Registros encontrados:")
    print(f"   - Con datos completamente nulos: {total_nulos}")
    print(f"   - Con datos vacíos: {total_vacios}")
    print(f"   - Sin usuario ni comentario: {total_sin_usuario}")
    
    total_a_eliminar = total_nulos + total_vacios
    
    if total_a_eliminar > 0:
        confirmacion = input(f"\n❓ ¿Deseas eliminar {total_a_eliminar} registros problemáticos? (s/n): ")
        
        if confirmacion.lower() in ['s', 'si', 'yes', 'y']:
            print("\n🗑️ Eliminando registros problemáticos...")
            
            # Eliminar registros nulos
            if total_nulos > 0:
                registros_nulos.delete()
                print(f"   ✅ Eliminados {total_nulos} registros con datos nulos")
            
            # Eliminar registros vacíos
            if total_vacios > 0:
                registros_vacios.delete()
                print(f"   ✅ Eliminados {total_vacios} registros con datos vacíos")
            
            print(f"\n🎉 Limpieza completada! Se eliminaron {total_a_eliminar} registros problemáticos.")
        else:
            print("\n❌ Limpieza cancelada.")
    else:
        print("\n✅ No se encontraron registros problemáticos para eliminar.")
    
    # Mostrar estadísticas finales
    total_restantes = TicketAuditoria.objects.count()
    print(f"\n📈 Registros de auditoría restantes: {total_restantes}")

if __name__ == "__main__":
    limpiar_auditorias()