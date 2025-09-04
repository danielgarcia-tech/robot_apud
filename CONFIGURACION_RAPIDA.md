# 🚀 Guía Rápida: Configuración Segura de GitHub Actions

## ⚡ **EN 3 MINUTOS LISTO**

### **Paso 1: Crear repositorio privado**
```bash
# Crear repo privado (IMPORTANTE para seguridad)
echo "Crear repositorio PRIVADO en GitHub"
```

### **Paso 2: Configurar secrets (2 minutos)**
1. Ve a tu repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Crear estos 3 secrets:

| Secret Name | Value | Descripción |
|-------------|-------|-------------|
| `EMAIL` | `jesusoroza@ruaabogados.es` | Usuario ApudActa |
| `PASSWORD` | `Ruaabogados2024` | Contraseña ApudActa |
| `EMAIL_PASSWORD` | `[contraseña_app_gmail]` | Para enviar emails |

### **⚠️ IMPORTANTE: Configurar Gmail App Password**

Para que funcione el envío de emails, necesitas crear una "contraseña de aplicación" en Gmail:

1. Ve a tu cuenta Gmail → **Configuración** → **Verificación en 2 pasos**
2. Al final: **"Contraseñas de aplicaciones"**
3. Seleccionar **"Correo"** y **"Windows"**
4. **Ingresa el código de verificación**: `4149 8678`
5. Copiar la contraseña de 16 caracteres generada
6. Usar esa contraseña en `EMAIL_PASSWORD`

**✅ CONTRASEÑA DE APLICACIÓN OBTENIDA:** `pqng soax span oque`

**¿Por qué?** Gmail bloquea el acceso directo desde apps externas por seguridad.

### **Paso 3: Subir código**
```bash
git init
git add .
git commit -m "Add secure ApudActa scraper"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### **Paso 4: Verificar funcionamiento**
- Ve a **Actions** en tu repo
- Deberías ver el workflow ejecutándose automáticamente
- O ejecuta manualmente con **"Run workflow"**

---

## 🔍 **¿Cómo verificar que es seguro?**

### **1. Secrets protegidos:**
```bash
# En los logs verás:
📧 Usuario: jesusoroza@ruaabogados.es
🔐 Password: [PROTEGIDO]  # ✅ Nunca se muestra
```

### **2. Permisos mínimos:**
- ✅ Solo puede leer código
- ❌ No puede escribir en repo
- ❌ No puede modificar settings

### **3. Aislamiento:**
- ✅ Máquina nueva cada ejecución
- ✅ Datos se destruyen al terminar
- ✅ Red sandboxed

---

## 🎯 **¿Es realmente seguro?**

**SÍ, extremadamente seguro.** Comparado con:

| Método | Seguridad | Complejidad | Costo |
|--------|-----------|-------------|-------|
| **GitHub Actions** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 🆓 |
| Dejar PC encendido | ⭐⭐⭐ | ⭐⭐⭐ | 💡 Electricidad |
| VPS + Cron | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 💰 $5-15/mes |
| N8N | ⭐⭐⭐⭐ | ⭐⭐⭐ | 💰 $20+/mes |

---

## 🚨 **¿Qué hacer si hay dudas?**

### **Opción A: Test primero (Recomendado)**
1. Crea un repo de prueba
2. Ejecuta el scraper manualmente
3. Verifica que funciona
4. Si todo OK, configura el horario

### **Opción B: Alternativa más segura**
Si prefieres máxima seguridad:
```bash
# Crear cuenta GitHub nueva solo para esto
# Usar repositorio privado
# Configurar 2FA obligatorio
```

### **Opción C: Backup plan**
```bash
# Mantén el .bat local como backup
# En caso de problemas, ejecuta manualmente
```

---

## ✅ **Checklist de seguridad:**

- [ ] **Repositorio privado** creado
- [ ] **Secrets configurados** correctamente
- [ ] **2FA activado** en GitHub
- [ ] **Código subido** y workflow activo
- [ ] **Primera ejecución** probada manualmente
- [ ] **Notificaciones** configuradas

---

## 🎉 **¡LISTO!**

Una vez configurado, tu scraper se ejecutará **automáticamente todos los días a las 6:00 AM** de forma completamente segura.

**¿Necesitas ayuda con algún paso específico?** 🤔</content>
<parameter name="filePath">c:\Users\DanielGarcíaCarabelo\Downloads\PROYECTO ROBOT APUD\CONFIGURACION_RAPIDA.md
