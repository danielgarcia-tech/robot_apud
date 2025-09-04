@echo off
echo ===========================================
echo    INSTALADOR DE APUDACTA SCRAPER
echo ===========================================

:: Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

echo Python encontrado correctamente

:: Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip

:: Instalar dependencias directamente en el sistema
echo Instalando dependencias...
python -m pip install -r requirements.txt

:: Crear archivo .env si no existe
if not exist ".env" (
    echo Creando archivo de configuración...
    copy .env.example .env
    echo.
    echo IMPORTANTE: Edita el archivo .env con tus credenciales
    echo antes de ejecutar el scraper.
)

echo.
echo ===========================================
echo    INSTALACIÓN COMPLETADA
echo ===========================================
echo.
echo Para ejecutar el scraper:
echo   1. Edita el archivo .env con tus credenciales
echo   2. Ejecuta: python scheduler.py
echo   3. Para prueba inmediata: python scheduler.py --now
echo.
pause
