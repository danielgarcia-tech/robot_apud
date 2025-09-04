"""
Script de prueba para el scraper sin filtro de fecha
Descarga todos los archivos finalizados disponibles
"""

import os
import sys
from src.apudacta_scraper import ApudActaScraper

def main():
    """Ejecutar prueba del scraper sin filtro de fecha"""
    
    print("=" * 60)
    print(" PRUEBA - DESCARGA DE TODOS LOS ARCHIVOS")
    print("=" * 60)
    print()
    print("Este script descargará:")
    print("- ✅ TODOS los archivos con estado 'FINALIZADA'")
    print("- ✅ Sin filtro de fecha (no solo día anterior)")
    print("- ✅ Con slow motion de 3000ms")
    print("- ✅ Evita duplicados usando historial")
    print()
    
    # Confirmar que el usuario quiere continuar
    respuesta = input("¿Deseas ejecutar la descarga completa? (s/n): ").lower().strip()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Descarga cancelada.")
        return
    
    try:
        # Crear instancia del scraper
        print("\n🤖 Inicializando scraper...")
        scraper = ApudActaScraper()
        
        print(f"⏱️  Configuración de timing:")
        print(f"   - Slow motion delay: {scraper.slow_motion_delay}s")
        print(f"   - Wait implícito: {scraper.implicit_wait}s")
        print(f"   - Wait explícito: {scraper.explicit_wait}s")
        
        print("\n📊 Estado de descargas previas:")
        print(f"   - Archivos ya descargados: {len(scraper.downloaded_files)}")
        
        print("\n🚀 Iniciando descarga completa...")
        
        # Ejecutar scraping completo
        scraper.run_daily_scraping()
        
        print("\n✅ Descarga completa finalizada!")
        print("Revisa la carpeta 'descargas' para ver los archivos descargados.")
        
    except Exception as e:
        print(f"\n❌ Error durante la descarga: {e}")
        
    finally:
        print("\n📊 Proceso completado.")
    
    print("\n" + "=" * 60)
    print(" DESCARGA COMPLETA FINALIZADA")
    print("=" * 60)

if __name__ == "__main__":
    main()
