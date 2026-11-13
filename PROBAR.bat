@echo off
rem Ejecuta las pruebas automatizadas y genera reporte_entorno.txt
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Primero ejecute INSTALAR.bat
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pytest -v
".venv\Scripts\python.exe" scripts\verificar_entorno.py
echo.
pause
