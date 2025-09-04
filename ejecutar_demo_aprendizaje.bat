@echo off
echo ========================================
echo  DEMO - APRENDIZAJE INTERACTIVO
echo ========================================
echo.

cd /d "C:\Users\DanielGarcíaCarabelo\Downloads\PROYECTO ROBOT APUD"

echo Activando entorno virtual...
call venv\Scripts\activate

echo.
echo Ejecutando demo de aprendizaje...
python demo_aprendizaje.py

echo.
echo Presiona cualquier tecla para cerrar...
pause > nul
