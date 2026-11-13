@echo off
rem Abre OrtoSetup. Puede arrastrar una carpeta de proyecto sobre este archivo para abrirla.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Primero ejecute INSTALAR.bat
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m ortosetup %*
if errorlevel 1 pause
