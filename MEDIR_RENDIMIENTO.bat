@echo off
rem Mide el rendimiento de OrtoSetup con un escaneo (AC10).
rem Uso: arrastre el archivo STL sobre este .bat, o ejecute:
rem   MEDIR_RENDIMIENTO.bat "C:\ruta\escaneo.stl"
rem Sin archivo: mide con una malla sintetica de 500.000 triangulos.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Primero ejecute INSTALAR.bat
  pause
  exit /b 1
)
if "%~1"=="" (
  ".venv\Scripts\python.exe" scripts\medir_rendimiento.py --sintetico 500000
) else (
  ".venv\Scripts\python.exe" scripts\medir_rendimiento.py "%~1" --mostrar-cabecera
)
echo.
pause
