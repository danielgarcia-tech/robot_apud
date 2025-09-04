# ApudActa Scraper

Bot automatizado para descargar documentos desde la plataforma ApudActa con programación horaria.

## 🚀 Características

- ✅ **Login automático** en ApudActa
- ✅ **Descarga automática** de archivos 7Z protegidos con contraseña
- ✅ **Programación diaria** configurable
- ✅ **Envío automático por email** a danielgarcia@ruaabogados.es
- ✅ **Notificaciones inteligentes** (éxito/error/sin archivos)
- ✅ **Ejecución headless** sin ventana visible
- ✅ **Ultra rápido** con Playwright
- ✅ **Solo descarga fila 1** optimizado
- ✅ **Logging completo** de operaciones

## 📋 Requisitos

- Windows 10/11
- Python 3.8+ instalado
- Chrome/Chromium instalado
- Cuenta activa en ApudActa

## 🛠️ Instalación Rápida

1. **Descarga** el proyecto
2. **Doble click** en `instalar.bat`
3. **Edita** el archivo `.env` con tus credenciales
4. **¡Listo!** Ya puedes usar el scraper

## ⚙️ Configuración

### 1. Configurar Credenciales

Edita el archivo `.env` con tus datos:

```env
# Tu email y contraseña de ApudActa
EMAIL=tu_email@ejemplo.com
PASSWORD=tu_contraseña

# Configuración opcional
EXECUTION_TIME=09:00
HEADLESS=True
```

### 2. Carpetas del Proyecto

```
PROYECTO ROBOT APUD/
├── src/                 # Código fuente
├── descargas/          # Archivos descargados
├── logs/               # Archivos de log
├── .env               # Configuración (crear desde .env.example)
└── *.bat              # Scripts de ejecución
```

## 🎯 Uso

### Ejecución Automática (Recomendado)
```bash
# Doble click en:
ejecutar.bat
```
Esto iniciará el bot que se ejecutará automáticamente cada día a la hora configurada.

### Prueba Inmediata
```bash
# Doble click en:
probar.bat
```
Ejecuta el scraper inmediatamente para probar que todo funciona.

### Desde Terminal
```bash
# Activar entorno
venv\Scripts\activate

# Ejecución programada
python scheduler.py

# Ejecución inmediata
python scheduler.py --now
```

## 📊 Monitoreo

### Logs
Los logs se guardan en la carpeta `logs/` con información detallada de cada ejecución:
- Archivos descargados
- Errores y advertencias  
- Tiempo de ejecución
- Estado de las operaciones

### Reportes
Se generan reportes en Excel con:
- Lista de archivos descargados
- Fechas y tamaños
- Estado de cada descarga

## 🔧 Configuración Avanzada

### Archivo config.json
```json
{
  "scraper_config": {
    "max_retries": 3,
    "download_timeout": 300
  },
  "advanced": {
    "generate_daily_report": true,
    "cleanup_old_files": true
  }
}
```

### Variables de Entorno (.env)
```env
# Credenciales
EMAIL=tu_email@ejemplo.com
PASSWORD=tu_contraseña

# Rutas
DOWNLOAD_PATH=./descargas
LOG_PATH=./logs

# Horarios
EXECUTION_TIME=09:00

# Configuración del navegador
HEADLESS=True
IMPLICIT_WAIT=10
```

## 🚨 Solución de Problemas

### Error de Credenciales
- Verifica que el email y contraseña sean correctos
- Asegúrate de que tu cuenta esté activa

### ChromeDriver
- Se instala automáticamente con webdriver-manager
- Si hay problemas, reinicia después de instalar

### Descargas No Funcionan
- Verifica permisos de la carpeta `descargas/`
- Ejecuta como administrador si es necesario

### Logs para Debugging
Revisa los archivos en `logs/` para información detallada de errores.

## 📅 Programación con Tareas de Windows

Para que el bot se ejecute automáticamente al iniciar Windows:

1. Abrir **Programador de Tareas** de Windows
2. Crear tarea básica
3. Configurar para ejecutar diariamente
4. Acción: `ejecutar.bat`

## 🔒 Seguridad

- ⚠️ **NUNCA** compartas el archivo `.env`
- 🔐 Usa contraseñas seguras
- 📝 Revisa los logs regularmente
- 🗂️ Haz backup de la configuración

## 📝 Estructura de Archivos

```
PROYECTO ROBOT APUD/
├── src/
│   └── apudacta_scraper.py    # Scraper principal
├── logs/                       # Logs por fecha
├── descargas/                 # Archivos descargados
├── scheduler.py               # Programador
├── config.json               # Configuración avanzada
├── requirements.txt          # Dependencias Python
├── .env.example             # Plantilla de configuración
├── instalar.bat             # Instalador automático
├── ejecutar.bat             # Ejecutar programado
└── probar.bat              # Prueba inmediata
```

## 🆘 Soporte

Si tienes problemas:

1. Revisa los **logs** en la carpeta `logs/`
2. Verifica la **configuración** en `.env`
3. Ejecuta **prueba inmediata** con `probar.bat`
4. Consulta la **documentación** de errores comunes

## 📄 Licencia

Este proyecto es de uso personal/profesional. Respeta los términos de servicio de ApudActa.

---

## 📧 Configuración Gmail para Emails Automáticos

**Para envío automático de archivos por email:**

1. **Crear App Password en Gmail:**
   - Ve a Configuración → Verificación en 2 pasos → Contraseñas de aplicaciones
   - Seleccionar "Correo" → "Windows"
   - **Usar código de verificación:** `4149 8678`
   - Copiar la contraseña de 16 caracteres generada

2. **Configurar en GitHub:**
   - Secret `EMAIL_PASSWORD` con la contraseña generada
   - Secret `EMAIL` con `jesusoroza@ruaabogados.es`

3. **Ver guía completa:** `GMAIL_SETUP_GUIA.md`
4. **Configuración final:** `CONFIGURACION_FINAL.md`

**⚡ Bot desarrollado para automatizar descargas de ApudActa**
