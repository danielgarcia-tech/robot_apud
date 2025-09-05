"""
Script de prueba para verificar la organización de archivos en subcarpetas
Simula el procesamiento de un ZIP con estructura de ApudActa
"""

import os
import tempfile
import zipfile
from datetime import datetime


def crear_zip_prueba():
    """Crear un ZIP de prueba con estructura similar a ApudActa"""
    print("🔧 Creando ZIP de prueba con estructura ApudActa...")
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    
    # Archivos de prueba a crear
    archivos_prueba = [
        # Certificados (van a PODERES)
        "CertificadoRegistro.pdf_12345678A_JUAN_PEREZ_2025-09-05_10-30-00.pdf",
        "CertificadoRegistro.pdf_87654321B_MARIA_GARCIA_2025-09-05_11-00-00.pdf",
        "CertificadoRegistro_especial.pdf",
        
        # Solicitudes (van a SOLICITUDES)  
        "Solicitud_ApudActa_cliente1_2025-09-05.pdf",
        "Solicitud_ApudActa_cliente2_2025-09-05.pdf",
        
        # Excel (va a raíz)
        "Solicitudes.xlsx",
        "Solicitudes_backup.xlsx",
        
        # Otros archivos para probar
        "documento_extra.pdf",
        "readme.txt"
    ]
    
    try:
        # Crear archivos de prueba
        for archivo in archivos_prueba:
            archivo_path = os.path.join(temp_dir, archivo)
            
            # Crear contenido según el tipo de archivo
            if archivo.lower().endswith('.pdf'):
                # Simular contenido PDF con identificadores para algunos archivos
                if "12345678A" in archivo:
                    contenido = "Contenido del PDF con DNI 12345678A en el texto"
                elif "87654321B" in archivo:
                    contenido = "Este documento contiene el DNI 87654321B del titular"
                else:
                    contenido = "Contenido PDF sin identificadores claros"
            elif archivo.lower().endswith('.xlsx'):
                contenido = "Datos,Excel,Solicitudes\nFila1,Datos1,Info1\nFila2,Datos2,Info2"
            else:
                contenido = f"Archivo de prueba: {archivo}"
            
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
        
        # Crear ZIP
        zip_nombre = f"apudacta_prueba_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(zip_nombre, 'w') as zip_ref:
            for archivo in archivos_prueba:
                archivo_path = os.path.join(temp_dir, archivo)
                zip_ref.write(archivo_path, archivo)
        
        print(f"✅ ZIP de prueba creado: {zip_nombre}")
        print(f"📁 Contenido:")
        for archivo in archivos_prueba:
            if "CertificadoRegistro" in archivo:
                print(f"   🏛️ {archivo} → PODERES/")
            elif "Solicitud_ApudActa" in archivo:
                print(f"   📋 {archivo} → SOLICITUDES/")
            elif "Solicitudes" in archivo and archivo.endswith('.xlsx'):
                print(f"   📊 {archivo} → RAÍZ/")
            else:
                print(f"   ❓ {archivo} → OTROS/")
        
        return zip_nombre
        
    finally:
        # Limpiar directorio temporal
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def probar_estructura_zip(zip_file):
    """Probar que el ZIP tenga la estructura esperada"""
    print(f"\n🔍 PROBANDO ESTRUCTURA DE: {zip_file}")
    print("="*50)
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            archivos = zip_ref.namelist()
            
            # Verificar estructura esperada
            poderes_files = [f for f in archivos if f.startswith('PODERES/')]
            solicitudes_files = [f for f in archivos if f.startswith('SOLICITUDES/')]
            excel_files = [f for f in archivos if f.endswith('.xlsx') and '/' not in f]
            otros_files = [f for f in archivos if f.startswith('OTROS/')]
            
            print(f"📊 ANÁLISIS DE ESTRUCTURA:")
            print(f"   🏛️ PODERES/: {len(poderes_files)} archivos")
            for f in poderes_files:
                print(f"      • {f}")
                
            print(f"   📋 SOLICITUDES/: {len(solicitudes_files)} archivos")
            for f in solicitudes_files:
                print(f"      • {f}")
                
            print(f"   📊 Excel en raíz: {len(excel_files)} archivos")
            for f in excel_files:
                print(f"      • {f}")
                
            if otros_files:
                print(f"   ❓ OTROS/: {len(otros_files)} archivos")
                for f in otros_files:
                    print(f"      • {f}")
            
            # Verificar que la estructura sea correcta
            estructura_correcta = (
                len(poderes_files) > 0 and  # Debe haber archivos en PODERES
                len(solicitudes_files) > 0 and  # Debe haber archivos en SOLICITUDES
                len(excel_files) > 0  # Debe haber Excel en raíz
            )
            
            if estructura_correcta:
                print(f"\n✅ ESTRUCTURA CORRECTA")
                print(f"   ✓ Certificados en PODERES/")
                print(f"   ✓ Solicitudes en SOLICITUDES/")
                print(f"   ✓ Excel en raíz")
            else:
                print(f"\n❌ ESTRUCTURA INCORRECTA")
                print(f"   • PODERES: {'✓' if len(poderes_files) > 0 else '✗'}")
                print(f"   • SOLICITUDES: {'✓' if len(solicitudes_files) > 0 else '✗'}")
                print(f"   • Excel raíz: {'✓' if len(excel_files) > 0 else '✗'}")
            
            return estructura_correcta
            
    except Exception as e:
        print(f"❌ Error analizando ZIP: {e}")
        return False


def main():
    """Función principal para probar la estructura"""
    print("🧪 PRUEBA DE ORGANIZACIÓN DE ARCHIVOS")
    print("="*60)
    
    # Crear ZIP de prueba
    zip_prueba = crear_zip_prueba()
    
    if not zip_prueba:
        print("❌ No se pudo crear ZIP de prueba")
        return
    
    # Probar estructura
    estructura_ok = probar_estructura_zip(zip_prueba)
    
    if estructura_ok:
        print(f"\n🎉 ¡PRUEBA EXITOSA!")
        print(f"✅ El ZIP tiene la estructura correcta")
        print(f"\n💡 Ahora puedes usar este ZIP para probar easyday.py:")
        print(f"   python easyday.py")
        print(f"   (Coloca el ZIP en la carpeta downloads)")
    else:
        print(f"\n❌ PRUEBA FALLIDA")
        print(f"❌ La estructura no es la esperada")
    
    print(f"\n📁 Archivo de prueba: {zip_prueba}")
    
    # Limpiar
    limpiar = input("\n🗑️ ¿Eliminar archivo de prueba? (s/N): ").strip().lower()
    if limpiar in ['s', 'si', 'sí']:
        try:
            os.remove(zip_prueba)
            print(f"✅ Archivo eliminado")
        except:
            print(f"❌ No se pudo eliminar el archivo")


if __name__ == "__main__":
    main()
