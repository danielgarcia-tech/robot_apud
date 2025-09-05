"""
Crear ZIP simple para probar easyday.py
"""

import os
import tempfile
import zipfile
from datetime import datetime


def crear_zip_simple_prueba():
    """Crear un ZIP simple para probar con easyday.py"""
    print("🔧 Creando ZIP simple para probar easyday.py...")
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    
    # Archivos de prueba simples (sin caracteres problemáticos)
    archivos_prueba = [
        # Certificados 
        "CertificadoRegistro_12345678A.pdf",
        "CertificadoRegistro_87654321B.pdf", 
        
        # Solicitudes
        "Solicitud_ApudActa_cliente1.pdf",
        "Solicitud_ApudActa_cliente2.pdf",
        
        # Excel
        "Solicitudes.xlsx"
    ]
    
    try:
        # Crear archivos de prueba
        for archivo in archivos_prueba:
            archivo_path = os.path.join(temp_dir, archivo)
            
            # Crear contenido según el tipo
            if "12345678A" in archivo:
                contenido = "Documento PDF con DNI 12345678A del titular"
            elif "87654321B" in archivo:
                contenido = "Este certificado pertenece al DNI 87654321B"
            elif "Solicitud_ApudActa" in archivo:
                contenido = "Solicitud de ApudActa sin identificadores específicos"
            elif "Solicitudes.xlsx" in archivo:
                contenido = "Datos,Excel\nFila1,Datos1\nFila2,Datos2"
            else:
                contenido = f"Contenido de prueba para {archivo}"
            
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
        
        # Crear ZIP en la carpeta downloads
        downloads_folder = "downloads"
        os.makedirs(downloads_folder, exist_ok=True)
        
        zip_nombre = os.path.join(downloads_folder, f"apudacta_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        with zipfile.ZipFile(zip_nombre, 'w') as zip_ref:
            for archivo in archivos_prueba:
                archivo_path = os.path.join(temp_dir, archivo)
                zip_ref.write(archivo_path, archivo)
        
        print(f"✅ ZIP de prueba creado: {zip_nombre}")
        print(f"📁 Contenido:")
        for archivo in archivos_prueba:
            print(f"   📄 {archivo}")
        
        return zip_nombre
        
    finally:
        # Limpiar directorio temporal
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    zip_file = crear_zip_simple_prueba()
    print(f"\n💡 Ahora puedes ejecutar easyday.py para procesar este archivo")
    print(f"   El archivo está en: {zip_file}")
