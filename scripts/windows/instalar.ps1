# Instalador de OrtoSetup para Windows. Normalmente se ejecuta con INSTALAR.bat.
# (Archivo sin acentos a proposito: PowerShell 5.1 lee mal UTF-8 sin BOM.)
$ErrorActionPreference = "Continue"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $Root
Write-Host ""
Write-Host "=== OrtoSetup - instalacion (software experimental, no clinico) ===" -ForegroundColor Cyan
Write-Host "Carpeta: $Root"

if ($Root -match "OneDrive") {
    Write-Warning "El proyecto esta dentro de OneDrive. Se recomienda moverlo a C:\dev\ortosetup."
}

function Test-Py312 {
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) { return $false }
    & py -3.12 -c "import sys" *> $null
    return ($LASTEXITCODE -eq 0)
}

# 1. Python 3.12
if (-not (Test-Py312)) {
    Write-Host "No se encontro Python 3.12 (64 bits)." -ForegroundColor Yellow
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        $r = Read-Host "Instalarlo ahora con winget? (s/n)"
        if ($r -eq "s") {
            winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
            Write-Host "Python instalado. CIERRE esta ventana y ejecute INSTALAR.bat de nuevo." -ForegroundColor Green
            exit 1
        }
    }
    Write-Host "Instale Python 3.12 de 64 bits desde https://www.python.org/downloads/windows/"
    Write-Host "(marque 'Add python.exe to PATH') y ejecute INSTALAR.bat de nuevo."
    exit 1
}

# 2. Entorno virtual
$VPy = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $VPy)) {
    Write-Host "Creando entorno virtual .venv ..."
    & py -3.12 -m venv .venv
    if ($LASTEXITCODE -ne 0) { Write-Host "No se pudo crear .venv" -ForegroundColor Red; exit 1 }
}

# 3. Dependencias
Write-Host "Instalando dependencias (puede tardar varios minutos la primera vez) ..."
& $VPy -m pip install --upgrade pip
& $VPy -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) { Write-Host "Fallo la instalacion de dependencias." -ForegroundColor Red; exit 1 }

# 4. Pruebas automatizadas
Write-Host ""
Write-Host "Ejecutando pruebas automatizadas ..." -ForegroundColor Cyan
& $VPy -m pytest -q
$TestsOk = ($LASTEXITCODE -eq 0)

# 5. Caso sintetico y reporte de entorno
& $VPy tools\make_synthetic_case.py caso_sintetico
& $VPy scripts\verificar_entorno.py

Write-Host ""
if ($TestsOk) {
    Write-Host "INSTALACION CORRECTA. Todas las pruebas pasaron." -ForegroundColor Green
    Write-Host "Abra el programa con EJECUTAR.bat. Caso de prueba en: $Root\caso_sintetico"
} else {
    Write-Host "La instalacion termino, pero ALGUNAS PRUEBAS FALLARON." -ForegroundColor Red
    Write-Host "Comparta reporte_entorno.txt y la salida de pytest con el agente de IA."
    exit 2
}
