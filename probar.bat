@echo off
echo ===========================================
echo    PRUEBA INMEDIATA - APUDACTA SCRAPER
echo ===========================================

::No necesitamos activar entorno virtual

:: Verificar si existe el archivo .env
if not exist ".env" (
    echo ERROR: No existe el archivo .env
    echo Por favor configura tus credenciales ejecutando instalar.bat
    pause
    exit /b 1
)

:: Ejecutar scraper inmediatamente
echo Ejecutando scraper inmediatamente...
echo.
python scheduler.py --now

echo.
echo Proceso completado. Revisa la carpeta 'descargas' y 'logs'
pause
