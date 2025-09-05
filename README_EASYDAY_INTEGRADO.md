# EASYDAY con Procesamiento PDF Integrado

Scraper automatizado de ApudActa con procesamiento PDF integrado basado en RPA_PODERES.PY. Descarga archivos, procesa PDFs para extraer identificadores DNI/NIF/NIE, renombra archivos y genera un archivo 7Z final con contraseña.

## 🎯 Características principales

### 🔄 Flujo completo automatizado:
1. **Login automático** en ApudActa
2. **Descarga de archivos** de la primera fila
3. **Extracción y procesamiento** de PDFs del ZIP descargado
4. **Análisis de contenido** con PyMuPDF (OCR y texto)
5. **Búsqueda automática** de DNI/NIF/NIE
6. **Renombrado inteligente** a formato `PODER_{identificador}.pdf`
7. **Generación de reportes** JSON con estadísticas
8. **Compresión final** 7Z con contraseña

### 📄 Procesamiento PDF (basado en RPA_PODERES.PY):
- ✅ **Extracción de texto** con detección OCR automática
- ✅ **Búsqueda de identificadores** (DNI/NIF/NIE) con regex avanzado
- ✅ **Renombrado automático** siguiendo el patrón `PODER_{ID}.pdf`
- ✅ **Manejo de duplicados** con sufijos numéricos
- ✅ **Preservación de originales** sin identificadores
- ✅ **Reportes detallados** con estadísticas de procesamiento

## 📦 Instalación

```bash
# Instalar dependencias (incluyendo PyMuPDF)
pip install -r requirements.txt

# Instalar Playwright browsers
playwright install chromium
```

## 🚀 Uso

### Configuración básica:
Crear archivo `.env` con credenciales:
```env
EMAIL=tu_email@ejemplo.com
PASSWORD=tu_contraseña
```

### Ejecución:
```bash
python easyday.py
```

## 📁 Estructura de archivos generados

```
PROYECTO ROBOT APUD/
├── descargas/                          # Archivos descargados originales
│   └── temp_fila1.zip
├── procesados/                         # PDFs procesados y renombrados
│   ├── PODER_12345678A.pdf            # PDF renombrado con DNI
│   ├── PODER_X1234567B.pdf            # PDF renombrado con NIE  
│   ├── documento_original.pdf          # PDF sin identificadores
│   ├── reporte_procesamiento_*.json    # Reporte detallado
│   └── apudacta_procesado_*.7z         # Archivo final comprimido
└── easyday.py                          # Script principal
```

## 📊 Ejemplo de reporte generado

```json
{
  "resumen": {
    "fecha_procesamiento": "2025-01-15T10:30:00",
    "total_archivos": 5,
    "archivos_renombrados": 3,
    "archivos_con_ocr": 4,
    "archivos_con_identificadores": 3,
    "total_identificadores_encontrados": 5
  },
  "archivos_renombrados": [
    {
      "original": "certificado_antiguo.pdf",
      "nuevo": "PODER_12345678A.pdf", 
      "identificador": "12345678A"
    }
  ],
  "detalle_procesamiento": [...]
}
```

## 🔍 Patrones de identificadores reconocidos

- **DNI/NIF**: `12345678A` (7-8 dígitos + letra)
- **NIE**: `X1234567B` (X/Y/Z + 7 dígitos + letra)

## ⚡ Flujo de ejecución paso a paso

```
🎯 INICIANDO PROCESO COMPLETO CON PROCESAMIENTO PDF
======================================================================
⚡ MODO SÚPER SIMPLIFICADO CON PROCESAMIENTO INTEGRADO
🔍 MODO HEADLESS (sin ventana visible)
📄 PROCESAMIENTO PDF AUTOMÁTICO:
   • Extracción de texto y detección OCR
   • Búsqueda de DNI/NIF/NIE
   • Renombrado automático a PODER_{ID}.pdf
   • Generación de reportes JSON
📦 COMPRESIÓN FINAL CON CONTRASEÑA

🔧 PASO 1: Configurando navegador...
🔐 PASO 2: Haciendo login...
🎯 PASO 3: Navegando a descargas...
🔍 PASO 4: Encontrando archivos...
⬇️  PASO 5: Descargando archivo de la FILA 1...
🔍 PASO 6: Procesando PDFs del archivo descargado...
   📄 Procesando: documento1.pdf
      ✅ Renombrado a: PODER_12345678A.pdf
      🆔 Identificador: 12345678A (DNI/NIF)
      🔍 OCR: Detectado
📦 PASO 7: Creando archivo 7Z final...

🎉 PROCESO COMPLETADO EXITOSAMENTE!
📁 Archivo final: apudacta_procesado_20250115_103000.7z
```

## 🔧 Configuración avanzada

### Parámetros ajustables en el código:
```python
# Tiempos de espera
self.wait_between_steps = 0.5  # Segundos entre pasos
self.download_wait = 2         # Segundos para descarga

# Contraseña del archivo 7Z
self.archive_password = 'Rua2025'

# Carpetas
self.download_path = './descargas'    # Descargas temporales
self.processed_path = './procesados'  # PDFs procesados
```

## 🔐 Seguridad

- **Contraseña 7Z**: `Rua2025` (AES-256)
- **Archivos temporales**: Se eliminan automáticamente
- **Credenciales**: Cargadas desde archivo `.env`
- **Modo headless**: Sin ventana visible del navegador

## 🛠️ Funciones PDF integradas (de RPA_PODERES.PY)

### Métodos principales:
- `extract_text_from_pdf()`: Extrae texto y detecta OCR
- `buscar_identificadores()`: Busca DNI/NIF/NIE con regex
- `extraer_cliente_fecha()`: Parsea información del nombre del archivo
- `procesar_pdf_individual()`: Procesa cada PDF individualmente
- `generar_nuevo_nombre()`: Crea nombres basados en identificadores
- `verificar_archivo_existe()`: Maneja duplicados

### Lógica de renombrado:
1. **Extrae texto** del PDF usando PyMuPDF
2. **Busca identificadores** con patrones regex específicos
3. **Genera nuevo nombre** con formato `PODER_{identificador}.pdf`
4. **Verifica duplicados** y agrega sufijos si es necesario
5. **Copia archivos** a carpeta de procesados
6. **Preserva originales** sin identificadores

## 📈 Estadísticas de procesamiento

El script genera estadísticas completas:
- Total de archivos procesados
- Archivos renombrados exitosamente  
- Archivos con capacidad OCR
- Archivos con identificadores encontrados
- Total de identificadores únicos

## 🐛 Manejo de errores

- **PDFs corruptos**: Continúa con el siguiente archivo
- **Falta de identificadores**: Mantiene nombre original
- **Duplicados**: Agrega sufijos numéricos automáticamente
- **Errores de OCR**: Marca el archivo pero continúa procesando
- **Fallos de descarga**: Informa error y termina limpiamente

## 🔄 Integración con sistemas externos

El archivo 7Z final puede ser integrado fácilmente con:
- Sistemas de gestión documental
- Workflows automatizados
- APIs de terceros
- Sistemas de backup

## 📝 Ejemplo de salida de consola

```
[1/3] 📄 Procesando: CertificadoRegistro.pdf_12345678A_CLIENTE_2025-01-15.pdf
      ✅ Renombrado a: PODER_12345678A.pdf
      🆔 Identificador: 12345678A (DNI/NIF)
      🔍 OCR: Detectado

[2/3] 📄 Procesando: documento_sin_id.pdf
      ℹ️ Sin identificadores, copiado como: documento_sin_id.pdf
      ❌ OCR: No detectado

[3/3] 📄 Procesando: poder_X7654321C_test.pdf
      ✅ Renombrado a: PODER_X7654321C.pdf
      🆔 Identificador: X7654321C (NIE)
      🔍 OCR: Detectado

📊 REPORTE DE PROCESAMIENTO:
   📁 Total archivos procesados: 3
   🔄 Archivos renombrados: 2
   🔍 Con OCR: 2
   🆔 Con identificadores: 2
   📈 Total identificadores: 2
   💾 Reporte guardado en: reporte_procesamiento_20250115_103000.json

📦 Comprimiendo 4 archivos...
✅ Archivo 7Z creado: apudacta_procesado_20250115_103000.7z
🔐 Protegido con contraseña: Rua2025
```

---

**Desarrollado integrando las capacidades de RPA_PODERES.PY en el scraper EASYDAY para automatización completa de documentos de ApudActa** 🤖📄
