@echo off
echo ========================================
echo  DEMO - APRENDIZAJE INTERACTIVO V2
echo  (Con rastreo de URLs)
echo ========================================
echo.

cd /d "C:\Users\DanielGarcíaCarabelo\Downloads\PROYECTO ROBOT APUD"

echo Activando entorno virtual...
call venv\Scripts\activate

echo.
echo Ejecutando demo de aprendizaje avanzado...
python demo_aprendizaje_v2.py

echo.
echo Presiona cualquier tecla para cerrar...
pause > nul
