import os
import time
import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ApudActaScraper:
    """
    Scraper para descargar todos los documentos finalizados desde ApudActa
    """
    
    def __init__(self):
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.download_path = os.getenv('DOWNLOAD_PATH', './descargas')
        self.log_path = os.getenv('LOG_PATH', './logs')
        
        # MODO SIMPLIFICADO - SIEMPRE VISIBLE
        self.headless = False  # Forzar modo visible
        self.implicit_wait = 10
        self.wait_between_steps = 10  # 10 segundos entre pasos
        
        self.login_url = 'https://app.apudacta.com/login/'
        
        # Configurar paths
        Path(self.download_path).mkdir(parents=True, exist_ok=True)
        Path(self.log_path).mkdir(parents=True, exist_ok=True)
        
        # Configurar logging
        self.setup_logging()
        
        # Estado del scraper
        self.state_file = Path('scraper_state.json')
        self.downloaded_files = self.load_downloaded_files()
        
        self.driver = None
        
        self.logger.info("=== SCRAPER MODO SIMPLIFICADO INICIADO ===")
        self.logger.info("- Modo visible activado")
        self.logger.info(f"- Wait entre pasos: {self.wait_between_steps}s")
    
    def setup_logging(self):
        """Configurar el sistema de logging"""
        log_filename = f"{self.log_path}/scraper_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def load_downloaded_files(self) -> Dict:
        """Cargar el estado de archivos ya descargados"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error cargando estado: {e}")
                return {}
        return {}
    
    def save_downloaded_files(self):
        """Guardar el estado de archivos descargados"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.downloaded_files, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando estado: {e}")
    
    def setup_driver(self):
        """Configurar Chrome en modo visible simplificado"""
        try:
            self.logger.info("🚀 PASO 1: Configurando navegador...")
            
            chrome_options = Options()
            # MODO VISIBLE - Sin headless
            chrome_options.add_argument('--start-maximized')
            
            # Configurar carpeta de descarga
            prefs = {
                "download.default_directory": os.path.abspath(self.download_path),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "profile.default_content_settings.popups": 0
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Crear driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(self.implicit_wait)
            
            self.logger.info("✅ Navegador configurado correctamente")
            print("✅ NAVEGADOR LISTO - Puedes ver el proceso en la ventana del navegador")
            
            # Wait entre pasos
            time.sleep(self.wait_between_steps)
            
        except Exception as e:
            self.logger.error(f"❌ Error configurando navegador: {e}")
            raise
    
    def slow_motion_wait(self, message: str = ""):
        """Aplicar delay de slow motion entre acciones"""
        if message:
            self.logger.info(f"Slow motion: {message}")
        time.sleep(self.slow_motion_delay)
    
    def wait_for_element(self, locator, timeout: int = None):
        """Esperar por un elemento con timeout personalizado"""
        timeout = timeout or self.explicit_wait
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))
    
    def wait_and_click(self, locator, timeout: int = None):
        """Esperar por un elemento y hacer click con slow motion"""
        element = self.wait_for_element(locator, timeout)
        self.slow_motion_wait("Preparando click")
        element.click()
        self.slow_motion_wait("Click realizado")
        return element

    def login(self) -> bool:
        """Realizar login en ApudActa con waits mejorados"""
        try:
            self.logger.info("Iniciando proceso de login")
            
            # Ir a la página de login
            self.driver.get(self.login_url)
            self.slow_motion_wait("Página de login cargada")
            
            # Esperar a que aparezca el formulario de login
            wait = WebDriverWait(self.driver, 20)
            
            # Buscar el campo de email por ID
            email_field = wait.until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.clear()
            email_field.send_keys(self.email)
            self.slow_motion_wait("Email ingresado")
            
            # Buscar el campo de contraseña por ID
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            self.slow_motion_wait("Contraseña ingresada")
            
            # Hacer click en el botón de login usando el texto del span
            login_button = self.driver.find_element(By.XPATH, "//span[text()='Inicia sesión']/parent::button")
            login_button.click()
            self.slow_motion_wait("Botón de login presionado")
            
            # Esperar a ser redirigido al dashboard
            wait.until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "APODERAMIENTOS"))
            )
            
            self.logger.info("Login realizado correctamente")
            self.slow_motion_wait("Login verificado")
            return True
            
        except Exception as e:
            self.logger.error(f"Error durante el login: {e}")
            return False
    
    def navigate_to_downloads(self) -> bool:
        """Navegar a la sección de descargas con slow motion"""
        try:
            self.logger.info("Navegando a la sección de descargas")
            
            # Hacer click en APODERAMIENTOS
            apoderamientos_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "APODERAMIENTOS")
            apoderamientos_link.click()
            self.slow_motion_wait("Click en APODERAMIENTOS")
            
            # Hacer click en la pestaña DESCARGAS ZIP usando el role="tab" y el texto
            wait = WebDriverWait(self.driver, self.explicit_wait)
            descargas_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@role='tab' and contains(text(), 'Descargas Zip')]"))
            )
            descargas_tab.click()
            self.slow_motion_wait("Click en pestaña Descargas Zip")
            
            self.logger.info("Navegación a descargas completada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error navegando a descargas: {e}")
            return False
    
    def learn_download_button_location(self) -> Dict:
        """Función interactiva para que el usuario enseñe dónde está el botón de descarga"""
        
        try:
            original_headless = self.headless
            self.logger.info("=== MODO APRENDIZAJE: UBICACIÓN DEL BOTÓN DE DESCARGA ===")
            
            print("🎓 MODO APRENDIZAJE ACTIVADO")
            print("Vamos a enseñar al sistema dónde está el botón de descarga...")
            print()
            
            # Verificar que ya tenemos una sesión activa con el driver
            if not hasattr(self, 'driver') or self.driver is None:
                raise Exception("No hay sesión activa del navegador. Asegúrate de haber ejecutado setup_driver() primero.")
            
            print("✅ Usando la sesión del navegador ya existente.")
            print("✅ Ya estamos en la página de descargas.")
            print()
            print("INSTRUCCIONES:")
            print("1. 👀 Observa la tabla que se muestra en el navegador")
            print("2. 🖱️  Haz click MANUALMENTE en el botón de descarga de cualquier archivo")
            print("3. ⏰ Tienes 60 segundos para hacer el click")
            print("4. 🤖 El sistema detectará automáticamente qué elemento clickeaste")
            print("5. 🔗 También registraré la URL que se abre al hacer click")
            print()
            input("Presiona ENTER cuando estés listo...")
            
            # Esperar a que cargue la tabla
            wait = WebDriverWait(self.driver, 15)
            table = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            print("⏳ Esperando tu click... (60 segundos)")
            
            # JavaScript para detectar clicks
            click_detector_script = """
            window.clickedElement = null;
            window.clickedElementInfo = null;
            
            document.addEventListener('click', function(event) {
                window.clickedElement = event.target;
                
                // Obtener información detallada del elemento
                var info = {
                    tagName: event.target.tagName,
                    className: event.target.className,
                    id: event.target.id,
                    textContent: event.target.textContent.trim(),
                    innerHTML: event.target.innerHTML,
                    xpath: getXPath(event.target)
                };
                
                // Información de la celda padre
                var cell = event.target.closest('td');
                if (cell) {
                    var row = cell.closest('tr');
                    if (row) {
                        var cells = row.querySelectorAll('td');
                        info.cellIndex = Array.from(cells).indexOf(cell);
                        info.rowIndex = Array.from(row.parentNode.children).indexOf(row);
                    }
                }
                
                window.clickedElementInfo = info;
                console.log('Click detectado:', info);
            });
            
            function getXPath(element) {
                if (!element) return '';
                if (element.id) return `//*[@id="${element.id}"]`;
                
                var parts = [];
                while (element && element.nodeType === Node.ELEMENT_NODE) {
                    var siblings = Array.from(element.parentNode.children).filter(child => child.tagName === element.tagName);
                    var index = siblings.indexOf(element) + 1;
                    var tagName = element.tagName.toLowerCase();
                    var part = siblings.length > 1 ? `${tagName}[${index}]` : tagName;
                    parts.unshift(part);
                    element = element.parentNode;
                }
                return parts.length ? '/' + parts.join('/') : '';
            }
            
            return true;
            """
            
            # Ejecutar el script de detección
            self.driver.execute_script(click_detector_script)
            
            # Esperar hasta que el usuario haga click o timeout
            start_time = time.time()
            timeout = 60  # 60 segundos
            
            while time.time() - start_time < timeout:
                try:
                    click_info = self.driver.execute_script("return window.clickedElementInfo;")
                    if click_info:
                        print("✅ ¡Click detectado!")
                        print(f"Elemento: {click_info['tagName']}")
                        print(f"Clases: {click_info['className']}")
                        print(f"Texto: {click_info['textContent']}")
                        print(f"Posición: Fila {click_info.get('rowIndex', 'N/A')}, Columna {click_info.get('cellIndex', 'N/A')}")
                        print()
                        
                        # Guardar la información del botón
                        button_config = {
                            'detection_method': 'user_click',
                            'tagName': click_info['tagName'],
                            'className': click_info['className'],
                            'textContent': click_info['textContent'],
                            'cellIndex': click_info.get('cellIndex'),
                            'xpath_template': self._create_xpath_template(click_info),
                            'timestamp': datetime.now().isoformat(),
                            'success': True
                        }
                        
                        # Guardar configuración
                        self._save_button_config(button_config)
                        
                        print("💾 Configuración guardada exitosamente!")
                        print(f"XPath generado: {button_config['xpath_template']}")
                        
                        # Restaurar configuración original
                        self.headless = original_headless
                        
                        return button_config
                        
                except Exception as e:
                    pass
                
                time.sleep(0.5)
            
            print("⏰ Tiempo agotado. No se detectó ningún click.")
            print("Usando configuración predeterminada...")
            
            # Configuración por defecto
            default_config = {
                'detection_method': 'default',
                'xpath_template': ".//span[@class='font-bold cursor-pointer text-lg' and text()='📂']",
                'cellIndex': 8,
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            
            self._save_button_config(default_config)
            self.headless = original_headless
            
            return default_config
            
        except Exception as e:
            self.logger.error(f"Error en modo aprendizaje: {e}")
            self.headless = original_headless
            return None
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def _create_xpath_template(self, click_info: Dict) -> str:
        """Crear un template XPath basado en la información del click"""
        tag_name = click_info['tagName'].lower()
        class_name = click_info['className']
        text_content = click_info['textContent']
        
        if class_name and text_content:
            # Crear XPath con clase y texto
            return f".//{tag_name}[@class='{class_name}' and text()='{text_content}']"
        elif class_name:
            # Solo con clase
            class_parts = class_name.split()
            class_conditions = " and ".join([f"contains(@class, '{cls}')" for cls in class_parts if cls])
            return f".//{tag_name}[{class_conditions}]"
        elif text_content:
            # Solo con texto
            return f".//{tag_name}[text()='{text_content}']"
        else:
            # XPath genérico
            return f".//{tag_name}"
    
    def _save_button_config(self, config: Dict):
        """Guardar configuración del botón aprendida"""
        config_file = Path('button_config.json')
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuración del botón guardada en {config_file}")
        except Exception as e:
            self.logger.error(f"Error guardando configuración del botón: {e}")
    
    def _load_button_config(self) -> Dict:
        """Cargar configuración del botón guardada"""
        config_file = Path('button_config.json')
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info("Configuración del botón cargada desde archivo")
                return config
            except Exception as e:
                self.logger.warning(f"Error cargando configuración del botón: {e}")
        
        # Configuración por defecto
        return {
            'detection_method': 'default',
            'xpath_template': ".//span[@class='font-bold cursor-pointer text-lg' and text()='📂']",
            'cellIndex': 8
        }
    def get_available_downloads(self) -> List[Dict]:
        """Obtener lista de archivos disponibles para descarga (todos los finalizados)"""
        try:
            self.logger.info("Obteniendo lista de todas las descargas disponibles")
            
            # Cargar configuración del botón de descarga
            button_config = self._load_button_config()
            self.logger.info(f"Usando configuración de botón: {button_config['detection_method']}")
            
            # Esperar a que cargue la tabla
            wait = WebDriverWait(self.driver, 15)
            table = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            downloads = []
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Saltar header
            
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 7:  # Verificar que tiene columnas suficientes
                        
                        # Extraer información de la fila
                        if len(cells) >= 9:
                            # Estructura de 9 columnas
                            numero = cells[0].text.strip()     
                            nombre = cells[1].text.strip()     
                            tamaño = cells[2].text.strip()     
                            fecha = cells[3].text.strip()      
                            archivos = cells[4].text.strip()   
                            apudactas = cells[5].text.strip()  
                            estado = cells[6].text.strip()     
                            download_cell_index = button_config.get('cellIndex', 8)
                        else:
                            # Estructura de 8 columnas (respaldo)
                            numero = cells[0].text.strip() if len(cells) > 0 else ""
                            nombre = cells[1].text.strip() if len(cells) > 1 else ""
                            tamaño = cells[2].text.strip() if len(cells) > 2 else ""
                            fecha = cells[3].text.strip() if len(cells) > 3 else ""
                            archivos = cells[4].text.strip() if len(cells) > 4 else ""
                            apudactas = cells[5].text.strip() if len(cells) > 5 else ""
                            estado = cells[6].text.strip() if len(cells) > 6 else ""
                            download_cell_index = min(button_config.get('cellIndex', 7), len(cells) - 1)
                        
                        # Buscar el botón de descarga usando la configuración aprendida
                        try:
                            if download_cell_index < len(cells):
                                download_cell = cells[download_cell_index]
                                xpath_template = button_config['xpath_template']
                                download_icon = download_cell.find_element(By.XPATH, xpath_template)
                            else:
                                # Buscar en la última columna como respaldo
                                download_cell = cells[-1]
                                download_icon = download_cell.find_element(By.XPATH, ".//span[contains(@class, 'cursor-pointer')]")
                                
                        except NoSuchElementException:
                            # Intentar con métodos alternativos
                            try:
                                download_cell = cells[-1]
                                # Buscar cualquier elemento clickeable
                                download_icon = download_cell.find_element(By.XPATH, ".//*[contains(@class, 'cursor-pointer') or contains(@onclick, '') or @href]")
                            except NoSuchElementException:
                                self.logger.warning(f"No se encontró botón de descarga para: {nombre}")
                                continue
                        
                        # Verificar si está finalizada (sin filtro de fecha)
                        if 'FINALIZADA' in estado.upper():
                            download_info = {
                                'numero': numero,
                                'nombre': nombre,
                                'tamaño': tamaño,
                                'fecha': fecha,
                                'archivos': archivos,
                                'apudactas': apudactas,
                                'estado': estado,
                                'download_icon': download_icon,
                                'row_element': row,
                                'button_method': button_config['detection_method']
                            }
                            downloads.append(download_info)
                            self.logger.info(f"Archivo disponible para descarga: {nombre} - {fecha}")
                            
                except Exception as e:
                    self.logger.warning(f"Error procesando fila de descarga: {e}")
                    continue
            
            self.logger.info(f"Encontrados {len(downloads)} archivos disponibles para descargar")
            return downloads
            
        except Exception as e:
            self.logger.error(f"Error obteniendo descargas: {e}")
            return []
    
    def download_file(self, download_info: Dict) -> bool:
        """Descargar un archivo específico haciendo click en el botón 📂 con slow motion"""
        try:
            filename = download_info['nombre']
            
            # Verificar si ya se descargó
            if filename in self.downloaded_files:
                self.logger.info(f"Archivo ya descargado anteriormente: {filename}")
                return True
            
            self.logger.info(f"Descargando: {filename} - Fecha: {download_info['fecha']}")
            
            # Hacer scroll al elemento si es necesario
            self.driver.execute_script("arguments[0].scrollIntoView();", download_info['row_element'])
            self.slow_motion_wait("Scroll al elemento de descarga")
            
            # Hacer click en el botón 📂 con clases: font-bold cursor-pointer text-lg
            download_info['download_icon'].click()
            self.slow_motion_wait("Click en botón de descarga")
            
            # Esperar a que termine la descarga
            download_completed = self.wait_for_download(filename)
            
            if download_completed:
                # Marcar como descargado
                self.downloaded_files[filename] = {
                    'fecha_descarga': datetime.now().isoformat(),
                    'info': {k: v for k, v in download_info.items() 
                            if k not in ['download_icon', 'row_element']}
                }
                self.save_downloaded_files()
                self.logger.info(f"Descarga completada: {filename}")
                return True
            else:
                self.logger.error(f"Timeout esperando descarga: {filename}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error descargando {filename}: {e}")
            return False
    
    def wait_for_download(self, expected_filename: str, timeout: int = 300) -> bool:
        """Esperar a que se complete la descarga"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Buscar archivos en la carpeta de descarga
            download_files = list(Path(self.download_path).glob("*.zip"))
            
            # Buscar el archivo específico
            for file_path in download_files:
                if expected_filename in file_path.name:
                    # Verificar que no esté parcialmente descargado
                    if not file_path.name.endswith('.crdownload'):
                        return True
            
            time.sleep(2)
        
        return False
    
    
    
    
    def run_daily_scraping(self):
        """Ejecutar el scraping de todos los archivos disponibles"""
        try:
            self.logger.info("=== INICIO DE SCRAPING COMPLETO ===")
            
            # Verificar si existe configuración del botón
            button_config = self._load_button_config()
            if button_config['detection_method'] == 'default':
                self.logger.warning("⚠️  No hay configuración personalizada del botón de descarga.")
                self.logger.warning("⚠️  Recomendación: Ejecutar 'demo_aprendizaje.py' primero para configurar el botón.")
                self.logger.info("Continuando con configuración por defecto...")
            else:
                self.logger.info(f"✅ Usando configuración aprendida: {button_config['detection_method']}")
            
            # Configurar driver
            self.setup_driver()
            
            # Hacer login
            if not self.login():
                raise Exception("Falló el login")
            
            # Navegar a descargas
            if not self.navigate_to_downloads():
                raise Exception("Falló la navegación a descargas")
            
            # Obtener lista de todas las descargas disponibles
            downloads = self.get_available_downloads()
            
            if not downloads:
                self.logger.info("No se encontraron archivos finalizados disponibles para descarga")
                return
            
            self.logger.info(f"Se encontraron {len(downloads)} archivos finalizados para descargar")
            
            # Descargar archivos
            successful_downloads = 0
            failed_downloads = 0
            
            for download in downloads:
                if self.download_file(download):
                    successful_downloads += 1
                    self.slow_motion_wait(f"Descarga {successful_downloads} completada")
                else:
                    failed_downloads += 1
                    self.slow_motion_wait("Error en descarga, continuando")
            
            self.logger.info(f"Scraping completado: {successful_downloads} exitosas, {failed_downloads} fallidas")
            
        except Exception as e:
            self.logger.error(f"Error en scraping diario: {e}")
            raise
        
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("Driver cerrado")
    
    def generate_report(self) -> str:
        """Generar reporte de archivos descargados"""
        try:
            if not self.downloaded_files:
                return "No hay archivos descargados para reportar"
            
            # Crear DataFrame con la información
            data = []
            for filename, info in self.downloaded_files.items():
                row = {
                    'archivo': filename,
                    'fecha_descarga': info['fecha_descarga'],
                    'tamaño': info['info'].get('tamaño', 'N/A'),
                    'fecha_original': info['info'].get('fecha', 'N/A'),
                    'archivos_contenidos': info['info'].get('archivos', 'N/A'),
                    'apudactas': info['info'].get('apudactas', 'N/A')
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Guardar reporte
            report_filename = f"{self.log_path}/reporte_descargas_{datetime.now().strftime('%Y%m%d')}.xlsx"
            df.to_excel(report_filename, index=False)
            
            self.logger.info(f"Reporte generado: {report_filename}")
            return report_filename
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return None


if __name__ == "__main__":
    scraper = ApudActaScraper()
    scraper.run_daily_scraping()
    scraper.generate_report()
