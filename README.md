# 🤖 ApudActa Robot - Scraper Automatizado con Procesamiento PDF

Automatización completa para extraer, procesar y organizar documentos de ApudActa con análisis OCR y organización inteligente.

## ✨ Características

- 🌐 **Scraping Automatizado**: Extrae archivos ZIP de ApudActa
- 📄 **Procesamiento PDF**: Análisis OCR con PyMuPDF
- 🆔 **Detección de Identificadores**: Reconoce DNI/NIE/NIF automáticamente
- 📁 **Organización Inteligente**: 
  - `PODERES/` → Certificados de Registro
  - `SOLICITUDES/` → Solicitudes ApudActa
  - Archivos Excel en la raíz
- 🔐 **Compresión Protegida**: Archivos 7Z con contraseña AES-256
- ☁️ **Ejecución Automatizada**: GitHub Actions con cron diario
- 🪝 **Integración Webhook**: Envío automático a JustiFlow
- 🧹 **Limpieza Automática**: Solo conserva archivos finales

## 🚀 Uso Rápido

### Ejecución Local
```bash
python easyday.py
```

### Ejecución Automática
El sistema se ejecuta automáticamente todos los días a las 6:00 UTC mediante GitHub Actions.

## 📋 Requisitos

```txt
selenium==4.15.0
playwright==1.40.0
PyMuPDF>=1.23.20
py7zr==0.21.0
requests==2.31.0
beautifulsoup4==4.12.2
```

## ⚙️ Configuración

1. **Variables de Entorno**:
   ```bash
   EMAIL=tu_email@ejemplo.com
   PASSWORD=tu_contraseña
   ```

2. **Contraseña 7Z**: `Rua2025`

3. **Webhooks JustiFlow**:
   - Test: `https://justiflow.com/webhook-test/99305ca7-ec18-465a-b192-05f3708387b4`
   - Prod: `https://justiflow.com/webhook/99305ca7-ec18-465a-b192-05f3708387b4`

## 📊 Flujo de Trabajo

1. **Login** → ApudActa con credenciales
2. **Navegación** → Sección APODERAMIENTOS → Descargas Zip
3. **Descarga** → Primer archivo disponible
4. **Extracción** → Descomprime ZIP descargado
5. **Análisis OCR** → Extrae texto de todos los PDFs
6. **Detección** → Identifica DNI/NIE/NIF en documentos
7. **Renombrado** → `PODER_DNI.pdf` y `SOLICITUD_DNI.pdf`
8. **Organización** → Estructura de carpetas final
9. **Compresión** → Archivo 7Z protegido con contraseña
10. **Envío** → Webhook a JustiFlow con archivo final
11. **Limpieza** → Eliminación de archivos temporales

## 🏗️ Estructura de Salida

```
apudacta_procesado_YYYYMMDD_HHMMSS.7z
├── PODERES/
│   ├── PODER_12345678A.pdf
│   └── PODER_87654321B.pdf
├── SOLICITUDES/
│   ├── SOLICITUD_12345678A.pdf
│   └── SOLICITUD_87654321B.pdf
├── Solicitudes_YYYY-MM-DD.xlsx
└── reporte_procesamiento_YYYYMMDD_HHMMSS.json
```

## 🔧 Desarrollo

### Archivos Principales
- `easyday.py`: Script principal con todas las funcionalidades
- `pdf_processor_renamer.py`: Procesador PDF independiente
- `scheduler.py`: Programación de tareas
- `start_scraper.txt`: Trigger para GitHub Actions

### GitHub Actions
- Workflow: `.github/workflows/apudacta-scraper.yml`
- Ejecución: Diaria a las 6:00 UTC
- Timeout: 25 minutos máximo
- Artifacts: 7 días de retención

## 📈 Estadísticas

- **Identificadores soportados**: DNI, NIE, NIF
- **Formatos**: `12345678A`, `X1234567A`, `Y1234567A`, etc.
- **Detección OCR**: Automática con fallback
- **Compresión**: AES-256 con contraseña
- **Procesamiento**: Hasta 100+ archivos por ejecución

---
 | ⏰ **Ejecución**: 6:00 UTC diario | 🎯 **Estado**: Producción
