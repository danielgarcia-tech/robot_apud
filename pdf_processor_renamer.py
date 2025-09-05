"""
PDF Processor and Renamer for ApudActa Files
Extrae datos de PDFs dentro de archivos ZIP y los renombra según patrones encontrados
Basado en la lógica de RPA_PODERES.PY
"""

import os
import json
import tempfile
import zipfile
import shutil
import re
from datetime import datetime
from pathlib import Path
import fitz  # PyMuPDF


class PDFProcessorAndRenamer:
    """Procesador y renombrador de PDFs basado en RPA_PODERES.PY"""
    
    def __init__(self, input_zip_path, output_folder=None):
        self.input_zip_path = input_zip_path
        self.output_folder = output_folder or os.path.join(os.path.dirname(input_zip_path), "processed_pdfs")
        self.temp_dir = None
        self.processing_results = []
        self.renamed_files = []
        
        # Crear carpeta de salida si no existe
        os.makedirs(self.output_folder, exist_ok=True)

    def extract_text_from_pdf(self, pdf_path):
        """Extraer texto del PDF y detectar si tiene OCR - Extraído de RPA_PODERES.PY"""
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

    def verificar_ocr_pdf(self, pdf_path):
        """Verificar si un PDF tiene OCR - Extraído de RPA_PODERES.PY"""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    page_text = page.get_text().strip()
                    if page_text:
                        return True
                return False
        except Exception:
            return False

    def buscar_identificadores(self, text):
        """Buscar DNI/NIF/NIE en texto - Extraído de RPA_PODERES.PY"""
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
        """Extraer información de cliente y fecha del nombre - Extraído de RPA_PODERES.PY"""
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
        """Generar nuevo nombre basado en identificadores encontrados"""
        if not identificadores:
            return None
        
        # Usar el primer identificador encontrado
        tipo, secuencia, post = identificadores[0]
        nuevo_nombre = f"PODER_{secuencia}.pdf"
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

    def procesar_pdf_individual(self, pdf_path, archivo_original, temp_extraction_dir):
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
                    nuevo_path_destino = os.path.join(self.output_folder, nuevo_nombre)
                    nuevo_path_final = self.verificar_archivo_existe(nuevo_path_destino)
                    nuevo_nombre_final = os.path.basename(nuevo_path_final)
                    
                    # Verificar si ya existe en destino (para evitar duplicados)
                    repetido_destino = os.path.exists(nuevo_path_destino) and nuevo_nombre != nuevo_nombre_final
                    
                    if not repetido_destino:
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
                        resultado.update({
                            "estado": "Repetido en destino - No copiado"
                        })
                        print(f"      ⚠️ Ya existe en destino, no copiado")
            else:
                # Sin identificadores, copiar con nombre original
                destino_original = os.path.join(self.output_folder, archivo_original)
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
            
            # En caso de error, al menos verificar OCR
            try:
                has_ocr = self.verificar_ocr_pdf(pdf_path)
                estado_ocr = "Sí" if has_ocr else "No"
            except:
                estado_ocr = "No se pudo verificar"
            
            cliente, fecha = self.extraer_cliente_fecha(archivo_original)
            
            resultado_error = {
                "archivo_original": archivo_original,
                "archivo_nuevo": archivo_original,
                "tipo": "ERROR",
                "secuencia": "",
                "secuencia_post": "",
                "estado": f"Error: {str(e)}",
                "export_path": "Error en exportación",
                "tiene_ocr": estado_ocr,
                "cliente": cliente,
                "fecha": fecha,
                "procesado_en": datetime.now().isoformat()
            }
            
            self.processing_results.append(resultado_error)
            return resultado_error

    def extraer_zip_y_procesar(self):
        """Extraer ZIP y procesar todos los PDFs encontrados"""
        print(f"📦 Extrayendo ZIP: {self.input_zip_path}")
        
        # Crear directorio temporal
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            # Extraer ZIP
            with zipfile.ZipFile(self.input_zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Buscar todos los archivos PDF
            pdf_files = []
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        full_path = os.path.join(root, file)
                        pdf_files.append((full_path, file))
            
            if not pdf_files:
                print("❌ No se encontraron archivos PDF en el ZIP")
                return False
            
            print(f"🔍 Encontrados {len(pdf_files)} archivos PDF")
            print(f"📁 Carpeta de salida: {self.output_folder}")
            print()
            
            # Procesar cada PDF
            for i, (pdf_path, pdf_name) in enumerate(pdf_files, 1):
                print(f"[{i}/{len(pdf_files)}]", end=" ")
                self.procesar_pdf_individual(pdf_path, pdf_name, self.temp_dir)
            
            return True
            
        except Exception as e:
            print(f"❌ Error procesando ZIP: {e}")
            return False
        
        finally:
            # Limpiar directorio temporal
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)

    def generar_reporte_excel_json(self):
        """Generar reporte en formato JSON (similar al Excel de RPA_PODERES)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.output_folder, f"reporte_procesamiento_{timestamp}.json")
        
        # Generar estadísticas
        total_archivos = len(self.processing_results)
        archivos_renombrados = len(self.renamed_files)
        archivos_con_ocr = sum(1 for r in self.processing_results if r.get('tiene_ocr') == 'Sí')
        archivos_con_identificadores = sum(1 for r in self.processing_results if r.get('identificadores_encontrados', 0) > 0)
        total_identificadores = sum(r.get('identificadores_encontrados', 0) for r in self.processing_results)
        
        reporte = {
            "resumen": {
                "archivo_zip_origen": os.path.basename(self.input_zip_path),
                "fecha_procesamiento": datetime.now().isoformat(),
                "carpeta_salida": self.output_folder,
                "total_archivos": total_archivos,
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
        
        print(f"\n📊 REPORTE GENERADO:")
        print(f"   📁 Total archivos procesados: {total_archivos}")
        print(f"   🔄 Archivos renombrados: {archivos_renombrados}")
        print(f"   🔍 Con OCR: {archivos_con_ocr}")
        print(f"   🆔 Con identificadores: {archivos_con_identificadores}")
        print(f"   📈 Total identificadores: {total_identificadores}")
        print(f"   💾 Reporte guardado en: {report_file}")
        
        return report_file

    def mostrar_resumen_terminal(self):
        """Mostrar resumen en terminal similar a RPA_PODERES"""
        print(f"\n" + "="*60)
        print(f"🎉 PROCESAMIENTO COMPLETADO")
        print(f"="*60)
        
        if self.renamed_files:
            print(f"\n📝 ARCHIVOS RENOMBRADOS:")
            for item in self.renamed_files:
                print(f"   • {item['original']}")
                print(f"     → {item['nuevo']} (ID: {item['identificador']})")
        
        errores = [r for r in self.processing_results if r.get('tipo') == 'ERROR']
        if errores:
            print(f"\n❌ ERRORES ENCONTRADOS:")
            for error in errores:
                print(f"   • {error['archivo_original']}: {error['estado']}")
        
        sin_identificadores = [r for r in self.processing_results 
                             if r.get('identificadores_encontrados', 0) == 0 and r.get('tipo') != 'ERROR']
        if sin_identificadores:
            print(f"\n⚠️ ARCHIVOS SIN IDENTIFICADORES:")
            for archivo in sin_identificadores:
                print(f"   • {archivo['archivo_original']}")


def procesar_zip_con_renombrado(zip_path, output_folder=None):
    """Función principal para procesar un ZIP con renombrado de PDFs"""
    if not os.path.exists(zip_path):
        print(f"❌ El archivo ZIP no existe: {zip_path}")
        return False
    
    print("="*60)
    print("🤖 PROCESADOR Y RENOMBRADOR DE PDFs")
    print("    Basado en RPA_PODERES.PY")
    print("="*60)
    
    processor = PDFProcessorAndRenamer(zip_path, output_folder)
    
    # Extraer y procesar
    success = processor.extraer_zip_y_procesar()
    
    if success:
        # Generar reporte
        processor.generar_reporte_excel_json()
        
        # Mostrar resumen
        processor.mostrar_resumen_terminal()
        
        return True
    else:
        print("❌ Error en el procesamiento")
        return False


def main():
    """Función principal - busca archivos ZIP en el directorio actual"""
    import sys
    
    # Verificar si se pasó un archivo ZIP como argumento
    if len(sys.argv) > 1:
        zip_path = sys.argv[1]
        output_folder = sys.argv[2] if len(sys.argv) > 2 else None
        
        if procesar_zip_con_renombrado(zip_path, output_folder):
            print("\n✅ Proceso completado exitosamente")
        else:
            print("\n❌ Error en el proceso")
        return
    
    # Buscar archivos ZIP en el directorio actual
    current_dir = os.getcwd()
    zip_files = [f for f in os.listdir(current_dir) 
                if f.lower().endswith('.zip') and os.path.isfile(f)]
    
    if not zip_files:
        print("❌ No se encontraron archivos ZIP en el directorio actual")
        print("\n💡 Uso:")
        print(f"   python {os.path.basename(__file__)} archivo.zip [carpeta_salida]")
        print("   o coloca archivos .zip en este directorio")
        return
    
    print(f"📦 Archivos ZIP encontrados: {len(zip_files)}")
    
    for zip_file in zip_files:
        print(f"\n🔄 Procesando: {zip_file}")
        
        # Crear carpeta de salida específica para cada ZIP
        base_name = os.path.splitext(zip_file)[0]
        output_folder = f"{base_name}_processed"
        
        if procesar_zip_con_renombrado(zip_file, output_folder):
            print(f"✅ {zip_file} procesado correctamente")
        else:
            print(f"❌ Error procesando {zip_file}")
    
    print(f"\n🎉 ¡Procesamiento de todos los archivos completado!")


if __name__ == "__main__":
    main()
