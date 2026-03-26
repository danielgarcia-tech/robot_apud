"""
EASYDAY - Scraper con procesamiento PDF integrado
Descarga, procesa PDFs (extrae identificadores y renombra) y comprime
"""

import os
import time
import json
import shutil
import tempfile
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import zipfile
import py7zr
import fitz  # PyMuPDF para procesamiento PDF

# Cargar variables de entorno
load_dotenv()

class EasyDayScraper:
    """Scraper con procesamiento PDF integrado"""
    
    def __init__(self):
        self.email = os.getenv('EMAIL', 'jesusoroza@ruaabogados.es')
        self.password = os.getenv('PASSWORD', 'Ruaabogados2024')
        self.download_path = os.path.abspath('./descargas')
        self.processed_path = os.path.abspath('./procesados')
        
        # CONFIGURACIÓN SÚPER SIMPLE
        self.wait_between_steps = 0.5  # 0.5 segundos entre pasos (rápido)
        self.download_wait = 2  # 2 segundos para el paso de descarga
        self.login_url = 'https://app.apudacta.com/login/'
        
        # CONFIGURACIÓN DE SEGURIDAD PARA ARCHIVOS COMPRIMIDOS
        self.archive_password = 'Rua2025'  # 🔐 Contraseña para archivos 7Z
        
        # Crear carpetas necesarias
        Path(self.download_path).mkdir(parents=True, exist_ok=True)
        Path(self.processed_path).mkdir(parents=True, exist_ok=True)
        
        # Variables para procesamiento PDF
        self.processing_results = []
        self.renamed_files = []
        
        # Variables de estado
        self.page = None
        self.browser = None
        self.context = None
        
        print("🚀 EASYDAY SCRAPER CON PROCESAMIENTO PDF INICIADO")
        print(f"📁 Descargas en: {self.download_path}")
        print(f"📁 Procesados en: {self.processed_path}")
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
            
            # NO ELIMINAR archivo original aquí - se eliminará después del procesamiento PDF
            print(f"� Archivo original preservado para procesamiento PDF")
            
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
            
            # Crear navegador en modo visible (DEBUG)
            self.browser = self.playwright.chromium.launch(
                headless=True,  # MODO VISIBLE PARA DEBUG
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
            
            # Esperar a que aparezcan los campos de fecha
            print("⏳ Esperando campos de fecha...")
            self.page.wait_for_selector("input[name='date-from']", timeout=15000)
            self.page.wait_for_selector("input[name='date-to']", timeout=15000)
            self.wait_step("Campos de fecha encontrados")
            
            # Llenar fecha desde (hoy - 30 días)
            print("📅 Llenando fecha desde...")
            fecha_desde = (datetime.now() - __import__('datetime').timedelta(days=30)).strftime("%Y-%m-%d")
            self.page.fill("input[name='date-from']", fecha_desde)
            self.wait_step(f"Fecha desde: {fecha_desde}")
            
            # Llenar fecha hasta (hoy)
            print("📅 Llenando fecha hasta...")
            fecha_hasta = datetime.now().strftime("%Y-%m-%d")
            self.page.fill("input[name='date-to']", fecha_hasta)
            self.wait_step(f"Fecha hasta: {fecha_hasta}")
            
            # Hacer click en botón Buscar
            print("👆 Haciendo click en botón 'Buscar'...")
            self.page.wait_for_selector("button.bg-sky-600.text-white", timeout=15000)
            self.page.click("button.bg-sky-600.text-white")
            self.wait_step("Click en Buscar")
            
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
                
                # RETORNAR EL ARCHIVO ORIGINAL PARA PROCESAMIENTO
                return [temp_filepath]
                
            except Exception as e:
                print(f"❌ Error descargando archivo de fila 1: {e}")
                return []
            
            print(f"\n🎉 PROCESO COMPLETADO: Archivo de FILA 1 descargado exitosamente")
            
        except Exception as e:
            print(f"❌ Error en proceso de descarga: {e}")
            return []
    
    def run_complete_process(self):
        """Ejecutar todo el proceso paso a paso con procesamiento PDF"""
        try:
            print("🎯 INICIANDO PROCESO COMPLETO CON PROCESAMIENTO PDF")
            print("=" * 60)
            
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
            downloaded_files = self.download_files(download_buttons)
            
            # Paso 6: Procesar PDFs de archivos descargados
            organized_folders = []
            if downloaded_files:
                for downloaded_file in downloaded_files:
                    if downloaded_file and os.path.exists(downloaded_file):
                        print(f"\n🔍 PASO 6: Procesando ZIP descargado...")
                        organized_folder = self.procesar_zip_descargado(downloaded_file)
                        if organized_folder:
                            print("✅ Procesamiento y organización completados")
                            organized_folders.append(organized_folder)
                        else:
                            print("⚠️ Error en procesamiento PDF, continuando...")
                        
                        # Limpiar archivo original después del procesamiento
                        try:
                            os.remove(downloaded_file)
                            print(f"🗑️ Archivo original eliminado: {os.path.basename(downloaded_file)}")
                        except:
                            print(f"⚠️ No se pudo eliminar archivo original")
                
                # Paso 7: Crear archivo 7Z final con archivos organizados
                if organized_folders:
                    # Usar la primera carpeta organizada (normalmente solo habrá una)
                    final_7z = self.crear_7z_final(organized_folders[0])
                else:
                    # Fallback al método original si no hay carpetas organizadas
                    final_7z = self.crear_7z_final()
                
                if final_7z:
                    print(f"\n🎉 PROCESO COMPLETADO EXITOSAMENTE!")
                    print(f"📁 Archivo final: {final_7z}")
                    print(f"📁 Archivos organizados en: {organized_folders[0] if organized_folders else self.processed_path}")
                    
                    # Limpiar archivos temporales manteniendo solo el 7Z
                    self.limpiar_archivos_temporales(final_7z, organized_folders)
                else:
                    print("\n⚠️ Proceso completado pero sin archivo final 7Z")
            else:
                print("❌ No se descargaron archivos para procesar")
            
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

    def limpiar_archivos_temporales(self, final_7z_path, organized_folders):
        """
        Elimina todos los archivos y carpetas temporales, manteniendo solo el archivo 7Z final
        """
        import shutil
        
        print("\n🧹 Iniciando limpieza de archivos temporales...")
        
        try:
            # COPIAR REPORTE JSON A LA RAÍZ ANTES DE ELIMINAR
            print("📋 Buscando reporte JSON para copiar a raíz...")
            for folder_path in organized_folders:
                if os.path.exists(folder_path):
                    for file in os.listdir(folder_path):
                        if file.startswith("reporte_procesamiento_") and file.endswith(".json"):
                            json_src = os.path.join(folder_path, file)
                            json_dst = file  # Copiar a la raíz con el mismo nombre
                            try:
                                import shutil as shutil_copy
                                shutil_copy.copy2(json_src, json_dst)
                                print(f"   ✅ Reporte JSON copiado a raíz: {file}")
                            except Exception as e:
                                print(f"   ❌ Error copiando JSON: {e}")
            
            # El archivo 7Z final está en el directorio raíz
            final_7z_name = os.path.basename(final_7z_path) if final_7z_path else ""
            
            eliminados = 0
            errores = 0
            
            # 1. Limpiar directorio raíz (excepto el 7Z final y el JSON)
            elementos_raiz = []
            if os.path.exists("."):
                elementos_raiz = [f for f in os.listdir(".") if os.path.isfile(f)]
            
            for archivo in elementos_raiz:
                # Conservar el archivo 7Z final y el reporte JSON
                if archivo == final_7z_name:
                    print(f"   ✅ Conservando: {archivo}")
                    continue
                if archivo.startswith("reporte_procesamiento_") and archivo.endswith(".json"):
                    print(f"   ✅ Conservando: {archivo}")
                    continue
                    
                # Eliminar otros archivos temporales (PDFs, etc.)
                if archivo.endswith(('.pdf', '.zip', '.7z')) or 'solicitud' in archivo.lower() or 'poder' in archivo.lower():
                    try:
                        os.remove(archivo)
                        print(f"   🗑️ Eliminado archivo: {archivo}")
                        eliminados += 1
                    except Exception as e:
                        print(f"   ❌ Error eliminando {archivo}: {e}")
                        errores += 1
            
            # 2. Limpiar carpetas organizadas
            for folder_path in organized_folders:
                try:
                    if os.path.exists(folder_path):
                        shutil.rmtree(folder_path)
                        print(f"   📁🗑️ Eliminada carpeta: {os.path.basename(folder_path)}")
                        eliminados += 1
                except Exception as e:
                    print(f"   ❌ Error eliminando carpeta {folder_path}: {e}")
                    errores += 1
            
            # 3. Limpiar carpeta de procesados completa
            if os.path.exists(self.processed_path):
                try:
                    shutil.rmtree(self.processed_path)
                    print(f"   📁🗑️ Eliminada carpeta: {os.path.basename(self.processed_path)}")
                    eliminados += 1
                except Exception as e:
                    print(f"   ❌ Error eliminando carpeta procesados: {e}")
                    errores += 1
            
            print(f"\n🧹 Limpieza completada:")
            print(f"   ✅ Elementos eliminados: {eliminados}")
            if errores > 0:
                print(f"   ❌ Errores: {errores}")
            if final_7z_name:
                print(f"   📦 Archivo final conservado: {final_7z_name}")
            
        except Exception as e:
            print(f"❌ Error en limpieza general: {e}")

    # === MÉTODOS DE PROCESAMIENTO PDF (de pdf_processor_renamer.py) ===
    
    def extract_text_from_pdf(self, pdf_path):
        """Extraer texto del PDF y detectar si tiene OCR"""
        text = ""
        has_ocr = False
        
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    page_text = page.get_text()
                    text += page_text
                    
                    # Verificar si la página tiene texto extraíble (OCR)
                    if page_text.strip():
                        has_ocr = True
            
            return text, has_ocr
        except Exception as e:
            print(f"❌ Error extrayendo texto de {pdf_path}: {e}")
            return "", False

    def buscar_identificadores(self, text):
        """Buscar DNI/NIF/NIE en texto"""
        dni_nif_pattern = r"\b\d{7,8}[A-Z]\b"
        nie_pattern = r"\b[XYZ]\d{7}[A-Z]\b"
        
        resultados = []
        
        for match in re.finditer(f"{nie_pattern}|{dni_nif_pattern}", text):
            secuencia = match.group()
            tipo = "NIE" if re.match(nie_pattern, secuencia) else "DNI/NIF"
            
            # Buscar lo que viene después (20 caracteres siguientes)
            start_pos = match.end()
            secuencia_post = text[start_pos:start_pos+20].strip()
            resultados.append((tipo, secuencia, secuencia_post))
            
        return resultados

    def extraer_cliente_fecha(self, nombre_archivo):
        """Extraer información de cliente y fecha del nombre"""
        # Busca patrón: _DNI_CLIENTE_FECHA.pdf
        patron = r'_(\w{7,9}[A-Z])_([A-ZÁÉÍÓÚÑa-záéíóúñ\-\s]+)_((?:\d{4}-\d{2}-\d{2})_\d{2}:\d{2}:\d{2})'
        m = re.search(patron, nombre_archivo)
        if m:
            cliente = m.group(2).replace('_', ' ').strip()
            fecha = m.group(3).replace('_', ' ')
            return cliente, fecha
        
        # Alternativa: buscar última fecha tipo yyyy-mm-dd en el nombre
        fecha_alt = re.findall(r'(\d{4}-\d{2}-\d{2})', nombre_archivo)
        fecha = fecha_alt[-1] if fecha_alt else ''
        return '', fecha

    def generar_nuevo_nombre(self, identificadores, archivo_original):
        """Generar nuevo nombre basado en identificadores encontrados y tipo de archivo"""
        if not identificadores:
            return None
        
        # Usar el primer identificador encontrado
        tipo, secuencia, post = identificadores[0]
        
        # Determinar prefijo según el tipo de archivo
        if "certificadoregistro" in archivo_original.lower():
            # CertificadoRegistro → PODER_
            prefijo = "PODER"
        elif "solicitud_apudacta" in archivo_original.lower():
            # Solicitud_ApudActa → SOLICITUD_
            prefijo = "SOLICITUD"
        else:
            # Por defecto usar PODER para compatibilidad
            prefijo = "PODER"
        
        nuevo_nombre = f"{prefijo}_{secuencia}.pdf"
        return nuevo_nombre

    def verificar_archivo_existe(self, nuevo_path):
        """Verificar si el archivo ya existe y generar nombre alternativo"""
        if not os.path.exists(nuevo_path):
            return nuevo_path
        
        # Si existe, agregar contador
        base_path = os.path.dirname(nuevo_path)
        base_name = os.path.splitext(os.path.basename(nuevo_path))[0]
        ext = os.path.splitext(nuevo_path)[1]
        
        counter = 1
        while True:
            nuevo_nombre = f"{base_name}_{counter}{ext}"
            nuevo_path = os.path.join(base_path, nuevo_nombre)
            if not os.path.exists(nuevo_path):
                return nuevo_path
            counter += 1

    def procesar_pdf_individual(self, pdf_path, archivo_original):
        """Procesar un PDF individual y renombrarlo si es posible"""
        try:
            print(f"   📄 Procesando: {archivo_original}")
            
            # Extraer texto y verificar OCR
            text, has_ocr = self.extract_text_from_pdf(pdf_path)
            
            # Buscar identificadores
            identificadores = self.buscar_identificadores(text)
            
            # Extraer información de cliente y fecha del nombre original
            cliente, fecha = self.extraer_cliente_fecha(archivo_original)
            
            # Información básica del archivo
            file_size = os.path.getsize(pdf_path)
            
            resultado = {
                "archivo_original": archivo_original,
                "archivo_nuevo": archivo_original,  # Por defecto, mantener nombre original
                "tipo": "NO ENCONTRADO",
                "secuencia": "",
                "secuencia_post": "",
                "estado": "Sin identificadores",
                "export_path": "",
                "tiene_ocr": "Sí" if has_ocr else "No",
                "cliente": cliente,
                "fecha": fecha,
                "tamaño_bytes": file_size,
                "identificadores_encontrados": len(identificadores),
                "procesado_en": datetime.now().isoformat()
            }
            
            if identificadores:
                # Generar nuevo nombre basado en identificadores
                nuevo_nombre = self.generar_nuevo_nombre(identificadores, archivo_original)
                
                if nuevo_nombre:
                    # Verificar si ya existe un archivo con ese nombre en la carpeta de destino
                    nuevo_path_destino = os.path.join(self.processed_path, nuevo_nombre)
                    nuevo_path_final = self.verificar_archivo_existe(nuevo_path_destino)
                    nuevo_nombre_final = os.path.basename(nuevo_path_final)
                    
                    # Copiar archivo con nuevo nombre
                    shutil.copy2(pdf_path, nuevo_path_final)
                    
                    tipo, secuencia, post = identificadores[0]
                    resultado.update({
                        "archivo_nuevo": nuevo_nombre_final,
                        "tipo": tipo,
                        "secuencia": secuencia,
                        "secuencia_post": post,
                        "estado": "Procesado y renombrado",
                        "export_path": nuevo_path_final
                    })
                    
                    self.renamed_files.append({
                        "original": archivo_original,
                        "nuevo": nuevo_nombre_final,
                        "path": nuevo_path_final,
                        "identificador": secuencia
                    })
                    
                    print(f"      ✅ Renombrado a: {nuevo_nombre_final}")
                    print(f"      🆔 Identificador: {secuencia} ({tipo})")
            else:
                # Sin identificadores, copiar con nombre original
                destino_original = os.path.join(self.processed_path, archivo_original)
                destino_final = self.verificar_archivo_existe(destino_original)
                shutil.copy2(pdf_path, destino_final)
                
                resultado.update({
                    "archivo_nuevo": os.path.basename(destino_final),
                    "estado": "Sin identificadores - Copiado con nombre original",
                    "export_path": destino_final
                })
                
                print(f"      ℹ️ Sin identificadores, copiado como: {os.path.basename(destino_final)}")
            
            if has_ocr:
                print(f"      🔍 OCR: Detectado")
            else:
                print(f"      ❌ OCR: No detectado")
            
            self.processing_results.append(resultado)
            return resultado
            
        except Exception as e:
            print(f"      ❌ Error procesando {archivo_original}: {e}")
            
            resultado_error = {
                "archivo_original": archivo_original,
                "archivo_nuevo": archivo_original,
                "tipo": "ERROR",
                "secuencia": "",
                "secuencia_post": "",
                "estado": f"Error: {str(e)}",
                "export_path": "Error en exportación",
                "tiene_ocr": "No se pudo verificar",
                "cliente": "",
                "fecha": "",
                "procesado_en": datetime.now().isoformat()
            }
            
            self.processing_results.append(resultado_error)
            return resultado_error

    def procesar_zip_descargado(self, zip_path):
        """Procesar el ZIP descargado separando archivos por tipo y procesando PDFs"""
        print(f"\n🔍 PASO 6: Procesando y organizando archivos descargados...")
        print(f"📦 Archivo: {os.path.basename(zip_path)}")
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Extraer ZIP
            print("📂 Extrayendo archivo ZIP...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Crear estructura de carpetas organizadas
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            organized_folder = os.path.join(self.processed_path, f"apudacta_organizado_{timestamp}")
            
            poderes_folder = os.path.join(organized_folder, "PODERES")
            solicitudes_folder = os.path.join(organized_folder, "SOLICITUDES")
            
            # Crear carpetas
            os.makedirs(poderes_folder, exist_ok=True)
            os.makedirs(solicitudes_folder, exist_ok=True)
            
            print("📁 Estructura de carpetas creada:")
            print(f"   🗂️ PODERES: {poderes_folder}")
            print(f"   🗂️ SOLICITUDES: {solicitudes_folder}")
            print(f"   📋 Excel directo en: {organized_folder}")
            
            # Separar y procesar archivos
            certificados_encontrados = []
            solicitudes_encontradas = []
            excel_solicitudes = []
            otros_archivos = []
            
            # Analizar todos los archivos extraídos
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    file_lower = file.lower()
                    
                    if "certificadoregistro" in file_lower and file_lower.endswith('.pdf'):
                        certificados_encontrados.append((full_path, file))
                    elif "solicitud_apudacta" in file_lower and file_lower.endswith('.pdf'):
                        solicitudes_encontradas.append((full_path, file))
                    elif "solicitudes" in file_lower and file_lower.endswith('.xlsx'):
                        excel_solicitudes.append((full_path, file))
                    else:
                        otros_archivos.append((full_path, file))
            
            print(f"\n📊 ANÁLISIS DE ARCHIVOS:")
            print(f"   📜 CertificadoRegistro: {len(certificados_encontrados)}")
            print(f"   📝 Solicitud_ApudActa: {len(solicitudes_encontradas)}")
            print(f"   📊 Excel Solicitudes: {len(excel_solicitudes)}")
            print(f"   ❓ Otros archivos: {len(otros_archivos)}")
            
            # Limpiar resultados previos
            self.processing_results = []
            self.renamed_files = []
            
            # PROCESAR CERTIFICADOS (van a PODERES)
            if certificados_encontrados:
                print(f"\n🏛️ PROCESANDO CERTIFICADOS → PODERES")
                for i, (pdf_path, pdf_name) in enumerate(certificados_encontrados, 1):
                    print(f"\n[PODER {i}/{len(certificados_encontrados)}]", end=" ")
                    resultado = self.procesar_pdf_individual(pdf_path, pdf_name)
                    
                    # Copiar archivo procesado a carpeta PODERES
                    if resultado and resultado.get('export_path'):
                        # Si fue renombrado, usar el nuevo nombre
                        archivo_destino = os.path.join(poderes_folder, resultado.get('archivo_nuevo', pdf_name))
                    else:
                        # Si no fue renombrado, usar nombre original
                        archivo_destino = os.path.join(poderes_folder, pdf_name)
                    
                    # Verificar que no exista duplicado
                    if os.path.exists(archivo_destino):
                        base, ext = os.path.splitext(archivo_destino)
                        contador = 1
                        while os.path.exists(f"{base}_{contador}{ext}"):
                            contador += 1
                        archivo_destino = f"{base}_{contador}{ext}"
                    
                    shutil.copy2(pdf_path, archivo_destino)
                    print(f"✅ → {os.path.basename(archivo_destino)}")
            
            # PROCESAR SOLICITUDES (van a SOLICITUDES)
            if solicitudes_encontradas:
                print(f"\n📋 PROCESANDO SOLICITUDES → SOLICITUDES")
                for i, (pdf_path, pdf_name) in enumerate(solicitudes_encontradas, 1):
                    print(f"\n[SOLICITUD {i}/{len(solicitudes_encontradas)}]", end=" ")
                    resultado = self.procesar_pdf_individual(pdf_path, pdf_name)
                    
                    # Copiar archivo procesado a carpeta SOLICITUDES
                    if resultado and resultado.get('export_path'):
                        # Si fue renombrado, usar el nuevo nombre
                        archivo_destino = os.path.join(solicitudes_folder, resultado.get('archivo_nuevo', pdf_name))
                    else:
                        # Si no fue renombrado, usar nombre original
                        archivo_destino = os.path.join(solicitudes_folder, pdf_name)
                    
                    # Verificar que no exista duplicado
                    if os.path.exists(archivo_destino):
                        base, ext = os.path.splitext(archivo_destino)
                        contador = 1
                        while os.path.exists(f"{base}_{contador}{ext}"):
                            contador += 1
                        archivo_destino = f"{base}_{contador}{ext}"
                    
                    shutil.copy2(pdf_path, archivo_destino)
                    print(f"✅ → {os.path.basename(archivo_destino)}")
            
            # COPIAR EXCEL SOLICITUDES (directamente en la raíz)
            if excel_solicitudes:
                print(f"\n📊 COPIANDO EXCEL SOLICITUDES → RAÍZ")
                for excel_path, excel_name in excel_solicitudes:
                    archivo_destino = os.path.join(organized_folder, excel_name)
                    
                    # Verificar que no exista duplicado
                    if os.path.exists(archivo_destino):
                        base, ext = os.path.splitext(archivo_destino)
                        contador = 1
                        while os.path.exists(f"{base}_{contador}{ext}"):
                            contador += 1
                        archivo_destino = f"{base}_{contador}{ext}"
                    
                    shutil.copy2(excel_path, archivo_destino)
                    print(f"✅ Excel copiado: {os.path.basename(archivo_destino)}")
            
            # PROCESAR OTROS ARCHIVOS (si los hay)
            if otros_archivos:
                print(f"\n❓ PROCESANDO OTROS ARCHIVOS")
                otros_folder = os.path.join(organized_folder, "OTROS")
                os.makedirs(otros_folder, exist_ok=True)
                
                for other_path, other_name in otros_archivos:
                    archivo_destino = os.path.join(otros_folder, other_name)
                    
                    # Si es PDF, procesarlo también
                    if other_name.lower().endswith('.pdf'):
                        resultado = self.procesar_pdf_individual(other_path, other_name)
                        if resultado and resultado.get('export_path'):
                            archivo_destino = os.path.join(otros_folder, resultado.get('archivo_nuevo', other_name))
                    
                    # Verificar duplicados
                    if os.path.exists(archivo_destino):
                        base, ext = os.path.splitext(archivo_destino)
                        contador = 1
                        while os.path.exists(f"{base}_{contador}{ext}"):
                            contador += 1
                        archivo_destino = f"{base}_{contador}{ext}"
                    
                    shutil.copy2(other_path, archivo_destino)
                    print(f"✅ Otro archivo: {os.path.basename(archivo_destino)}")
            
            # Generar reporte con información de organización
            self.generar_reporte_procesamiento_organizado(organized_folder, certificados_encontrados, solicitudes_encontradas, excel_solicitudes, otros_archivos)
            
            # Mostrar resumen final
            print(f"\n🎉 PROCESAMIENTO Y ORGANIZACIÓN COMPLETADA")
            print(f"📁 Carpeta organizada: {organized_folder}")
            print(f"   🏛️ PODERES: {len(certificados_encontrados)} archivos")
            print(f"   📋 SOLICITUDES: {len(solicitudes_encontradas)} archivos") 
            print(f"   📊 EXCEL: {len(excel_solicitudes)} archivos")
            if otros_archivos:
                print(f"   ❓ OTROS: {len(otros_archivos)} archivos")
            
            return organized_folder  # Retornar la carpeta organizada
            
        except Exception as e:
            print(f"❌ Error procesando ZIP: {e}")
            return False
        
        finally:
            # Limpiar directorio temporal
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def generar_reporte_procesamiento_organizado(self, organized_folder, certificados, solicitudes, excel_files, otros):
        """Generar reporte del procesamiento PDF con información de organización"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(organized_folder, f"reporte_procesamiento_{timestamp}.json")
        
        # Generar estadísticas
        total_archivos = len(self.processing_results)
        archivos_renombrados = len(self.renamed_files)
        archivos_con_ocr = sum(1 for r in self.processing_results if r.get('tiene_ocr') == 'Sí')
        archivos_con_identificadores = sum(1 for r in self.processing_results if r.get('identificadores_encontrados', 0) > 0)
        total_identificadores = sum(r.get('identificadores_encontrados', 0) for r in self.processing_results)
        cantidad_poderes = len(certificados)  # Cantidad de poderes obtenidos
        
        reporte = {
            "resumen": {
                "fecha_procesamiento": datetime.now().isoformat(),
                "carpeta_organizada": organized_folder,
                "total_archivos_procesados": total_archivos,
                "cantidad_poderes_obtenidos": cantidad_poderes,
                "archivos_renombrados": archivos_renombrados,
                "archivos_con_ocr": archivos_con_ocr,
                "archivos_con_identificadores": archivos_con_identificadores,
                "total_identificadores_encontrados": total_identificadores
            },
            "organizacion": {
                "poderes_certificados": {
                    "cantidad": len(certificados),
                    "archivos": [nombre for _, nombre in certificados]
                },
                "solicitudes_apudacta": {
                    "cantidad": len(solicitudes),
                    "archivos": [nombre for _, nombre in solicitudes]
                },
                "excel_solicitudes": {
                    "cantidad": len(excel_files),
                    "archivos": [nombre for _, nombre in excel_files]
                },
                "otros_archivos": {
                    "cantidad": len(otros),
                    "archivos": [nombre for _, nombre in otros]
                }
            },
            "archivos_renombrados": self.renamed_files,
            "detalle_procesamiento": self.processing_results
        }
        
        # Guardar reporte
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 REPORTE DE PROCESAMIENTO ORGANIZADO:")
        print(f"   📁 Total archivos procesados: {total_archivos}")
        print(f"   🏛️ PODERES OBTENIDOS: {cantidad_poderes}")
        print(f"   📋 Solicitudes procesadas: {len(solicitudes)}")
        print(f"   🔄 Archivos renombrados: {archivos_renombrados}")
        print(f"   🔍 Con OCR: {archivos_con_ocr}")
        print(f"   🆔 Con identificadores: {archivos_con_identificadores}")
        print(f"   📈 Total identificadores: {total_identificadores}")
        print(f"   💾 Reporte guardado en: {report_file}")
        
        return report_file

    def generar_reporte_procesamiento(self):
        """Generar reporte del procesamiento PDF"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.processed_path, f"reporte_procesamiento_{timestamp}.json")
        
        # Generar estadísticas
        total_archivos = len(self.processing_results)
        archivos_renombrados = len(self.renamed_files)
        archivos_con_ocr = sum(1 for r in self.processing_results if r.get('tiene_ocr') == 'Sí')
        archivos_con_identificadores = sum(1 for r in self.processing_results if r.get('identificadores_encontrados', 0) > 0)
        total_identificadores = sum(r.get('identificadores_encontrados', 0) for r in self.processing_results)
        cantidad_poderes = sum(1 for r in self.processing_results if 'PODER_' in r.get('archivo_nuevo', ''))
        
        reporte = {
            "resumen": {
                "fecha_procesamiento": datetime.now().isoformat(),
                "carpeta_salida": self.processed_path,
                "total_archivos": total_archivos,
                "cantidad_poderes_obtenidos": cantidad_poderes,
                "archivos_renombrados": archivos_renombrados,
                "archivos_con_ocr": archivos_con_ocr,
                "archivos_con_identificadores": archivos_con_identificadores,
                "total_identificadores_encontrados": total_identificadores
            },
            "archivos_renombrados": self.renamed_files,
            "detalle_procesamiento": self.processing_results
        }
        
        # Guardar reporte
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 REPORTE DE PROCESAMIENTO:")
        print(f"   📁 Total archivos procesados: {total_archivos}")
        print(f"   🏛️ PODERES OBTENIDOS: {cantidad_poderes}")
        print(f"   🔄 Archivos renombrados: {archivos_renombrados}")
        print(f"   🔍 Con OCR: {archivos_con_ocr}")
        print(f"   🆔 Con identificadores: {archivos_con_identificadores}")
        print(f"   📈 Total identificadores: {total_identificadores}")
        print(f"   💾 Reporte guardado en: {report_file}")
        
        return report_file

    def crear_7z_final(self, organized_folder=None):
        """Crear archivo 7Z final con archivos organizados y procesados"""
        print(f"\n📦 PASO 7: Creando archivo 7Z final...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # CREAR EL 7Z EN EL DIRECTORIO RAÍZ PARA QUE SEA ENCONTRADO POR GITHUB ACTIONS
        output_7z = f"apudacta_procesado_{timestamp}.7z"
        
        try:
            if organized_folder and os.path.exists(organized_folder):
                # Comprimir toda la carpeta organizada manteniendo estructura
                print(f"📁 Comprimiendo carpeta organizada: {os.path.basename(organized_folder)}")
                print(f"🗂️ Creando estructura en ZIP:")
                
                with py7zr.SevenZipFile(output_7z, 'w', password=self.archive_password) as archive:
                    # Agregar toda la estructura de carpetas organizadas
                    for root, dirs, files in os.walk(organized_folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Mantener la estructura de carpetas relativa
                            arcname = os.path.relpath(file_path, organized_folder)
                            archive.write(file_path, arcname)
                            
                            # Mostrar qué se está agregando
                            if "PODERES" in arcname:
                                print(f"   🏛️ PODERES/{os.path.basename(file)}")
                            elif "SOLICITUDES" in arcname:
                                print(f"   📋 SOLICITUDES/{os.path.basename(file)}")
                            elif "OTROS" in arcname:
                                print(f"   ❓ OTROS/{os.path.basename(file)}")
                            else:
                                print(f"   📄 {os.path.basename(file)}")
                
                print(f"✅ Estructura completa comprimida:")
                print(f"   🏛️ PODERES/")
                print(f"   📋 SOLICITUDES/") 
                print(f"   📊 Excel Solicitudes")
                print(f"   📝 Reporte de procesamiento")
                
            else:
                # Método original: buscar archivos en la carpeta de procesados
                files_to_compress = []
                for file in os.listdir(self.processed_path):
                    file_path = os.path.join(self.processed_path, file)
                    if os.path.isfile(file_path) and not file.endswith('.7z'):
                        files_to_compress.append(file_path)
                
                if not files_to_compress:
                    print("⚠️ No hay archivos procesados para comprimir")
                    return None
                
                print(f"📁 Comprimiendo {len(files_to_compress)} archivos...")
                
                with py7zr.SevenZipFile(output_7z, 'w', password=self.archive_password) as archive:
                    for file_path in files_to_compress:
                        archive.write(file_path, os.path.basename(file_path))
            
            print(f"✅ Archivo 7Z creado: {os.path.basename(output_7z)}")
            print(f"🔐 Protegido con contraseña: {self.archive_password}")
            
            return output_7z
            
        except Exception as e:
            print(f"❌ Error creando archivo 7Z: {e}")
            return None


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


def test_processing_only():
    """Función de prueba para procesar archivos existentes sin scraping"""
    print("🧪 MODO PRUEBA - SOLO PROCESAMIENTO")
    print("="*60)
    
    try:
        # Crear instancia del scraper
        scraper = EasyDayScraper()
        
        # Buscar archivos ZIP en downloads
        downloads_folder = "downloads"
        if not os.path.exists(downloads_folder):
            print("❌ No existe la carpeta downloads")
            return False
        
        zip_files = [f for f in os.listdir(downloads_folder) 
                    if f.lower().endswith('.zip')]
        
        if not zip_files:
            print("❌ No hay archivos ZIP en la carpeta downloads")
            print("💡 Ejecuta crear_zip_prueba.py primero")
            return False
        
        print(f"📦 Archivos ZIP encontrados: {len(zip_files)}")
        for i, zip_file in enumerate(zip_files, 1):
            print(f"   {i}. {zip_file}")
        
        # Procesar el primer ZIP encontrado
        zip_path = os.path.join(downloads_folder, zip_files[0])
        print(f"\n🔄 Procesando: {zip_files[0]}")
        
        # Procesar ZIP
        organized_folder = scraper.procesar_zip_descargado(zip_path)
        
        if organized_folder:
            print(f"\n📁 Carpeta organizada creada: {organized_folder}")
            
            # Crear 7Z final
            final_7z = scraper.crear_7z_final(organized_folder)
            
            if final_7z:
                print(f"✅ Archivo 7Z final creado: {final_7z}")
                
                # Verificar contenido del 7Z
                verificar_7z_contenido(final_7z)
                
                return True
            else:
                print("❌ Error creando archivo 7Z final")
                return False
        else:
            print("❌ Error procesando ZIP")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False


def verificar_7z_contenido(archivo_7z):
    """Verificar el contenido del archivo 7Z creado"""
    print(f"\n🔍 VERIFICANDO CONTENIDO DE: {os.path.basename(archivo_7z)}")
    
    try:
        import py7zr
        with py7zr.SevenZipFile(archivo_7z, mode="r", password="Rua2025") as archive:
            archivos = archive.getnames()
            
            print(f"📊 Total archivos en 7Z: {len(archivos)}")
            
            # Categorizar archivos
            poderes = [f for f in archivos if f.startswith("PODERES/")]
            solicitudes = [f for f in archivos if f.startswith("SOLICITUDES/")]
            excel_raiz = [f for f in archivos if f.endswith(".xlsx") and "/" not in f]
            otros = [f for f in archivos if f.startswith("OTROS/")]
            reportes = [f for f in archivos if "reporte" in f.lower()]
            
            print(f"\n📋 ESTRUCTURA ENCONTRADA:")
            print(f"   🏛️ PODERES/: {len(poderes)} archivos")
            for p in poderes:
                print(f"      • {p}")
                
            print(f"   📋 SOLICITUDES/: {len(solicitudes)} archivos")
            for s in solicitudes:
                print(f"      • {s}")
                
            print(f"   📊 Excel en raíz: {len(excel_raiz)} archivos")
            for e in excel_raiz:
                print(f"      • {e}")
            
            if otros:
                print(f"   ❓ OTROS/: {len(otros)} archivos")
                for o in otros:
                    print(f"      • {o}")
            
            if reportes:
                print(f"   📝 REPORTES: {len(reportes)} archivos")
                for r in reportes:
                    print(f"      • {r}")
            
            # Verificar estructura esperada
            estructura_correcta = (
                len(poderes) > 0 or len(solicitudes) > 0 or len(excel_raiz) > 0
            )
            
            if estructura_correcta:
                print(f"\n✅ ESTRUCTURA VERIFICADA CORRECTAMENTE")
                if len(poderes) > 0:
                    print(f"   ✓ Certificados organizados en PODERES/")
                if len(solicitudes) > 0:
                    print(f"   ✓ Solicitudes organizadas en SOLICITUDES/") 
                if len(excel_raiz) > 0:
                    print(f"   ✓ Excel en raíz correctamente")
            else:
                print(f"\n⚠️ Estructura puede no ser la esperada")
            
            return estructura_correcta
            
    except Exception as e:
        print(f"❌ Error verificando 7Z: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    # Si se pasa 'test' como argumento, ejecutar solo procesamiento
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'test':
        print("🔧 MODO PRUEBA ACTIVADO")
        success = test_processing_only()
        if success:
            print("\n🎉 ¡PRUEBA COMPLETADA EXITOSAMENTE!")
        else:
            print("\n❌ La prueba falló")
    else:
        main()
