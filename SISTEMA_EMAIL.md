# 📧 Sistema de Notificaciones por Email

## #### **Gmail App Pa#### **Secrets Requeridos:**
```yaml
EMAIL: jesusoroza@ruaabogados.es          # Usuario ApudActa
PASSWORD: Ruaabogados2024               # Contraseña ApudActa  
EMAIL_PASSWORD: pqng soax span oque      # ✅ CONTRASEÑA OBTENIDA
``` (Obligatorio)**
```bash
# PASOS PARA CONFIGURAR:
1. Ir a Gmail → Configuración → Verificación en 2 pasos
2. Al final: "Contraseñas de aplicaciones"
3. Seleccionar "Correo" → "Windows"
4. INGRESAR CÓDIGO DE VERIFICACIÓN: 4149 8678
5. Copiar contraseña de 16 caracteres generada
6. Usar en EMAIL_PASSWORD secret
```ionalidades del Sistema de Email**

### **1. 📦 Envío Diario Automático**
- ✅ **Archivo adjunto**: El 7Z descargado se envía automáticamente
- ✅ **Destinatario**: danielgarcia@ruaabogados.es
- ✅ **Asunto descriptivo**: Incluye fecha y detalles
- ✅ **Cuerpo informativo**: Detalles completos de la descarga

### **2. 🔔 Tipos de Notificaciones**

#### **📧 Email de Éxito (con archivo adjunto)**
```
Asunto: 📦 ApudActa - Archivo diario 2025-09-04

Contenido:
- Archivo descargado exitosamente
- Nombre del archivo
- Tamaño del archivo
- Fecha y hora de descarga
- Archivo 7Z adjunto
```

#### **⚠️ Email cuando no hay archivos**
```
Asunto: ⚠️ ApudActa - No se encontraron archivos 2025-09-04

Contenido:
- Notificación de que no hay archivos nuevos
- Posibles razones
- Confirmación de que el scraper sigue funcionando
```

#### **❌ Email de Error**
```
Asunto: ❌ Error en ApudActa Scraper - [número de ejecución]

Contenido:
- Detalles del error
- Fecha y hora
- Link a los logs completos
- Próximo intento automático
```

### **3. 🔐 Configuración de Seguridad**

#### **Gmail App Password (Obligatorio)**
```bash
# PASOS PARA CONFIGURAR:
1. Ir a Gmail → Configuración → Verificación en 2 pasos
2. Al final: "Contraseñas de aplicaciones"
3. Seleccionar "Correo" → "Windows"
4. Copiar contraseña de 16 caracteres
5. Usar en EMAIL_PASSWORD secret
```

#### **Secrets Requeridos:**
```yaml
EMAIL: jesusoroza@ruaabogados.es      # Usuario ApudActa
PASSWORD: Ruaabogados2024           # Contraseña ApudActa
EMAIL_PASSWORD: [app_password_16_chars]  # Para envío de emails
```

### **4. 📊 Información Incluida en Emails**

#### **Email de Éxito:**
- ✅ Fecha y hora exacta
- ✅ Nombre del archivo descargado
- ✅ Tamaño del archivo
- ✅ Estado de la descarga
- ✅ Archivo ZIP adjunto **protegido con contraseña**
- ✅ **Contraseña incluida en el email: Rua2025**

#### **Email Informativo:**
- ✅ Fecha de ejecución
- ✅ Hora UTC
- ✅ Estado del proceso
- ✅ Número de archivos encontrados
- ✅ Link a logs si hay problemas

### **5. ⏰ Horarios de Notificación**

- **Diario**: 6:00 AM UTC (7:00 AM Madrid invierno / 8:00 AM verano)
- **Inmediato**: Notificación de error si falla
- **Condicional**: Solo notificación de "sin archivos" cuando corresponde

### **6. 🎯 Beneficios del Sistema**

#### **Para Daniel:**
- ✅ **Recibe archivos automáticamente** sin hacer nada
- ✅ **Notificaciones inteligentes** solo cuando es necesario
- ✅ **Información completa** en cada email
- ✅ **Archivos seguros** adjuntos directamente

#### **Para el Sistema:**
- ✅ **Monitoreo automático** del funcionamiento
- ✅ **Alertas tempranas** de problemas
- ✅ **Auditoría completa** de descargas
- ✅ **Sin intervención manual** requerida

### **7. 🔧 Configuración Técnica**

#### **Servidor SMTP:**
```yaml
server_address: smtp.gmail.com
server_port: 465
username: ${{ secrets.EMAIL }}
password: ${{ secrets.EMAIL_PASSWORD }}
```

#### **Condiciones de Envío:**
```yaml
# Solo enviar con archivo
if: success() && archivo_existe

# Solo enviar sin archivos
if: success() && no_hay_archivos

# Solo enviar en error
if: failure()
```

### **8. 📈 Estadísticas y Monitoreo**

#### **Métricas Incluidas:**
- 📅 Fecha de ejecución
- ⏱️ Hora exacta
- 📁 Número de archivos
- 📊 Tamaño total
- ✅ Estado de éxito/error

#### **Historial:**
- ✅ Logs completos en GitHub Actions
- ✅ Historial de emails enviados
- ✅ Estadísticas de descargas
- ✅ Tasa de éxito del proceso

### **9. 🚨 Manejo de Errores**

#### **Escenarios Cubiertos:**
- ❌ Fallo en login de ApudActa
- ❌ Error en descarga de archivo
- ❌ Problemas de conexión
- ❌ Credenciales expiradas
- ❌ Cambios en interfaz web

#### **Respuesta Automática:**
- 📧 Email inmediato de error
- 🔗 Link directo a logs
- 📝 Detalles del problema
- ⏰ Próximo intento automático

### **10. 💡 Mejores Prácticas**

#### **Recomendaciones:**
- ✅ **Revisar emails diariamente** las primeras semanas
- ✅ **Configurar filtros** en Gmail para organizar
- ✅ **Guardar archivos importantes** inmediatamente
- ✅ **Reportar problemas** si ocurren frecuentemente

#### **Optimizaciones:**
- ✅ **Archivos se eliminan** después de 7 días por seguridad
- ✅ **Adjuntos optimizados** para tamaño
- ✅ **Emails concisos** pero informativos
- ✅ **Asuntos descriptivos** para fácil identificación

---

## 🎉 **Resultado Final**

**Daniel recibirá automáticamente:**
- 📦 **Archivo ZIP diario** adjunto en email
- 🔔 **Notificaciones inteligentes** solo cuando necesario
- 📊 **Información completa** de cada descarga
- ✅ **Sistema 100% automático** sin intervención

**¡El scraper ahora es completamente autónomo!** 🤖✨</content>
<parameter name="filePath">c:\Users\DanielGarcíaCarabelo\Downloads\PROYECTO ROBOT APUD\SISTEMA_EMAIL.md
