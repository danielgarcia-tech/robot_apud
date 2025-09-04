"""
Script de demostración para el sistema de aprendizaje interactivo
Este script permite que el usuario configure manualmente dónde se encuentra
el botón de descarga en la interfaz web.
"""

import os
import sys
import time
import json
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.apudacta_scraper import ApudActaScraper

def learn_download_button_interactive(scraper):
    """Función de aprendizaje que usa el navegador ya abierto"""
    try:
        print("🎓 MODO APRENDIZAJE ACTIVADO")
        print("Vamos a enseñar al sistema dónde está el botón de descarga...")
        print()
        
        # Esperar a que cargue la tabla
        wait = WebDriverWait(scraper.driver, 15)
        table = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        print("✅ Tabla de descargas cargada.")
        print()
        print("INSTRUCCIONES:")
        print("1. 👀 Observa la tabla que se muestra en el navegador")
        print("2. 🖱️  Haz click MANUALMENTE en el botón de descarga de cualquier archivo")
        print("3. ⏰ Tienes 60 segundos para hacer el click")
        print("4. 🤖 El sistema detectará automáticamente qué elemento clickeaste")
        print("5. 🔗 También rastreará la URL que se abre al hacer click")
        print()
        input("Presiona ENTER cuando estés listo...")
        
        print("⏳ Esperando tu click... (60 segundos)")
        
        # JavaScript para detectar clicks y URLs
        click_detector_script = """
        window.clickedElement = null;
        window.clickedElementInfo = null;
        window.downloadUrl = null;
        window.originalUrl = window.location.href;
        
        // Rastrear cambios de URL
        let urlCheckInterval = setInterval(function() {
            if (window.location.href !== window.originalUrl) {
                window.downloadUrl = window.location.href;
                window.originalUrl = window.location.href;
            }
        }, 500);
        
        // Detectar clicks
        document.addEventListener('click', function(event) {
            window.clickedElement = event.target;
            
            // Obtener información detallada del elemento
            var info = {
                tagName: event.target.tagName,
                className: event.target.className,
                id: event.target.id,
                textContent: event.target.textContent.trim(),
                innerHTML: event.target.innerHTML,
                xpath: getXPath(event.target),
                href: event.target.href || null
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
            
            // Esperar un poco para capturar cambios de URL
            setTimeout(function() {
                if (window.downloadUrl) {
                    console.log('URL de descarga detectada:', window.downloadUrl);
                }
            }, 1000);
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
        scraper.driver.execute_script(click_detector_script)
        
        # Esperar hasta que el usuario haga click o timeout
        start_time = time.time()
        timeout = 60  # 60 segundos
        
        while time.time() - start_time < timeout:
            try:
                click_info = scraper.driver.execute_script("return window.clickedElementInfo;")
                download_url = scraper.driver.execute_script("return window.downloadUrl;")
                
                if click_info:
                    print("✅ ¡Click detectado!")
                    print(f"Elemento: {click_info['tagName']}")
                    print(f"Clases: {click_info['className']}")
                    print(f"Texto: {click_info['textContent']}")
                    print(f"Posición: Fila {click_info.get('rowIndex', 'N/A')}, Columna {click_info.get('cellIndex', 'N/A')}")
                    if click_info.get('href'):
                        print(f"Enlace: {click_info['href']}")
                    if download_url:
                        print(f"URL de descarga: {download_url}")
                    print()
                    
                    # Crear XPath template
                    xpath_template = create_xpath_template(click_info)
                    
                    # Guardar la información del botón
                    button_config = {
                        'detection_method': 'user_click_interactive',
                        'tagName': click_info['tagName'],
                        'className': click_info['className'],
                        'textContent': click_info['textContent'],
                        'cellIndex': click_info.get('cellIndex'),
                        'xpath_template': xpath_template,
                        'href': click_info.get('href'),
                        'download_url': download_url,
                        'timestamp': datetime.now().isoformat(),
                        'success': True
                    }
                    
                    # Guardar configuración
                    save_button_config(button_config)
                    
                    print("💾 Configuración guardada exitosamente!")
                    print(f"XPath generado: {button_config['xpath_template']}")
                    if download_url:
                        print(f"URL de descarga rastreada: {download_url}")
                    
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
        
        save_button_config(default_config)
        return default_config
        
    except Exception as e:
        print(f"Error en modo aprendizaje: {e}")
        return None

def create_xpath_template(click_info):
    """Crear template XPath basado en la información del click"""
    tag = click_info['tagName'].lower()
    class_name = click_info['className']
    text_content = click_info['textContent']
    
    if class_name and text_content:
        return f".//{tag}[@class='{class_name}' and text()='{text_content}']"
    elif class_name:
        return f".//{tag}[@class='{class_name}']"
    elif text_content:
        return f".//{tag}[text()='{text_content}']"
    else:
        return f".//{tag}"

def save_button_config(config):
    """Guardar configuración del botón"""
    config_file = "button_config.json"
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando configuración: {e}")

def main():
    """Ejecutar demo del sistema de aprendizaje"""
    
    print("=" * 60)
    print(" DEMO - SISTEMA DE APRENDIZAJE INTERACTIVO")
    print("=" * 60)
    print()
    print("Este demo te permitirá enseñar al robot dónde encontrar")
    print("el botón de descarga en la web de ApudActa.")
    print()
    
    # Confirmar que el usuario quiere continuar
    respuesta = input("¿Deseas continuar con el aprendizaje? (s/n): ").lower().strip()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Demo cancelado.")
        return
    
    print("\n" + "=" * 60)
    print(" INSTRUCCIONES")
    print("=" * 60)
    print("1. Se abrirá el navegador y navegará automáticamente a ApudActa")
    print("2. El robot hará login automáticamente")
    print("3. Navegará a la sección de descargas")
    print("4. ¡IMPORTANTE! Tendrás 60 segundos para hacer click")
    print("   en el botón de descarga de cualquier archivo")
    print("5. El sistema detectará automáticamente dónde hiciste click")
    print("6. También rastreará la URL que se abre")
    print("7. La configuración se guardará para futuros usos")
    print()
    
    input("Presiona ENTER cuando estés listo para comenzar...")
    
    
    try:
        # Crear instancia del scraper
        scraper = ApudActaScraper()
        
        print("\n🤖 Iniciando navegador...")
        scraper.setup_driver()
        
        print("🔐 Iniciando sesión...")
        if not scraper.login():
            print("❌ Error en el login. Verifica las credenciales en el archivo .env")
            return
        
        print("📂 Navegando a la sección de descargas...")
        if not scraper.navigate_to_downloads():
            print("❌ Error navegando a descargas")
            return
        
        print("\n" + "🎯" * 20)
        print("¡AHORA ES TU TURNO!")
        print("Tienes 60 segundos para hacer click en el botón de descarga")
        print("de cualquier archivo en la tabla.")
        print("También se rastreará la URL que se abre.")
        print("🎯" * 20)
        
        # Ejecutar el aprendizaje usando el navegador existente
        success = learn_download_button_interactive(scraper)
        
        if success and success.get('success'):
            print("\n✅ ¡Configuración guardada exitosamente!")
            print("El robot ahora sabe dónde encontrar el botón de descarga.")
            print("Puedes ejecutar el script principal con confianza.")
            if success.get('download_url'):
                print(f"URL de descarga detectada: {success['download_url']}")
        else:
            print("\n❌ No se pudo completar el aprendizaje.")
            print("Puedes intentarlo nuevamente ejecutando este demo.")
        
    except Exception as e:
        print(f"\n❌ Error durante el demo: {e}")
        
    finally:
        try:
            # Cerrar el navegador
            if hasattr(scraper, 'driver') and scraper.driver:
                scraper.driver.quit()
                print("\n🔒 Navegador cerrado.")
        except:
            pass
    
    print("\n" + "=" * 60)
    print(" DEMO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
