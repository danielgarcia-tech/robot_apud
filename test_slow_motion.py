"""
Script de prueba para el scraper con slow motion y sin TensorFlow
"""

import os
import sys
from src.apudacta_scraper import ApudActaScraper

def main():
    """Ejecutar prueba del scraper con slow motion"""
    
    print("=" * 60)
    print(" PRUEBA - SCRAPER CON SLOW MOTION")
    print("=" * 60)
    print()
    print("Este script probará el scraper con:")
    print("- ✅ Slow motion de 3000ms entre acciones")
    print("- ✅ Waits mejorados")
    print("- ✅ Sin TensorFlow (sin warnings)")
    print("- ✅ Logs detallados de timing")
    print()
    
    # Confirmar que el usuario quiere continuar
    respuesta = input("¿Deseas ejecutar la prueba? (s/n): ").lower().strip()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Prueba cancelada.")
        return
    
    try:
        # Crear instancia del scraper
        print("\n🤖 Inicializando scraper con slow motion...")
        scraper = ApudActaScraper()
        
        print(f"⏱️  Configuración de timing:")
        print(f"   - Slow motion delay: {scraper.slow_motion_delay}s")
        print(f"   - Wait implícito: {scraper.implicit_wait}s")
        print(f"   - Wait explícito: {scraper.explicit_wait}s")
        
        print("\n🚀 Iniciando prueba completa...")
        
        # Ejecutar scraping diario (esto incluye login, navegación y descarga)
        scraper.run_daily_scraping()
        
        print("\n✅ Prueba completada exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        
    finally:
        print("\n📊 Prueba finalizada.")
    
    print("\n" + "=" * 60)
    print(" PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    main()
