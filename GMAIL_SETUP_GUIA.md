# 🔐 Configuración Gmail App Password - Guía Paso a Paso

## 📧 **PASOS PARA CONFIGURAR GMAIL APP PASSWORD**

### **Paso 1: Acceder a Configuración de Gmail**
1. Ve a **Gmail** en tu navegador
2. Click en tu foto/avatar (esquina superior derecha)
3. Seleccionar **"Configuración de Google"**

### **Paso 2: Verificación en 2 Pasos**
1. En el menú lateral: **"Seguridad"**
2. Buscar la sección **"Verificación en 2 pasos"**
3. Si no está activada, actívala primero

### **Paso 3: Contraseñas de Aplicación**
1. En la sección "Verificación en 2 pasos"
2. Desplázate hasta el final
3. Click en **"Contraseñas de aplicaciones"**

### **Paso 4: Generar Nueva Contraseña**
1. Seleccionar **"Correo"** como aplicación
2. Seleccionar **"Windows"** como dispositivo
3. Click en **"Generar"**

### **Paso 5: Código de Verificación**
```
INGRESA ESTE CÓDIGO CUANDO TE LO PIDAN:
4 1 4 9   8 6 7 8
```

### **Paso 6: Obtener la Contraseña**
1. Gmail generará una contraseña de **16 caracteres**
2. **Cópiala inmediatamente** (ejemplo: `abcd efgh ijkl mnop`)
3. **Guárdala en un lugar seguro**

**✅ TU CONTRASEÑA GENERADA:** `pqng soax span oque`

### **Paso 7: Configurar en GitHub**
1. Ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions**
2. Crear nuevo secret: `EMAIL_PASSWORD`
3. Pegar la contraseña de 16 caracteres generada

---

## ⚠️ **NOTAS IMPORTANTES**

### **¿Por qué necesitas esto?**
- Gmail bloquea el acceso desde aplicaciones externas por seguridad
- La "contraseña de aplicación" es específica para este uso
- Tu contraseña normal de Gmail sigue funcionando normalmente

### **¿Es seguro?**
- ✅ **Muy seguro** - solo funciona para envío de emails
- ✅ **Limitado** - no permite acceso completo a tu cuenta
- ✅ **Controlado** - puedes revocarlo en cualquier momento
- ✅ **Auditable** - Gmail registra todos los usos

### **¿Qué hacer si pierdes la contraseña?**
1. Ve a "Contraseñas de aplicaciones" en Gmail
2. Revoca la contraseña anterior
3. Genera una nueva
4. Actualiza el secret en GitHub

---

## 🔧 **VERIFICACIÓN DE CONFIGURACIÓN**

### **Para probar que funciona:**
1. Configura todos los secrets en GitHub
2. Ejecuta el workflow manualmente
3. Deberías recibir un email de prueba

### **Si hay problemas:**
- ✅ Verifica que el código `4149 8678` sea correcto
- ✅ Asegúrate de que la verificación en 2 pasos esté activada
- ✅ Confirma que copiaste la contraseña completa (16 caracteres)
- ✅ Revisa los logs de GitHub Actions para errores específicos

---

## 📞 **SOPORTE**

Si tienes problemas con la configuración de Gmail:
- Revisa la [ayuda oficial de Google](https://support.google.com/accounts/answer/185833)
- Contacta al soporte de Gmail
- O avísame para ayudarte con la configuración

---

## ✅ **CHECKLIST FINAL**

- [ ] Verificación en 2 pasos activada en Gmail
- [ ] Código de verificación `4149 8678` usado correctamente
- [ ] Contraseña de aplicación generada (16 caracteres)
- [ ] Secret `EMAIL_PASSWORD` configurado en GitHub
- [ ] Workflow probado manualmente
- [ ] Email de confirmación recibido

**¡Una vez completado, el sistema estará listo para enviar emails automáticamente!** 🎉</content>
<parameter name="filePath">c:\Users\DanielGarcíaCarabelo\Downloads\PROYECTO ROBOT APUD\GMAIL_SETUP_GUIA.md
