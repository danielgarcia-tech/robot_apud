@echo off
echo ===========================================
echo    DEMO DEL SCRAPER APUDACTA
echo ===========================================
echo.
echo Este demo te mostrará paso a paso lo que hace el scraper:
echo.
echo 1. Configurar el navegador Chrome
echo 2. Hacer login en ApudActa
echo 3. Navegar a la sección de descargas
echo 4. Buscar archivos disponibles
echo 5. Mostrar lista de archivos encontrados
echo 6. (Opcional) Descargar archivos
echo 7. Generar reporte
echo.
echo IMPORTANTE: Antes de ejecutar, configura tu email y contraseña
echo en el archivo .env
echo.
pause

:: Ejecutar demo
python demo.py

pause
