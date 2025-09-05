"""
Ejemplo de uso independiente del procesador PDF
Demuestra cómo usar las funciones de procesamiento PDF extraídas de RPA_PODERES.PY
"""

import json
import os
import tempfile
import zipfile
from datetime import datetime
import fitz  # PyMuPDF
import re


class PDFProcessorExample:
    """Demostración de procesamiento PDF independiente"""
    
    def __init__(self):
        self.results = []
    
    def extract_text_from_pdf(self, pdf_path):
        """Extraer texto de PDF y detectar capacidad OCR"""
        text = ""
        has_ocr = False
        
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    page_text = page.get_text()
                    text += page_text
                    
                    if page_text.strip():
                        has_ocr = True
            
            return text, has_ocr
        except Exception as e:
            print(f"Error extrayendo texto de {pdf_path}: {e}")
            return "", False

    def buscar_identificadores(self, text):
        """Buscar identificadores DNI/NIF/NIE en texto"""
        dni_nif_pattern = r"\b\d{7,8}[A-Z]\b"
        nie_pattern = r"\b[XYZ]\d{7}[A-Z]\b"
        
        resultados = []
        
        for match in re.finditer(f"{nie_pattern}|{dni_nif_pattern}", text):
            secuencia = match.group()
            tipo = "NIE" if re.match(nie_pattern, secuencia) else "DNI/NIF"
            
            start_pos = match.end()
            secuencia_post = text[start_pos:start_pos+20].strip()
            resultados.append((tipo, secuencia, secuencia_post))
            
        return resultados

    def extraer_cliente_fecha(self, nombre_archivo):
        """Extraer información de cliente y fecha del nombre del archivo"""
        # Patrón: _DNI_CLIENTE_FECHA.pdf
        patron = r'_(\w{7,9}[A-Z])_([A-ZÁÉÍÓÚÑa-záéíóúñ\-\s]+)_((?:\d{4}-\d{2}-\d{2})_\d{2}:\d{2}:\d{2})'
        m = re.search(patron, nombre_archivo)
        if m:
            cliente = m.group(2).replace('_', ' ').strip()
            fecha = m.group(3).replace('_', ' ')
            return cliente, fecha
        
        # Alternativa: buscar última fecha tipo yyyy-mm-dd
        fecha_alt = re.findall(r'(\d{4}-\d{2}-\d{2})', nombre_archivo)
        fecha = fecha_alt[-1] if fecha_alt else ''
        return '', fecha

    def procesar_archivo_zip(self, zip_path):
        """Procesar todos los PDFs dentro de un archivo ZIP"""
        print(f"🔍 Procesando archivo ZIP: {zip_path}")
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Extraer ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Buscar y procesar PDFs
            pdf_count = 0
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_path = os.path.join(root, file)
                        resultado = self.procesar_pdf_individual(pdf_path, file)
                        self.results.append(resultado)
                        pdf_count += 1
            
            print(f"✅ Procesados {pdf_count} archivos PDF")
            return self.generar_resumen()
            
        finally:
            # Limpiar directorio temporal
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def procesar_pdf_individual(self, pdf_path, filename):
        """Procesar un archivo PDF individual"""
        try:
            # Extraer texto y verificar OCR
            text, has_ocr = self.extract_text_from_pdf(pdf_path)
            
            # Buscar identificadores
            identificadores = self.buscar_identificadores(text)
            
            # Extraer información de cliente y fecha
            cliente, fecha = self.extraer_cliente_fecha(filename)
            
            # Información del archivo
            file_size = os.path.getsize(pdf_path)
            
            resultado = {
                "archivo": filename,
                "tamaño_bytes": file_size,
                "tiene_ocr": has_ocr,
                "longitud_texto": len(text),
                "identificadores_encontrados": len(identificadores),
                "identificadores": [
                    {"tipo": tipo, "numero": numero, "contexto": contexto}
                    for tipo, numero, contexto in identificadores
                ],
                "cliente": cliente,
                "fecha": fecha,
                "procesado_en": datetime.now().isoformat(),
                "preview_texto": text[:200] + "..." if len(text) > 200 else text
            }
            
            print(f"   📄 {filename}")
            print(f"      - OCR: {'✅' if has_ocr else '❌'}")
            print(f"      - IDs encontrados: {len(identificadores)}")
            if cliente:
                print(f"      - Cliente: {cliente}")
            if identificadores:
                print(f"      - Primer ID: {identificadores[0][1]} ({identificadores[0][0]})")
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error procesando {filename}: {e}")
            return {
                "archivo": filename,
                "error": str(e),
                "procesado_en": datetime.now().isoformat()
            }

    def generar_resumen(self):
        """Generar resumen del procesamiento"""
        total_archivos = len(self.results)
        archivos_con_ocr = sum(1 for r in self.results if r.get('tiene_ocr', False))
        archivos_con_ids = sum(1 for r in self.results if r.get('identificadores_encontrados', 0) > 0)
        total_ids = sum(r.get('identificadores_encontrados', 0) for r in self.results)
        
        resumen = {
            "resumen_procesamiento": {
                "total_archivos": total_archivos,
                "archivos_con_ocr": archivos_con_ocr,
                "archivos_con_identificadores": archivos_con_ids,
                "total_identificadores": total_ids,
                "fecha_procesamiento": datetime.now().isoformat()
            },
            "detalles_archivos": self.results
        }
        
        print(f"\n📊 RESUMEN DEL PROCESAMIENTO:")
        print(f"   📁 Total archivos: {total_archivos}")
        print(f"   🔍 Con OCR: {archivos_con_ocr}")
        print(f"   🆔 Con identificadores: {archivos_con_ids}")
        print(f"   📈 Total IDs encontrados: {total_ids}")
        
        return resumen

    def exportar_resultados(self, output_file="resultados_procesamiento.json"):
        """Exportar resultados a archivo JSON"""
        resumen = self.generar_resumen()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados exportados a: {output_file}")
        return output_file


def ejemplo_uso():
    """Ejemplo de uso del procesador PDF"""
    print("=== EJEMPLO DE PROCESAMIENTO PDF ===\n")
    
    processor = PDFProcessorExample()
    
    # Buscar archivos ZIP en el directorio actual
    archivos_zip = [f for f in os.listdir('.') if f.lower().endswith('.zip')]
    
    if not archivos_zip:
        print("❌ No se encontraron archivos ZIP para procesar")
        print("💡 Coloca un archivo ZIP con PDFs en el directorio actual")
        return
    
    print(f"📦 Archivos ZIP encontrados: {len(archivos_zip)}")
    
    for zip_file in archivos_zip:
        print(f"\n🔄 Procesando: {zip_file}")
        try:
            resumen = processor.procesar_archivo_zip(zip_file)
            
            # Exportar resultados individuales
            output_name = f"procesamiento_{os.path.splitext(zip_file)[0]}.json"
            processor.exportar_resultados(output_name)
            
        except Exception as e:
            print(f"❌ Error procesando {zip_file}: {e}")
    
    print(f"\n🎉 ¡Procesamiento completado!")


if __name__ == "__main__":
    ejemplo_uso()
