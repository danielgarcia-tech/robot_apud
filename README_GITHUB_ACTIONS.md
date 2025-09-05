# GitHub Actions Workflow - ApudActa Scraper con Procesamiento PDF

## 🚀 Funcionalidades del Workflow

Este workflow de GitHub Actions ejecuta automáticamente el scraper de ApudActa con procesamiento completo de PDFs:

### ✨ Características Principales

- **🕰️ Ejecución Programada**: Todos los días a las 6:00 AM UTC
- **🔄 Ejecución Manual**: Via `workflow_dispatch` o modificando `start_scraper.txt`
- **📄 Procesamiento PDF Completo**: Extracción de identificadores DNI/NIF/NIE
- **📁 Organización Automática**: Separación en PODERES/ y SOLICITUDES/
- **🔐 Compresión Segura**: Archivos 7Z con password `Rua2025`
- **🧹 Limpieza Automática**: Solo conserva el archivo final procesado

## 🔧 Configuración

### Variables de Entorno Requeridas

```yaml
secrets:
  EMAIL: # Email de acceso a ApudActa
  PASSWORD: # Contraseña de ApudActa
  GITHUB_TOKEN: # Token automático de GitHub (pre-configurado)
```

### Dependencias Instaladas

- `playwright` - Automatización web
- `python-dotenv` - Gestión de variables de entorno
- `py7zr` - Compresión 7-Zip
- `PyMuPDF` - Procesamiento de PDFs
- `Pillow` - Procesamiento de imágenes
- `requests` - Peticiones HTTP

## 📋 Flujo de Trabajo

### 1. **Preparación del Entorno**
```bash
- Checkout del código
- Instalación de Python 3.11
- Instalación de dependencias
- Instalación de navegadores Playwright
```

### 2. **Ejecución del Scraper**
```bash
python easyday.py
```

**Proceso interno:**
- ✅ Autenticación en ApudActa
- 📥 Descarga de archivos disponibles  
- 🔍 Procesamiento de PDFs con extracción de identificadores
- 📁 Organización automática:
  - `PODERES/` → Archivos CertificadoRegistro
  - `SOLICITUDES/` → Archivos Solicitud_ApudActa
  - `Excel` → Archivos .xlsx en raíz
- 🏷️ Renombrado con prefijos PODER_ y SOLICITUD_
- 📦 Compresión en 7Z con password
- 🧹 Limpieza de archivos temporales

### 3. **Verificación de Resultados**
- 🔍 Detección de archivos `apudacta_procesado_*.7z`
- 📊 Cálculo de tamaños y estadísticas
- 📋 Preparación de metadatos

### 4. **Envío a Webhooks**
- 📡 Webhook principal de JustiFlow
- 📡 Webhook de test de JustiFlow  
- 📤 Incluye metadatos completos:
  - Password del archivo
  - Estructura de carpetas
  - Tipo de procesamiento
  - Timestamp y run_id

### 5. **Gestión de Artefactos**
- 📦 Upload de archivos procesados como artefactos
- ⏰ Retención de 7 días
- 🔗 Disponible para descarga manual

### 6. **Notificaciones Automáticas**
- ✅ **Success Issue**: Cuando el proceso es exitoso
- ⚠️ **No Files Issue**: Cuando no hay archivos para procesar
- ❌ **Error Issue**: Cuando ocurre algún fallo

## 📊 Estructura de Archivos Resultantes

```
apudacta_procesado_YYYYMMDD_HHMMSS.7z (🔐 Rua2025)
├── PODERES/
│   ├── PODER_12345678A_JUAN_PEREZ_2025-09-05_10-30-00.pdf
│   ├── PODER_87654321B_MARIA_GARCIA_2025-09-05_11-00-00.pdf
│   └── ...
├── SOLICITUDES/
│   ├── SOLICITUD_12345678A_JUAN_PEREZ_2025-09-05_10-30-00.pdf
│   ├── SOLICITUD_87654321B_MARIA_GARCIA_2025-09-05_11-00-00.pdf
│   └── ...
├── Solicitudes.xlsx
├── Solicitudes_backup.xlsx
└── ...
```

## 🔍 Monitoreo y Debug

### Issues Automáticos
- **Label `success`**: Ejecución exitosa con detalles del archivo
- **Label `no-files`**: Sin archivos disponibles 
- **Label `error`**: Fallos durante la ejecución
- **Label `pdf-processed`**: Incluye procesamiento PDF

### Logs Detallados
- 🔗 Enlace directo a los logs en cada issue
- 📊 Estadísticas de procesamiento
- 🔧 Información de debug para resolución de problemas

### Artefactos
- 📦 Archivos procesados disponibles por 7 días
- 📄 Logs de ejecución incluidos
- 💾 Descarga manual desde GitHub Actions

## ⚡ Triggers de Ejecución

1. **Programado**: `0 6 * * *` (6:00 AM UTC diariamente)
2. **Manual**: Button "Run workflow" en GitHub Actions  
3. **Push**: Modificar archivo `start_scraper.txt` en main
4. **API**: Via GitHub REST API con `workflow_dispatch`

## 🔧 Personalización

Para modificar el comportamiento:

1. **Horario**: Cambiar el cron en `schedule`
2. **Dependencias**: Modificar `Install Dependencies` step  
3. **Webhooks**: Actualizar URLs en `Send Processed Files to Webhook`
4. **Notificaciones**: Personalizar templates en los steps de Issues

## 📈 Mejoras Incluidas

- 🚀 **Procesamiento PDF integrado** vs versión anterior básica
- 🏷️ **Renombrado inteligente** con identificadores extraídos
- 📁 **Organización automática** en subcarpetas por tipo
- 🔐 **Seguridad mejorada** con compresión password-protected  
- 🧹 **Limpieza completa** manteniendo solo archivos finales
- 📊 **Metadatos enriquecidos** enviados a webhooks
- 📋 **Notificaciones detalladas** con más información

## 🔄 Versionado

- **v1.0**: Scraper básico con descarga simple
- **v2.0**: **ACTUAL** - Procesamiento PDF completo con organización

---

💡 **Tip**: Para forzar una ejecución inmediata, usa "Run workflow" en la pestaña Actions o modifica `start_scraper.txt`
