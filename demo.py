"""
DEMO DEL SCRAPER APUDACTA
=========================

Este script te permite ver paso a paso lo que hace el scraper
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.apudacta_scraper import ApudActaScraper
import time

def demo_scraper():
    """Demostración paso a paso del scraper"""
    
    print("=" * 60)
    print("🤖 DEMO: APUDACTA SCRAPER")
    print("=" * 60)
    print()
    
    # Verificar configuración
    print("📋 PASO 1: Verificando configuración...")
    scraper = ApudActaScraper()
    
    if not scraper.email or scraper.email == "jesusorzsa@ruaabogados.es":
        print("❌ ERROR: Necesitas configurar tu email en el archivo .env")
        print("   Edita el archivo .env con tu email y contraseña reales")
        return
    
    if not scraper.password or scraper.password == "tu_contraseña_aqui":
        print("❌ ERROR: Necesitas configurar tu contraseña en el archivo .env")
        print("   Edita el archivo .env con tu email y contraseña reales")
        return
    
    print(f"✅ Email configurado: {scraper.email}")
    print(f"✅ Carpeta de descarga: {scraper.download_path}")
    print(f"✅ Carpeta de logs: {scraper.log_path}")
    print(f"✅ Modo headless: {scraper.headless}")
    print()
    
    input("Presiona ENTER para continuar...")
    
    try:
        print("🌐 PASO 2: Configurando navegador Chrome...")
        scraper.setup_driver()
        print("✅ Navegador configurado correctamente")
        print()
        
        input("Presiona ENTER para hacer login...")
        
        print("🔐 PASO 3: Realizando login en ApudActa...")
        print(f"   → Conectando a: {scraper.login_url}")
        
        if scraper.login():
            print("✅ Login exitoso!")
        else:
            print("❌ Error en el login")
            return
        print()
        
        input("Presiona ENTER para navegar a descargas...")
        
        print("🧭 PASO 4: Navegando a sección de descargas...")
        if scraper.navigate_to_downloads():
            print("✅ Navegación exitosa!")
        else:
            print("❌ Error en la navegación")
            return
        print()
        
        input("Presiona ENTER para buscar archivos...")
        
        print("🔍 PASO 5: Buscando archivos disponibles...")
        downloads = scraper.get_available_downloads()
        
        if downloads:
            print(f"✅ Encontrados {len(downloads)} archivos para descargar:")
            print()
            for i, download in enumerate(downloads, 1):
                print(f"   📄 {i}. {download['nombre']}")
                print(f"      📊 Tamaño: {download['tamaño']}")
                print(f"      📅 Fecha: {download['fecha']}")
                print(f"      📁 Archivos: {download['archivos']}")
                print(f"      ⚖️ Apudactas: {download['apudactas']}")
                print()
        else:
            print("ℹ️ No se encontraron archivos nuevos para descargar")
            print()
        
        if downloads:
            response = input("¿Quieres descargar los archivos? (s/N): ").strip().lower()
            
            if response == 's':
                print("\n📥 PASO 6: Descargando archivos...")
                
                successful = 0
                failed = 0
                
                for i, download in enumerate(downloads, 1):
                    print(f"\n📥 Descargando {i}/{len(downloads)}: {download['nombre']}...")
                    
                    if scraper.download_file(download):
                        successful += 1
                        print("✅ Descarga completada")
                    else:
                        failed += 1
                        print("❌ Error en la descarga")
                    
                    time.sleep(2)  # Pausa entre descargas
                
                print(f"\n📊 RESUMEN DE DESCARGAS:")
                print(f"   ✅ Exitosas: {successful}")
                print(f"   ❌ Fallidas: {failed}")
                
                print("\n📝 PASO 7: Generando reporte...")
                report_file = scraper.generate_report()
                if report_file:
                    print(f"✅ Reporte generado: {report_file}")
                
            else:
                print("⏭️ Saltando descargas por solicitud del usuario")
        
        print("\n🎯 DEMOSTRACIÓN COMPLETADA")
        print("=" * 60)
        print("El scraper funciona correctamente!")
        print("Para uso automático diario, ejecuta: python scheduler.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error durante la demostración: {e}")
        
    finally:
        if scraper.driver:
            print("\n🔚 Cerrando navegador...")
            scraper.driver.quit()


if __name__ == "__main__":
    demo_scraper()
