"""
EASYDAY - Scraper ultra simplificado con Playwright
Proceso paso a paso visible sin TensorFlow
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import zipfile
import py7zr

# Cargar variables de entorno
load_dotenv()

class EasyDayScraper:
    """Scraper súper simplificado con Playwright"""
    
    def __init__(self):
        self.email = os.getenv('EMAIL', 'jesusoroza@ruaabogados.es')
        self.password = os.getenv('PASSWORD', 'Ruaabogados2024')
        self.download_path = os.path.abspath('./descargas')
        
        # CONFIGURACIÓN SÚPER SIMPLE
        self.wait_between_steps = 0.5  # 0.5 segundos entre pasos (rápido)
        self.download_wait = 2  # 2 segundos para el paso de descarga
        self.login_url = 'https://app.apudacta.com/login/'
        
        # CONFIGURACIÓN DE SEGURIDAD PARA ARCHIVOS COMPRIMIDOS
        self.archive_password = 'Rua2025'  # 🔐 Contraseña para archivos 7Z
        
        # Crear carpeta de descargas
        Path(self.download_path).mkdir(parents=True, exist_ok=True)
        
        # Variables de estado
        self.page = None
        self.browser = None
        self.context = None
        
        print("🚀 EASYDAY SCRAPER INICIADO")
        print(f"📁 Descargas en: {self.download_path}")
        print(f"⏱️  Wait entre pasos: {self.wait_between_steps}s")
        print(f"🔐 7Z Password: {self.archive_password}")
        print(f"⏰ Wait para descarga: {self.download_wait}s")
    
    def wait_step(self, message=""):
        """Wait de 0.5 segundos entre pasos"""
        if message:
            print(f"⏳ {message}")
        print(f"🕐 Esperando {self.wait_between_steps} segundos...")
        time.sleep(self.wait_between_steps)
    
    def wait_download(self, message=""):
        """Wait especial de 2 segundos para descarga"""
        if message:
            print(f"⏳ {message}")
        print(f"🕐 Esperando {self.download_wait} segundos para descarga...")
        time.sleep(self.download_wait)
    
    def create_password_protected_zip(self, source_file, zip_name):
        """Crear 7Z con contraseña usando la clave Rua2025"""
        try:
            print(f"🔐 Creando 7Z protegido: {zip_name}")
            
            # Crear nombre del archivo 7Z protegido
            protected_zip_path = os.path.join(self.download_path, zip_name.replace('.zip', '.7z'))
            
            # Crear 7Z con contraseña usando py7zr
            with py7zr.SevenZipFile(protected_zip_path, 'w', password=self.archive_password) as archive:
                archive.write(source_file, os.path.basename(source_file))
            
            print(f"✅ 7Z protegido creado: {zip_name.replace('.zip', '.7z')}")
            print(f"🔑 Contraseña: {self.archive_password}")
            
            # Eliminar archivo original por seguridad
            os.remove(source_file)
            print(f"🗑️  Archivo original eliminado por seguridad")
            
            return protected_zip_path
            
        except Exception as e:
            print(f"❌ Error creando 7Z protegido: {e}")
            return None
    
    def setup_browser(self):
        """Configurar Playwright en modo headless"""
        try:
            print("\n🚀 PASO 1: Configurando navegador...")
            
            # Inicializar Playwright
            self.playwright = sync_playwright().start()
            
            # Crear navegador en modo headless (sin ventana visible)
            self.browser = self.playwright.chromium.launch(
                headless=True,  # MODO HEADLESS
                args=[
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # Crear contexto con configuración de descargas
            self.context = self.browser.new_context(
                accept_downloads=True
            )
            
            # Crear página
            self.page = self.context.new_page()
            
            print("✅ Navegador configurado correctamente")
            print("✅ MODO HEADLESS ACTIVADO (sin ventana visible)")
            
            self.wait_step("Navegador listo")
            
        except Exception as e:
            print(f"❌ Error configurando navegador: {e}")
            raise
    
    def login(self):
        """Login paso a paso súper simple"""
        try:
            print("\n🔐 PASO 2: Haciendo login...")
            
            # Ir a la página de login
            print("🌐 Navegando a ApudActa...")
            self.page.goto(self.login_url)
            self.wait_step("Página de login cargada")
            
            # Llenar email
            print("📧 Escribiendo email...")
            self.page.fill('#email', self.email)
            self.wait_step("Email ingresado")
            
            # Llenar contraseña
            print("🔑 Escribiendo contraseña...")
            self.page.fill('#password', self.password)
            self.wait_step("Contraseña ingresada")
            
            # Hacer click en login
            print("👆 Haciendo click en 'Inicia sesión'...")
            self.page.click("button:has-text('Inicia sesión')")
            self.wait_step("Botón presionado")
            
            # Esperar a que aparezca APODERAMIENTOS
            print("⏳ Esperando dashboard...")
            self.page.wait_for_selector("text=APODERAMIENTOS", timeout=30000)
            
            print("✅ LOGIN COMPLETADO!")
            self.wait_step("Login verificado")
            
        except Exception as e:
            print(f"❌ Error en login: {e}")
            raise
    
    def navigate_to_downloads(self):
        """Navegar a descargas paso a paso"""
        try:
            print("\n📁 PASO 3: Navegando a descargas...")
            
            # Click en APODERAMIENTOS
            print("👆 Haciendo click en APODERAMIENTOS...")
            self.page.click("text=APODERAMIENTOS")
            self.wait_step("Click en APODERAMIENTOS")
            
            # Click en pestaña Descargas Zip
            print("👆 Haciendo click en 'Descargas Zip'...")
            self.page.wait_for_selector("button[role='tab']:has-text('Descargas Zip')", timeout=15000)
            self.page.click("button[role='tab']:has-text('Descargas Zip')")
            self.wait_step("Click en Descargas Zip")
            
            # Esperar a que cargue la tabla
            print("⏳ Esperando tabla de descargas...")
            self.page.wait_for_selector("table", timeout=15000)
            
            print("✅ NAVEGACIÓN COMPLETADA!")
            self.wait_step("Tabla de descargas lista")
            
        except Exception as e:
            print(f"❌ Error navegando a descargas: {e}")
            raise
    
    def get_download_buttons(self):
        """Encontrar SOLO el botón de descarga de la fila 1"""
        try:
            print("\n🔍 PASO 4: Buscando archivo en FILA 1 para descargar...")
            
            # Buscar todas las filas de la tabla (excepto header)
            rows = self.page.query_selector_all("table tr")[1:]  # Saltar header
            
            download_buttons = []
            
            # SOLO PROCESAR LA FILA 1 (índice 0)
            if len(rows) > 0:
                row = rows[0]  # SOLO LA PRIMERA FILA
                try:
                    cells = row.query_selector_all("td")
                    
                    if len(cells) >= 7:
                        # Obtener información de la fila 1
                        nombre = cells[1].inner_text().strip() if len(cells) > 1 else ""
                        fecha = cells[3].inner_text().strip() if len(cells) > 3 else ""
                        estado = cells[6].inner_text().strip() if len(cells) > 6 else ""
                        
                        # Buscar botón de descarga en la última columna
                        last_cell = cells[-1]
                        download_button = last_cell.query_selector("span.cursor-pointer, span:has-text('📂'), *[class*='cursor-pointer']")
                        
                        if download_button:
                            download_info = {
                                'nombre': nombre,
                                'fecha': fecha,
                                'estado': estado,
                                'button': download_button,
                                'row_index': 0
                            }
                            download_buttons.append(download_info)
                            print(f"✅ FILA 1 ENCONTRADA: {nombre} - {fecha} - Estado: {estado}")
                        else:
                            print("⚠️  No se encontró botón de descarga en la fila 1")
                        
                except Exception as e:
                    print(f"❌ Error procesando fila 1: {e}")
            
            print(f"🎯 ENCONTRADOS {len(download_buttons)} archivos para descargar")
            self.wait_step("Botones de descarga identificados")
            
            return download_buttons
            
        except Exception as e:
            print(f"❌ Error buscando botones: {e}")
            return []
    
    def download_files(self, download_buttons):
        """Descargar SOLO el archivo de la fila 1"""
        try:
            if not download_buttons:
                print("❌ No hay archivos para descargar")
                return
                
            print(f"\n⬇️  PASO 5: Descargando archivo de la FILA 1...")
            
            # Solo descargar el primer (y único) archivo
            download_info = download_buttons[0]
            
            try:
                print(f"\n📥 Descargando archivo: {download_info['nombre']}")
                print(f"📅 Fecha: {download_info['fecha']}")
                print(f"📊 Estado: {download_info['estado']}")
                
                # Scroll al botón
                download_info['button'].scroll_into_view_if_needed()
                
                # Wait especial de 2 segundos antes de hacer click en descarga
                self.wait_download("Preparando click en descarga")
                
                # Configurar listener para descarga
                with self.page.expect_download() as download_info_promise:
                    download_info['button'].click()
                    print("👆 Click realizado en FILA 1, esperando descarga...")
                
                # Esperar descarga
                download = download_info_promise.value
                
                # Guardar archivo temporalmente
                temp_filename = download.suggested_filename or f"temp_fila1.zip"
                temp_filepath = os.path.join(self.download_path, temp_filename)
                download.save_as(temp_filepath)
                
                print(f"✅ DESCARGA COMPLETADA: {temp_filename}")
                
                # Crear ZIP con contraseña
                fecha_hoy = datetime.now().strftime("%Y%m%d")
                protected_zip_name = f"ApudActa_{fecha_hoy}_Protegido.7z"
                protected_filepath = self.create_password_protected_zip(temp_filepath, protected_zip_name)
                
                if protected_filepath:
                    print(f"� ARCHIVO FINAL PROTEGIDO: {protected_zip_name}")
                    print(f"🔑 CONTRASEÑA: {self.archive_password}")
                    
                    # Actualizar filepath para el email
                    filepath = protected_filepath
                    filename = protected_zip_name
                else:
                    print("⚠️  Usando archivo sin protección por error")
                    filepath = temp_filepath
                    filename = temp_filename
                
                print(f"📁 Archivo final: {filepath}")
                
                self.wait_step("Descarga de FILA 1 completada")
                
            except Exception as e:
                print(f"❌ Error descargando archivo de fila 1: {e}")
                return
            
            print(f"\n🎉 PROCESO COMPLETADO: Archivo de FILA 1 descargado exitosamente")
            
        except Exception as e:
            print(f"❌ Error en proceso de descarga: {e}")
    
    def run_complete_process(self):
        """Ejecutar todo el proceso paso a paso"""
        try:
            print("🎯 INICIANDO PROCESO COMPLETO PASO A PASO")
            print("=" * 50)
            
            # Paso 1: Configurar navegador
            self.setup_browser()
            
            # Paso 2: Login
            self.login()
            
            # Paso 3: Navegar a descargas
            self.navigate_to_downloads()
            
            # Paso 4: Encontrar botones de descarga
            download_buttons = self.get_download_buttons()
            
            if not download_buttons:
                print("⚠️  No se encontraron archivos para descargar")
                return
            
            # Paso 5: Descargar archivos
            self.download_files(download_buttons)
            
            print("\n🎉 PROCESO COMPLETADO EXITOSAMENTE!")
            print(f"📁 Revisa la carpeta: {self.download_path}")
            
        except Exception as e:
            print(f"❌ Error en proceso completo: {e}")
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cerrar navegador"""
        try:
            if self.browser:
                print("\n🔒 Cerrando navegador...")
                self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()
        except:
            pass


# FUNCIÓN PRINCIPAL PARA EJECUTAR EL SCRAPER
def main():
    """Función principal para ejecutar el scraper"""
    try:
        print("🌟 EJECUTANDO EASYDAY SCRAPER CON PLAYWRIGHT")
        print("=" * 60)
        print("⚡ MODO SÚPER SIMPLIFICADO")
        print("� MODO HEADLESS (sin ventana visible)")
        print("⏰ WAITS DE 0.5 SEGUNDOS ENTRE PASOS")
        print("⏰ WAIT DE 2 SEGUNDOS SOLO PARA DESCARGA")
        print("🎯 SIN TENSORFLOW NI COMPLEJIDADES")
        print("🎯 DESCARGA SOLO EL ARCHIVO DE LA FILA 1")
        print("=" * 60)
        
        # Crear y ejecutar scraper
        scraper = EasyDayScraper()
        scraper.run_complete_process()
        
    except KeyboardInterrupt:
        print("\n⏹️  PROCESO CANCELADO POR USUARIO")
    except Exception as e:
        print(f"\n❌ ERROR EN PROCESO PRINCIPAL: {e}")
    finally:
        print("\n👋 EASYDAY SCRAPER FINALIZADO")


if __name__ == "__main__":
    main()
