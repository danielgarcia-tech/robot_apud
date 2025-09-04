@echo off
echo ========================================
echo  EASYDAY SCRAPER - MODO ULTRA SIMPLE
echo ========================================
echo.
echo Este scraper es ULTRA SIMPLIFICADO:
echo - Modo visible (puedes ver todo)
echo - Wait de 10 segundos entre pasos
echo - Sin TensorFlow ni complicaciones
echo - Proceso paso a paso
echo.

cd /d "C:\Users\DanielGarcíaCarabelo\Downloads\PROYECTO ROBOT APUD"

echo Activando entorno virtual...
call venv\Scripts\activate

echo.
echo Ejecutando EasyDay Scraper...
python easyday.py

echo.
echo Presiona cualquier tecla para cerrar...
pause > nul
