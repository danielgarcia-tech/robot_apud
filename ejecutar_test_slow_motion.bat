@echo off
echo ========================================
echo  PRUEBA - SCRAPER CON SLOW MOTION
echo ========================================
echo.

cd /d "C:\Users\DanielGarcíaCarabelo\Downloads\PROYECTO ROBOT APUD"

echo Activando entorno virtual...
call venv\Scripts\activate

echo.
echo Ejecutando prueba con slow motion...
python test_slow_motion.py

echo.
echo Presiona cualquier tecla para cerrar...
pause > nul
