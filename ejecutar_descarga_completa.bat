@echo off
echo ========================================
echo  DESCARGA COMPLETA - TODOS LOS ARCHIVOS
echo ========================================
echo.

cd /d "C:\Users\DanielGarcíaCarabelo\Downloads\PROYECTO ROBOT APUD"

echo Activando entorno virtual...
call venv\Scripts\activate

echo.
echo Ejecutando descarga completa (todos los archivos finalizados)...
python test_descarga_completa.py

echo.
echo Presiona cualquier tecla para cerrar...
pause > nul
