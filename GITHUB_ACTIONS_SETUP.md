# 🚀 ApudActa Scraper - Configuración GitHub Actions

## 📋 Pasos para configurar la ejecución diaria:

### 1. 📂 Subir proyecto a GitHub
```bash
git init
git add .
git commit -m "Initial commit - ApudActa Scraper"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

### 2. 🔐 Configurar secrets en GitHub
Ve a tu repositorio en GitHub → Settings → Secrets and variables → Actions

**Crear estos secrets:**
- `EMAIL`: jesusoroza@ruaabogados.es
- `PASSWORD`: Ruaabogados2024
- `EMAIL_PASSWORD`: (contraseña de aplicación de Gmail para notificaciones)

### 3. ⏰ Horario de ejecución
- **Configurado:** 6:00 AM UTC todos los días
- **Madrid:** 7:00 AM (invierno) / 8:00 AM (verano)

### 4. 🎛️ Controles disponibles

#### Ejecución manual:
- Ve a Actions → Daily ApudActa Scraper
- Click en "Run workflow"

#### Modificar horario:
Edita `.github/workflows/daily-scraper.yml`:
```yaml
schedule:
  - cron: '0 6 * * *'  # Cambiar hora aquí
```

**Ejemplos de horarios:**
- `'0 5 * * *'` = 5:00 AM UTC
- `'30 6 * * *'` = 6:30 AM UTC
- `'0 6 * * 1-5'` = 6:00 AM solo lunes a viernes

### 5. 📥 Descargar archivos
Los archivos descargados se guardan como "artifacts" en GitHub:
- Ve a Actions → tu ejecución
- Descarga "apudacta-downloads-XXX.zip"

### 6. 📧 Notificaciones
- ✅ Email automático si hay errores
- 📊 Logs detallados de cada ejecución
- 🔔 GitHub te notifica por email/web

## 🆚 Comparación de opciones:

| Opción | Costo | Configuración | Confiabilidad |
|--------|-------|---------------|---------------|
| **GitHub Actions** | 🆓 Gratis | ⭐⭐⭐ Fácil | ⭐⭐⭐⭐⭐ Excelente |
| N8N Cloud | 💰 $20/mes | ⭐⭐ Media | ⭐⭐⭐⭐ Buena |
| VPS + Cron | 💰 $5-15/mes | ⭐ Difícil | ⭐⭐⭐ Variable |

## 🎯 Ventajas de GitHub Actions:
- ✅ **100% gratis** para uso personal
- ✅ **Sin servidores** que mantener
- ✅ **Logs completos** de cada ejecución
- ✅ **Notificaciones** automáticas
- ✅ **Descarga fácil** de archivos
- ✅ **Ejecución manual** cuando quieras
- ✅ **Muy confiable** - infraestructura de Microsoft

## 🚀 Para activarlo:
1. Sube el código a GitHub
2. Configura los secrets
3. ¡Automáticamente se ejecutará todos los días a las 6:00 AM!
