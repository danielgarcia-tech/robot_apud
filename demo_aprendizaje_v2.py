"""
Script de demostración para el sistema de aprendizaje interactivo
Este script permite que el usuario configure manualmente dónde se encuentra
el botón de descarga en la interfaz web y rastrea las URLs de descarga.
"""

import os
import sys
import json
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.apudacta_scraper import ApudActaScraper

def learn_button_interactively(scraper):
    """Función de aprendizaje interactivo que usa la sesión existente"""
    try:
        print("\n🎓 MODO APRENDIZAJE ACTIVADO")
        print("Vamos a enseñar al sistema dónde está el botón de descarga...")
        print()
        
        print("✅ Usando sesión de navegador actual.")
        print()
        print("INSTRUCCIONES:")
        print("1. 👀 Observa la tabla que se muestra en el navegador")
        print("2. 🖱️  Haz click MANUALMENTE en el botón de descarga de cualquier archivo")
        print("3. ⏰ Tienes 60 segundos para hacer el click")
        print("4. 🤖 El sistema detectará automáticamente qué elemento clickeaste")
        print("5. 📋 También rastreará la URL que se abre")
        print()
        input("Presiona ENTER cuando estés listo...")
        
        # Esperar a que cargue la tabla
        wait = WebDriverWait(scraper.driver, 15)
        table = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        print("⏳ Esperando tu click... (60 segundos)")
        
        # JavaScript mejorado para detectar clicks y URLs
        click_detector_script = """
        window.clickedElement = null;
        window.clickedElementInfo = null;
        window.originalURL = window.location.href;
        window.newURL = null;
        
        // Detectar cambios de URL
        var originalPushState = history.pushState;
        var originalReplaceState = history.replaceState;
        
        history.pushState = function() {
            originalPushState.apply(history, arguments);
            window.newURL = window.location.href;
        };
        
        history.replaceState = function() {
            originalReplaceState.apply(history, arguments);
            window.newURL = window.location.href;
        };
        
        // Detectar navegación
        window.addEventListener('beforeunload', function() {
            window.newURL = 'navigation_detected';
        });
        
        // Detectar apertura de nuevas ventanas/tabs
        var originalOpen = window.open;
        window.open = function(url) {
            window.newURL = url || 'new_window_opened';
            return originalOpen.apply(window, arguments);
        };
        
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
                href: event.target.href || event.target.closest('a')?.href || null,
                onclick: event.target.getAttribute('onclick') || null
            };
            
            // Información de la celda padre
            var cell = event.target.closest('td');
            if (cell) {
                var row = cell.closest('tr');
                if (row) {
                    var cells = row.querySelectorAll('td');
                    info.cellIndex = Array.from(cells).indexOf(cell);
                    info.rowIndex = Array.from(row.parentNode.children).indexOf(row);
                    
                    // Obtener datos de la fila
                    info.rowData = Array.from(cells).map(cell => cell.textContent.trim());
                }
            }
            
            // Detectar si es un enlace de descarga
            var link = event.target.closest('a');
            if (link) {
                info.linkHref = link.href;
                info.linkTarget = link.target;
            }
            
            window.clickedElementInfo = info;
            console.log('Click detectado:', info);
            
            // Esperar un poco para capturar cambios de URL
            setTimeout(function() {
                if (window.location.href !== window.originalURL) {
                    window.newURL = window.location.href;
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
                new_url = scraper.driver.execute_script("return window.newURL;")
                
                if click_info:
                    print("✅ ¡Click detectado!")
                    print(f"Elemento: {click_info['tagName']}")
                    print(f"Clases: {click_info['className']}")
                    print(f"Texto: {click_info['textContent']}")
                    print(f"Posición: Fila {click_info.get('rowIndex', 'N/A')}, Columna {click_info.get('cellIndex', 'N/A')}")
                    
                    if new_url:
                        print(f"📋 URL detectada: {new_url}")
                    
                    if click_info.get('href'):
                        print(f"🔗 Enlace directo: {click_info['href']}")
                    
                    if click_info.get('rowData'):
                        print(f"📊 Datos de la fila: {click_info['rowData']}")
                    
                    print()
                    
                    # Crear XPath template mejorado
                    xpath_template = create_xpath_template(click_info)
                    
                    # Guardar la información del botón
                    button_config = {
                        'detection_method': 'interactive_learning',
                        'tagName': click_info['tagName'],
                        'className': click_info['className'],
                        'textContent': click_info['textContent'],
                        'cellIndex': click_info.get('cellIndex'),
                        'xpath_template': xpath_template,
                        'href_pattern': click_info.get('href'),
                        'link_target': click_info.get('linkTarget'),
                        'detected_url': new_url,
                        'row_data_sample': click_info.get('rowData'),
                        'timestamp': datetime.now().isoformat(),
                        'success': True
                    }
                    
                    # Guardar configuración
                    save_button_config(button_config)
                    
                    print("💾 Configuración guardada exitosamente!")
                    print(f"🎯 XPath generado: {button_config['xpath_template']}")
                    if button_config['detected_url']:
                        print(f"📋 URL capturada: {button_config['detected_url']}")
                    
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
        print(f"❌ Error en modo aprendizaje: {e}")
        return None

def create_xpath_template(click_info):
    """Crear un XPath template basado en la información del click"""
    tag = click_info['tagName'].lower()
    class_name = click_info['className']
    text_content = click_info['textContent']
    
    if class_name and text_content:
        return f".//{tag}[@class='{class_name}' and text()='{text_content}']"
    elif class_name:
        return f".//{tag}[contains(@class, '{class_name.split()[0]}')]"
    elif text_content:
        return f".//{tag}[text()='{text_content}']"
    else:
        return f".//{tag}"

def save_button_config(config):
    """Guardar configuración del botón en archivo JSON"""
    config_path = "button_config.json"
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
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
    print("También rastreará la URL que se abre al hacer click.")
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
    print("6. También rastreará la URL que se abra")
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
        print("Haz click en el botón de descarga de cualquier archivo.")
        print("El sistema detectará el click y la URL de descarga.")
        print("🎯" * 20)
        
        # Ejecutar el aprendizaje con la sesión actual
        config = learn_button_interactively(scraper)
        
        if config and config.get('success'):
            print("\n✅ ¡Configuración guardada exitosamente!")
            print("El robot ahora sabe dónde encontrar el botón de descarga.")
            if config.get('detected_url'):
                print("También se capturó la URL de descarga.")
            print("Puedes ejecutar el script principal con confianza.")
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
