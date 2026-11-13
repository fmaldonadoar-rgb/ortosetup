@echo off
rem Instala OrtoSetup: Python 3.12, entorno virtual, dependencias, pruebas y caso sintetico.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\windows\instalar.ps1"
echo.
pause
