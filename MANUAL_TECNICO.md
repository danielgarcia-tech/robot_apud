# 📖 Manual Técnico - ApudActa Robot Scraper

## 🎯 Tabla de Contenidos
1. [¿Qué es el ApudActa Robot?](#qué-es-el-apudacta-robot)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Funcionamiento Detallado](#funcionamiento-detallado)
4. [Automatización con GitHub Actions](#automatización-con-github-actions)
5. [Configuración y Variables de Entorno](#configuración-y-variables-de-entorno)
6. [Instalación y Configuración](#instalación-y-configuración)
7. [Troubleshooting](#troubleshooting)
8. [Mantenimiento](#mantenimiento)

---

## 🤖 ¿Qué es el ApudActa Robot?

El **ApudActa Robot Scraper** es un sistema automatizado de extracción, procesamiento y organización de documentos legales desde la plataforma ApudActa. Su objetivo principal es automatizar completamente el proceso de obtención de poderes notariales y documentos relacionados para el bufete jurídico RUA Abogados.

### 🎯 Objetivos Principales
- **Automatización Total**: Eliminar intervención manual en la descarga de documentos
- **Procesamiento Inteligente**: Análisis OCR para identificar DNI/NIE/NIF automáticamente
- **Organización Estructurada**: Clasificación automática por tipos de documentos
- **Seguridad**: Protección con contraseñas AES-256 en archivos comprimidos
- **Integración**: Envío automático a sistemas de gestión (JustiFlow)

### 📊 Flujo de Valor
```
ApudActa → Robot Scraper → Procesamiento PDF → Organización → Compresión → JustiFlow
```

---

## 🏗️ Arquitectura del Sistema

### 📁 Estructura de Archivos
```
PROYECTO ROBOT APUD/
├── easyday.py                     # Script principal - Motor del sistema
├── scheduler.py                   # Programador de tareas (uso local)
├── pdf_processor_renamer.py       # Procesador independiente de PDFs
├── requirements.txt               # Dependencias de Python
├── README.md                      # Documentación básica
├── start_scraper.txt             # Trigger para GitHub Actions
├── .env                          # Variables de entorno (no incluido)
├── .github/workflows/
│   └── apudacta-scraper.yml      # Configuración de GitHub Actions
├── descargas/                     # Carpeta temporal de descargas
├── logs/                         # Logs del sistema
└── procesados/                   # Archivos procesados y organizados
    ├── PODERES/                  # Certificados de Registro
    ├── SOLICITUDES/              # Solicitudes ApudActa
    └── *.xlsx                    # Archivos Excel
```

### 🔧 Componentes Principales

#### 1. **EasyDayScraper** (easyday.py)
- **Motor Principal**: Coordina todo el proceso de automatización
- **Web Scraping**: Utiliza Playwright para navegación automatizada
- **Autenticación**: Login automático con credenciales seguras
- **Descarga Selectiva**: Solo descarga el archivo más reciente (fila 1)

#### 2. **Procesador PDF**
- **OCR Avanzado**: PyMuPDF para extracción de texto de documentos
- **Detección de Identificadores**: Regex patterns para DNI/NIE/NIF
- **Renombrado Inteligente**: Convenciones automáticas de nomenclatura
- **Clasificación**: Organización por tipo de documento

#### 3. **Sistema de Compresión**
- **7-Zip Integration**: Archivos .7z con contraseña
- **Seguridad AES-256**: Protección robusta con contraseña "Rua2025"
- **Estructura Preservada**: Mantiene organización de carpetas

#### 4. **GitHub Actions Workflow**
- **Ejecución Diaria**: Cron schedule a las 6:00 UTC (7:00 en España)
- **Infraestructura en la Nube**: Ubuntu runners con todas las dependencias
- **Webhook Integration**: Envío automático a JustiFlow
- **Artifact Management**: Retención de archivos por 7 días
LO IMPORTANTE, VER EL YML
---

## ⚙️ Funcionamiento Detallado

### 🔄 Proceso Paso a Paso

#### **Fase 1: Inicialización (0-5 segundos)**
1. **Configuración de Entorno**
   ```python
   # Variables clave
   email = 'jesusoroza@ruaabogados.es'
   password = ''
   archive_password = '""""'
   ```

2. **Creación de Directorios**
   - `./descargas/` - Archivos temporales
   - `./procesados/` - Output organizado

#### **Fase 2: Autenticación (5-10 segundos)**
1. **Inicialización del Navegador**
   ```python
   # Playwright en modo headless
   playwright = sync_playwright().start()
   browser = playwright.chromium.launch(headless=True)
   ```

2. **Login Automatizado**
   - URL: `https://app.apudacta.com/login/`
   - Campos: email y password automáticos
   - Verificación de éxito de login

#### **Fase 3: Navegación (10-15 segundos)**
1. **Acceso a APODERAMIENTOS**
   - Navegación por menús de la plataforma
   - Acceso a sección "Descargas Zip"

2. **Identificación de Archivos**
   - Escaneo de tabla de archivos disponibles
   - Selección **SOLO del primer archivo** (más reciente)

#### **Fase 4: Descarga (15-30 segundos)**
1. **Descarga Controlada**
   ```python
   # Solo la fila 1 (más reciente)
   download_button = rows[0].query_selector("span.cursor-pointer")
   with page.expect_download() as download_info:
       download_button.click()
   ```

2. **Gestión de Archivos**
   - Descarga temporal del ZIP original
   - Verificación de integridad

#### **Fase 5: Procesamiento PDF (30-120 segundos)**
1. **Extracción de ZIP**
   ```python
   with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
       zip_ref.extractall(temp_extract_path)
   ```

2. **Análisis OCR de PDFs**
   ```python
   def extract_text_from_pdf(pdf_path):
       doc = fitz.open(pdf_path)
       text = ""
       for page in doc:
           text += page.get_text()
       return text
   ```

3. **Detección de Identificadores**
   ```python
   # Patrones de identificación
   dni_pattern = r'\b\d{8}[A-Z]\b'                    # DNI español
   nie_pattern = r'\b[XYZ]\d{7}[A-Z]\b'               # NIE
   nif_pattern = r'\b[A-Z]\d{7}[A-Z]\b'               # NIF empresas
   ```

4. **Renombrado Inteligente**
   - `certificado_registro_*.pdf` → `PODER_{DNI}.pdf`
   - `solicitud_*.pdf` → `SOLICITUD_{DNI}.pdf`

#### **Fase 6: Organización (120-150 segundos)**
1. **Estructura Final**
   ```
   apudacta_procesado_YYYYMMDD_HHMMSS/
   ├── PODERES/
   │   ├── PODER_12345678A.pdf
   │   └── PODER_87654321B.pdf
   ├── SOLICITUDES/
   │   ├── SOLICITUD_12345678A.pdf
   │   └── SOLICITUD_87654321B.pdf
   ├── Solicitudes_YYYY-MM-DD.xlsx
   └── reporte_procesamiento_YYYYMMDD_HHMMSS.json
   ```

#### **Fase 7: Compresión y Seguridad (150-180 segundos)**
1. **Creación de Archivo 7Z**
   ```python
   with py7zr.SevenZipFile(protected_path, 'w', password='') as archive:
       archive.write(organized_folder, arcname=os.path.basename(organized_folder))
   ```

2. **Verificación de Integridad**
   - Test de contraseña
   - Verificación de estructura

#### **Fase 8: Envío e Integración (180-210 segundos)**
1. **Webhook a JustiFlow**
   ```bash
   curl -F "file=@archivo_final.7z" \
        -F "source=ApudActa-PDF" \
        https://justiflow.com/webhook/poderes
   ```

2. **Cleanup Final**
   - Eliminación de archivos temporales
   - Preservación solo del archivo 7Z final

---

## 🚀 Automatización con GitHub Actions

### ⏰ Programación Diaria

El sistema está configurado para ejecutarse automáticamente **todos los días a las 6:00 UTC** (7:00 hora española) mediante GitHub Actions.

#### **Configuración del Workflow**

```yaml
name: ApudActa Scraper with PDF Processing

on:
  schedule:
    - cron: '0 6 * * *'  # 6:00 UTC diariamente
  workflow_dispatch:      # Ejecución manual
  push:
    branches: [ main ]
    paths:
      - 'start_scraper.txt'  # Trigger manual via commit
```

#### **Pasos de Ejecución**

1. **Setup del Entorno (30-60 segundos)**
   ```yaml
   - name: Setup Python
     uses: actions/setup-python@v4
     with:
       python-version: '3.11'
   
   - name: Install System Dependencies
     run: |
       sudo apt-get update
       sudo apt-get install -y python3-dev libmupdf-dev libfreetype6-dev
   ```

2. **Instalación de Dependencias (60-120 segundos)**
   ```yaml
   - name: Install Dependencies
     run: |
       pip install -r requirements.txt
       playwright install chromium
   ```

3. **Ejecución Principal (300-1500 segundos)**
   ```yaml
   - name: Run ApudActa Scraper
     env:
       EMAIL: ${{ secrets.EMAIL }}
       PASSWORD: ${{ secrets.PASSWORD }}
     run: |
       timeout 25m python easyday.py || exit 1
   ```

4. **Post-procesamiento (30-60 segundos)**
   ```yaml
   - name: Send to Webhook
     run: |
       curl -F "file=@*.7z" -F "source=ApudActa-PDF" \
         https://justiflow.com/webhook/poderes
   ```

### 🔄 Métodos de Activación

#### 1. **Automático (Diario)**
- **Horario**: 6:00 UTC / 7:00 España
- **Frecuencia**: Todos los días del año
- **Sin intervención manual requerida**

#### 2. **Manual via GitHub UI**
- Ir a GitHub → Actions → ApudActa Scraper
- Click en "Run workflow"
- Seleccionar branch main
- Click "Run workflow"

#### 3. **Trigger via Commit**
- Modificar el archivo `start_scraper.txt`
- Commit y push a main
- Se ejecuta automáticamente

### 📊 Monitoreo y Alertas

#### **Logs y Artifacts**
```yaml
- name: Upload Artifacts
  uses: actions/upload-artifact@v4
  with:
    name: apudacta-processed-files
    path: |
      "*.7z"
      "poderes.zip"
    retention-days: 7
```

#### **Issues Automáticos**
- **Success**: Issue creado automáticamente cuando el proceso es exitoso
- **Failure**: Issue de error con detalles del problema
- **Labels**: Clasificación automática (success/error)

---

## 🔧 Configuración y Variables de Entorno

### 🔐 Variables Secretas (GitHub)

En GitHub → Settings → Secrets and variables → Actions:

```
EMAIL=jesusoroza@ruaabogados.es
PASSWORD=""""
```

### 🔧 Configuración Local

#### **Archivo .env** (para desarrollo local)
```bash
# Credenciales ApudActa
EMAIL=jesusoroza@ruaabogados.es
PASSWORD=""

# Configuración de timeouts
WAIT_BETWEEN_STEPS=0.5
DOWNLOAD_WAIT=2

# Contraseña para archivos protegidos
ARCHIVE_PASSWORD=Rua2025

# Webhooks
WEBHOOK_TEST=https://justiflow.com/webhook-test/99305ca7-ec18-465a-b192-05f3708387b4
WEBHOOK_PROD=https://justiflow.com/webhook/poderes
```

### ⚙️ Configuraciones Avanzadas

#### **Timeouts y Esperas**
```python
wait_between_steps = 0.5    # Segundos entre pasos de navegación
download_wait = 2           # Segundos específicos para descarga
timeout_global = 25         # Minutos máximo total (GitHub Actions)
```

#### **Paths y Directorios**
```python
download_path = './descargas'      # Archivos temporales
processed_path = './procesados'    # Output final
log_path = './logs'               # Logs del sistema
```

---

## 💻 Instalación y Configuración

### 🐍 Requisitos del Sistema

#### **Python y Dependencias**
```bash
Python 3.11+
pip 23.0+
```

#### **Dependencias Principales**
```txt
selenium==4.15.0          # Web automation (backup)
playwright==1.40.0        # Web automation (principal)
PyMuPDF>=1.23.20          # Procesamiento PDF
py7zr==0.21.0            # Compresión 7Z
requests==2.31.0         # HTTP requests
beautifulsoup4==4.12.2   # HTML parsing
python-dotenv==1.0.0     # Variables de entorno
Pillow>=10.1.0           # Procesamiento de imágenes
```

### 🚀 Setup Local

#### **1. Clonar el Repositorio**
```bash
git clone [REPOSITORY_URL]
cd "PROYECTO ROBOT APUD"
```

#### **2. Instalar Dependencias**
```bash
# Crear entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Instalar navegadores para Playwright
playwright install chromium
```

#### **3. Configurar Variables de Entorno**
```bash
# Crear archivo .env
echo EMAIL=jesusoroza@ruaabogados.es >> .env
echo PASSWORD="" >> .env
```

#### **4. Verificar Instalación**
```bash
# Test básico
python -c "import fitz; print('PyMuPDF OK')"
python -c "import playwright; print('Playwright OK')"
python -c "import py7zr; print('7Z OK')"
```

### 🔧 Setup en GitHub

#### **1. Fork/Crear Repositorio**
- Fork del repositorio original
- O crear nuevo repositorio con los archivos

#### **2. Configurar Secrets**
```
GitHub → Settings → Secrets → Actions
```
- `EMAIL`: jesusoroza@ruaabogados.es
- `PASSWORD`: ""

#### **3. Habilitar Actions**
```
GitHub → Actions → Enable workflows
```

#### **4. Test Manual**
- Actions → ApudActa Scraper → Run workflow

---

## 🐛 Troubleshooting

### ❌ Problemas Comunes

#### **1. Error de Login**
```
Síntoma: "❌ Error en login" o timeout en autenticación
Causa: Credenciales incorrectas o cambios en la web
Solución:
- Verificar EMAIL y PASSWORD en secrets
- Comprobar si ApudActa cambió la página de login
- Revisar logs para mensajes específicos
```

#### **2. Error de Descarga**
```
Síntoma: "⚠️ No se encontraron archivos para descargar"
Causa: No hay archivos nuevos o cambios en la interfaz
Solución:
- Verificar manualmente si hay archivos en ApudActa
- Revisar si cambió la estructura de la tabla
- Modificar selectores CSS si es necesario
```

#### **3. Error de Procesamiento PDF**
```
Síntoma: "❌ Error procesando PDF" o archivos corruptos
Causa: PDF protegido o formato no estándar
Solución:
- Verificar que el PDF no esté protegido
- Comprobar logs de PyMuPDF
- Revisar patrones de identificación DNI/NIE
```

#### **4. Timeout en GitHub Actions**
```
Síntoma: Workflow cancelado por timeout (25 minutos)
Causa: Proceso lento o bloqueado
Solución:
- Revisar logs completos del workflow
- Optimizar tiempos de espera
- Dividir proceso en steps más pequeños
```

### 🔍 Diagnóstico

#### **Logs Locales**
```bash
# Ejecutar en modo verbose
python easyday.py --verbose

# Revisar logs
cat logs/scheduler_$(date +%Y%m%d).log
```

#### **GitHub Actions Logs**
```
GitHub → Actions → [Failed run] → [Step details]
```

#### **Webhook Testing**
```bash
# Test webhook manual
curl -F "file=@test.7z" \
     -F "source=ApudActa-TEST" \
     https://justiflow.com/webhook-test/99305ca7-ec18-465a-b192-05f3708387b4
```

---

## 🔄 Mantenimiento

### 📅 Tareas Regulares

#### **Semanal**
- ✅ Verificar ejecuciones exitosas en GitHub Actions
- ✅ Revisar issues automáticos generados
- ✅ Comprobar integridad de archivos en JustiFlow

#### **Mensual**
- 🔄 Actualizar dependencias de Python
- 🔄 Revisar credenciales y expiración
- 🔄 Validar patrones de detección DNI/NIE

#### **Trimestral**
- 📊 Análisis de rendimiento y optimización
- 🔐 Rotación de contraseñas de archivos
- 📈 Revisión de métricas y estadísticas

### 🔄 Actualizaciones

#### **Dependencias**
```bash
# Actualizar requirements.txt
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

#### **Playwright Browsers**
```bash
# Actualizar navegadores
playwright install chromium
```

### 🔐 Seguridad

#### **Credenciales**
- Rotación periódica de contraseñas
- Verificación de acceso a ApudActa
- Monitoreo de logs de autenticación

#### **Archivos**
- Verificación de integridad de archivos 7Z
- Test de contraseñas de compresión
- Validación de estructura de carpetas

### 📊 Métricas y KPIs

#### **Indicadores de Éxito**
- **Tasa de Éxito**: > 95% de ejecuciones exitosas
- **Tiempo de Procesamiento**: < 20 minutos por ejecución
- **Archivos Procesados**: Tracking diario de volumen
- **Detección OCR**: > 90% de identificadores detectados correctamente

#### **Alertas Automáticas**
- Fallos consecutivos > 2 días
- Timeouts > 20 minutos
- Errores de webhook
- Archivos sin identificadores detectados

---

## 📞 Soporte y Contacto

### 🆘 En Caso de Problemas

1. **Revisar este manual técnico** para problemas comunes
2. **Consultar logs** de GitHub Actions o locales
3. **Verificar estado** de la plataforma ApudActa
4. **Contactar** al equipo técnico de RUA Abogados

### 📧 Información de Contacto

**Desarrollador**: Equipo IT RUA Abogados
**Email Soporte**: danielgarcia@ruaabogados.es
**Documentación**: Este manual técnico

GH ACTIONS VINCULADO A USUARIO DANIELGARCIA@RUAABOGADOS.ES 
REPO https://github.com/danielgarcia-tech/robot_apud

---

## 📝 Notas Finales

### 🎯 Resumen Ejecutivo

El ApudActa Robot Scraper es una solución completa y automatizada que:

1. **Se ejecuta diariamente** sin intervención manual
2. **Procesa inteligentemente** documentos PDF con OCR
3. **Organiza automáticamente** archivos por categorías
4. **Protege con contraseñas** toda la información
5. **Integra perfectamente** con sistemas existentes (JustiFlow)

### 🚀 Valor para RUA Abogados

- **Ahorro de Tiempo**: 30+ minutos diarios automatizados
- **Reducción de Errores**: Eliminación de factor humano
- **Trazabilidad Completa**: Logs y reportes automáticos
- **Seguridad Mejorada**: Protección robusta de datos
- **Escalabilidad**: Fácil adaptación a volúmenes crecientes






**📅 Última actualización**: ENERO 2026  
**🔢 Versión**: 2.0  
**👨‍💻 Mantenido por**: Equipo IT RUA Abogados


