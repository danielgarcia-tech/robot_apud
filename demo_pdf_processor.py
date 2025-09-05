"""
Script de demostración y testing para el PDF Processor and Renamer
Permite probar las funcionalidades de procesamiento y renombrado
"""

import os
import sys
import tempfile
import zipfile
from datetime import datetime
from pdf_processor_renamer import PDFProcessorAndRenamer, procesar_zip_con_renombrado


def crear_zip_ejemplo():
    """Crear un ZIP de ejemplo para testing (si no hay archivos reales)"""
    print("🔧 Creando ZIP de ejemplo para testing...")
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Crear algunos archivos PDF ficticios (solo para estructura, no contenido real)
        archivos_ejemplo = [
            "documento_12345678A_ejemplo.pdf",
            "certificado_X1234567B_prueba.pdf", 
            "poder_87654321C_test_2025-01-15.pdf",
            "archivo_sin_dni.pdf"
        ]
        
        for archivo in archivos_ejemplo:
            archivo_path = os.path.join(temp_dir, archivo)
            with open(archivo_path, 'w') as f:
                f.write("Archivo PDF de ejemplo - No es un PDF real")
        
        # Crear ZIP
        zip_ejemplo = "ejemplo_para_testing.zip"
        with zipfile.ZipFile(zip_ejemplo, 'w') as zip_ref:
            for archivo in archivos_ejemplo:
                archivo_path = os.path.join(temp_dir, archivo)
                zip_ref.write(archivo_path, archivo)
        
        print(f"✅ ZIP de ejemplo creado: {zip_ejemplo}")
        return zip_ejemplo
        
    finally:
        # Limpiar directorio temporal
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def mostrar_info_archivos():
    """Mostrar información de los archivos ZIP disponibles"""
    print("📋 INFORMACIÓN DE ARCHIVOS DISPONIBLES")
    print("="*50)
    
    current_dir = os.getcwd()
    zip_files = [f for f in os.listdir(current_dir) 
                if f.lower().endswith('.zip') and os.path.isfile(f)]
    
    if not zip_files:
        print("❌ No hay archivos ZIP en el directorio actual")
        return []
    
    for i, zip_file in enumerate(zip_files, 1):
        file_size = os.path.getsize(zip_file)
        modified_time = datetime.fromtimestamp(os.path.getmtime(zip_file))
        
        print(f"{i}. {zip_file}")
        print(f"   📏 Tamaño: {file_size:,} bytes")
        print(f"   📅 Modificado: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Mostrar contenido del ZIP
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                pdf_files = [f for f in zip_ref.namelist() if f.lower().endswith('.pdf')]
                print(f"   📄 PDFs encontrados: {len(pdf_files)}")
                if pdf_files:
                    for pdf in pdf_files[:3]:  # Mostrar solo los primeros 3
                        print(f"      • {pdf}")
                    if len(pdf_files) > 3:
                        print(f"      ... y {len(pdf_files) - 3} más")
        except:
            print(f"   ❌ Error leyendo contenido del ZIP")
        
        print()
    
    return zip_files


def menu_interactivo():
    """Menu interactivo para usar el procesador"""
    while True:
        print("\n" + "="*60)
        print("🤖 PROCESADOR Y RENOMBRADOR DE PDFs - MENÚ PRINCIPAL")
        print("="*60)
        print("1. 📋 Mostrar archivos ZIP disponibles")
        print("2. 🔄 Procesar archivo ZIP específico")
        print("3. 🔄 Procesar todos los archivos ZIP")
        print("4. 🔧 Crear ZIP de ejemplo para testing")
        print("5. 📊 Ver último reporte generado")
        print("0. 🚪 Salir")
        
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
        if opcion == "0":
            print("👋 ¡Hasta luego!")
            break
        elif opcion == "1":
            mostrar_info_archivos()
        elif opcion == "2":
            procesar_archivo_especifico()
        elif opcion == "3":
            procesar_todos_archivos()
        elif opcion == "4":
            crear_zip_ejemplo()
        elif opcion == "5":
            mostrar_ultimo_reporte()
        else:
            print("❌ Opción no válida")


def procesar_archivo_especifico():
    """Procesar un archivo ZIP específico seleccionado por el usuario"""
    zip_files = mostrar_info_archivos()
    
    if not zip_files:
        print("❌ No hay archivos para procesar")
        return
    
    try:
        seleccion = input(f"\n👉 Selecciona archivo (1-{len(zip_files)}) o 0 para cancelar: ").strip()
        
        if seleccion == "0":
            return
        
        indice = int(seleccion) - 1
        if 0 <= indice < len(zip_files):
            archivo_seleccionado = zip_files[indice]
            
            # Preguntar por carpeta de salida
            output_default = f"{os.path.splitext(archivo_seleccionado)[0]}_processed"
            output_folder = input(f"📁 Carpeta de salida (Enter para '{output_default}'): ").strip()
            if not output_folder:
                output_folder = output_default
            
            print(f"\n🚀 Procesando: {archivo_seleccionado}")
            print(f"📁 Salida: {output_folder}")
            
            if procesar_zip_con_renombrado(archivo_seleccionado, output_folder):
                print(f"\n✅ ¡{archivo_seleccionado} procesado exitosamente!")
            else:
                print(f"\n❌ Error procesando {archivo_seleccionado}")
        else:
            print("❌ Selección no válida")
            
    except ValueError:
        print("❌ Debe ingresar un número válido")
    except KeyboardInterrupt:
        print("\n⏹️ Operación cancelada por el usuario")


def procesar_todos_archivos():
    """Procesar todos los archivos ZIP encontrados"""
    zip_files = [f for f in os.listdir('.') 
                if f.lower().endswith('.zip') and os.path.isfile(f)]
    
    if not zip_files:
        print("❌ No hay archivos ZIP para procesar")
        return
    
    print(f"📦 Se procesarán {len(zip_files)} archivos ZIP")
    confirmacion = input("¿Continuar? (s/N): ").strip().lower()
    
    if confirmacion not in ['s', 'si', 'sí', 'y', 'yes']:
        print("⏹️ Operación cancelada")
        return
    
    exitos = 0
    errores = 0
    
    for zip_file in zip_files:
        print(f"\n🔄 Procesando: {zip_file}")
        
        # Crear carpeta de salida específica
        base_name = os.path.splitext(zip_file)[0]
        output_folder = f"{base_name}_processed"
        
        try:
            if procesar_zip_con_renombrado(zip_file, output_folder):
                print(f"   ✅ {zip_file} - Éxito")
                exitos += 1
            else:
                print(f"   ❌ {zip_file} - Error")
                errores += 1
        except Exception as e:
            print(f"   ❌ {zip_file} - Error: {e}")
            errores += 1
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   ✅ Exitosos: {exitos}")
    print(f"   ❌ Errores: {errores}")
    print(f"   📁 Total: {len(zip_files)}")


def mostrar_ultimo_reporte():
    """Mostrar el contenido del último reporte generado"""
    import json
    import glob
    
    # Buscar archivos de reporte más recientes
    reportes = glob.glob("**/reporte_procesamiento_*.json", recursive=True)
    
    if not reportes:
        print("❌ No se encontraron reportes generados")
        return
    
    # Ordenar por fecha de modificación (más reciente primero)
    reportes.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    ultimo_reporte = reportes[0]
    
    print(f"📊 ÚLTIMO REPORTE: {ultimo_reporte}")
    print("="*50)
    
    try:
        with open(ultimo_reporte, 'r', encoding='utf-8') as f:
            reporte = json.load(f)
        
        resumen = reporte.get('resumen', {})
        print(f"📦 ZIP origen: {resumen.get('archivo_zip_origen', 'N/A')}")
        print(f"📅 Fecha: {resumen.get('fecha_procesamiento', 'N/A')}")
        print(f"📁 Total archivos: {resumen.get('total_archivos', 0)}")
        print(f"🔄 Renombrados: {resumen.get('archivos_renombrados', 0)}")
        print(f"🔍 Con OCR: {resumen.get('archivos_con_ocr', 0)}")
        print(f"🆔 Con identificadores: {resumen.get('archivos_con_identificadores', 0)}")
        
        # Mostrar archivos renombrados
        renombrados = reporte.get('archivos_renombrados', [])
        if renombrados:
            print(f"\n📝 ARCHIVOS RENOMBRADOS:")
            for item in renombrados:
                print(f"   • {item.get('original', 'N/A')}")
                print(f"     → {item.get('nuevo', 'N/A')} (ID: {item.get('identificador', 'N/A')})")
        
    except Exception as e:
        print(f"❌ Error leyendo reporte: {e}")


def modo_linea_comandos():
    """Manejar argumentos de línea de comandos"""
    if len(sys.argv) < 2:
        return False
    
    comando = sys.argv[1].lower()
    
    if comando in ['help', '--help', '-h']:
        print("📖 AYUDA - PDF Processor and Renamer")
        print("="*50)
        print("Uso:")
        print(f"  python {os.path.basename(__file__)}                    # Menú interactivo")
        print(f"  python {os.path.basename(__file__)} archivo.zip        # Procesar archivo específico")
        print(f"  python {os.path.basename(__file__)} archivo.zip salida # Procesar con carpeta de salida")
        print(f"  python {os.path.basename(__file__)} --all             # Procesar todos los ZIP")
        print(f"  python {os.path.basename(__file__)} --demo            # Crear ZIP de ejemplo")
        print(f"  python {os.path.basename(__file__)} --info            # Mostrar info de archivos")
        return True
    
    elif comando == '--all':
        procesar_todos_archivos()
        return True
    
    elif comando == '--demo':
        crear_zip_ejemplo()
        return True
    
    elif comando == '--info':
        mostrar_info_archivos()
        return True
    
    elif comando.endswith('.zip'):
        zip_path = comando
        output_folder = sys.argv[2] if len(sys.argv) > 2 else None
        
        if os.path.exists(zip_path):
            if procesar_zip_con_renombrado(zip_path, output_folder):
                print("\n✅ Proceso completado exitosamente")
            else:
                print("\n❌ Error en el proceso")
        else:
            print(f"❌ El archivo no existe: {zip_path}")
        return True
    
    return False


def main():
    """Función principal del script de demostración"""
    print("🤖 PDF PROCESSOR AND RENAMER - DEMO SCRIPT")
    print("="*60)
    
    # Verificar si hay argumentos de línea de comandos
    if modo_linea_comandos():
        return
    
    # Si no hay argumentos, mostrar menú interactivo
    try:
        menu_interactivo()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Programa terminado por el usuario!")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
