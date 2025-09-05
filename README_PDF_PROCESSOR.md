# PDF Processor and Renamer

Procesador y renombrador de archivos PDF basado en la lógica de `RPA_PODERES.PY`. Extrae datos de archivos PDF dentro de archivos ZIP y los renombra según los identificadores encontrados (DNI/NIF/NIE).

## 🎯 Características principales

- **Extracción automática**: Descomprime archivos ZIP y procesa todos los PDFs encontrados
- **Detección de identificadores**: Busca automáticamente DNI/NIF/NIE en el contenido de los PDFs
- **Renombrado inteligente**: Renombra archivos según el patrón `PODER_{identificador}.pdf`
- **Verificación OCR**: Detecta si los PDFs tienen texto extraíble
- **Prevención de duplicados**: Evita sobrescribir archivos existentes
- **Reportes detallados**: Genera reportes JSON con estadísticas completas
- **Modo interactivo**: Incluye menú para facilitar el uso

## 📦 Instalación

```bash
# Instalar dependencias
pip install -r requirements_pdf_processor.txt

# O instalar manualmente
pip install PyMuPDF
```

## 🚀 Uso

### Modo Línea de Comandos

```bash
# Procesar un archivo ZIP específico
python pdf_processor_renamer.py archivo.zip

# Procesar con carpeta de salida personalizada
python pdf_processor_renamer.py archivo.zip mi_carpeta_salida

# Procesar todos los archivos ZIP del directorio actual
python pdf_processor_renamer.py

# Ver ayuda
python demo_pdf_processor.py --help
```

### Modo Interactivo

```bash
# Ejecutar demo con menú interactivo
python demo_pdf_processor.py
```

El menú interactivo ofrece las siguientes opciones:
1. 📋 Mostrar archivos ZIP disponibles
2. 🔄 Procesar archivo ZIP específico  
3. 🔄 Procesar todos los archivos ZIP
4. 🔧 Crear ZIP de ejemplo para testing
5. 📊 Ver último reporte generado

### Uso Programático

```python
from pdf_processor_renamer import procesar_zip_con_renombrado

# Procesar un archivo
success = procesar_zip_con_renombrado("mi_archivo.zip", "carpeta_salida")

if success:
    print("✅ Procesamiento exitoso")
else:
    print("❌ Error en el procesamiento")
```

## 📋 Funcionalidades extraídas de RPA_PODERES.PY

### Funciones de procesamiento PDF:
- `extract_text_from_pdf()`: Extrae texto y detecta OCR
- `buscar_identificadores()`: Busca DNI/NIF/NIE con patrones regex
- `extraer_cliente_fecha()`: Extrae información de cliente y fecha del nombre
- `verificar_ocr_pdf()`: Verifica capacidad OCR del PDF

### Lógica de renombrado:
- Busca identificadores en el texto del PDF
- Genera nombres con formato `PODER_{identificador}.pdf`
- Maneja duplicados agregando sufijos numéricos
- Preserva archivos sin identificadores con nombre original

## 📊 Estructura de reportes

El procesador genera reportes JSON con la siguiente estructura:

```json
{
  "resumen": {
    "archivo_zip_origen": "ejemplo.zip",
    "fecha_procesamiento": "2025-01-15T10:30:00",
    "total_archivos": 5,
    "archivos_renombrados": 3,
    "archivos_con_ocr": 4,
    "archivos_con_identificadores": 3,
    "total_identificadores_encontrados": 5
  },
  "archivos_renombrados": [
    {
      "original": "documento_antiguo.pdf",
      "nuevo": "PODER_12345678A.pdf",
      "identificador": "12345678A"
    }
  ],
  "detalle_procesamiento": [...]
}
```

## 🔍 Patrones de identificadores soportados

- **DNI/NIF**: 7-8 dígitos seguidos de una letra (ej: `12345678A`)
- **NIE**: Letra X, Y, o Z seguida de 7 dígitos y una letra (ej: `X1234567B`)

## 📁 Estructura de archivos de salida

```
carpeta_salida/
├── PODER_12345678A.pdf        # PDF renombrado
├── PODER_X1234567B.pdf        # PDF renombrado  
├── documento_original.pdf      # PDF sin identificadores
└── reporte_procesamiento_20250115_103000.json
```

## ⚡ Ejemplos de uso

### Ejemplo 1: Procesamiento básico
```bash
# Tienes un archivo: descargas_apudacta.zip
python pdf_processor_renamer.py descargas_apudacta.zip

# Resultado:
# descargas_apudacta_processed/
#   ├── PODER_12345678A.pdf
#   ├── PODER_87654321B.pdf  
#   └── reporte_procesamiento_*.json
```

### Ejemplo 2: Múltiples archivos
```bash
# Tienes varios ZIP en el directorio
python pdf_processor_renamer.py

# Procesará automáticamente todos los .zip encontrados
```

### Ejemplo 3: Con demo interactivo
```bash
python demo_pdf_processor.py

# Menú interactivo:
# 1. Ver archivos disponibles
# 2. Procesar archivo específico
# 3. Procesar todos
# 4. Crear ZIP de ejemplo
# 5. Ver reportes
```

## 🛠️ Características técnicas

- **Manejo de errores**: Continúa procesando aunque algunos archivos fallen
- **Limpieza automática**: Elimina archivos temporales automáticamente  
- **Codificación UTF-8**: Soporte completo para caracteres especiales
- **Logging detallado**: Información completa del progreso en consola
- **Memoria eficiente**: Procesamiento archivo por archivo sin cargar todo en memoria

## 🔧 Integración con el scraper principal

Este procesador puede integrarse fácilmente con el scraper principal:

```python
from pdf_processor_renamer import PDFProcessorAndRenamer

# Después de descargar el ZIP
processor = PDFProcessorAndRenamer("descarga.zip", "salida")
success = processor.extraer_zip_y_procesar()

if success:
    reporte = processor.generar_reporte_excel_json()
    # Enviar archivos procesados por webhook...
```

## 📝 Notas importantes

- Los archivos PDF deben tener texto extraíble para que funcione la búsqueda de identificadores
- Si un PDF no tiene identificadores, se copia con su nombre original
- Los duplicados se manejan agregando sufijos numéricos (`_1`, `_2`, etc.)
- El procesamiento es seguro: nunca modifica los archivos originales

## 🐛 Solución de problemas

### "No se encontraron archivos PDF"
- Verifica que el ZIP contenga archivos con extensión .pdf
- Asegúrate de que el ZIP no esté corrupto

### "Error extrayendo texto"  
- El PDF puede estar protegido por contraseña
- El PDF puede ser solo imagen sin OCR

### "Sin identificadores encontrados"
- El PDF no contiene DNI/NIF/NIE en formato reconocible
- Verifica que el texto sea extraíble (no solo imagen)

---

**Desarrollado basándose en RPA_PODERES.PY para automatizar el procesamiento de documentos de ApudActa** 🤖
