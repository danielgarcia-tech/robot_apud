@echo off
echo ===========================================
echo    EJECUTAR APUDACTA SCRAPER
echo ===========================================

::No necesitamos activar entorno virtual

:: Verificar si existe el archivo .env
if not exist ".env" (
    echo ERROR: No existe el archivo .env
    echo Por favor configura tus credenciales ejecutando instalar.bat
    pause
    exit /b 1
)

:: Ejecutar scheduler directamente
echo Iniciando scraper programado...
echo Presiona Ctrl+C para detener
echo.
python scheduler.py

pause
