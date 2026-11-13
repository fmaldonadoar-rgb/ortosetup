# OrtoSetup (Fase 1: núcleo 3D)

> **Software experimental de investigación. No apto para planificación ni fabricación clínica.**

Importa escaneos intraorales (STL/PLY/OBJ) y dientes ya segmentados, permite moverlos con transformaciones numéricas de 6 GDL y guarda proyectos que se reabren sin pérdida de información.

## Instalación en Windows

1. Instale **Python 3.12 (64 bits)** desde python.org y marque "Add python.exe to PATH".
2. Abra PowerShell en esta carpeta:
   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -e .[dev]
   ```
   (Si PowerShell bloquea el script de activación: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.)
3. Ejecute las pruebas: `pytest`. Deben pasar todas.
4. Genere un caso sintético (sin datos de pacientes): `python tools\make_synthetic_case.py caso`
5. Abra la aplicación: `python -m ortosetup` (o `ortosetup`).
   - **Nuevo proyecto** → elija una carpeta vacía.
   - **Importar arcada sup.** → `caso\upper_arch.stl`.
   - **Importar dientes segmentados** → seleccione los archivos de `caso\teeth` (el FDI se toma del nombre, p. ej. `11.stl`).
   - Seleccione un diente → escriba el movimiento → **Aplicar** → **Guardar**.

## Documentación
- `docs/AUDITORIA_VIABILIDAD.md`: decisiones, modelos de IA, riesgos y pruebas de aceptación.
- `docs/CONVENCIONES_EJES.md`: ejes, signos y pivotes (normativo).
- `docs/ESTADO_PROYECTO.md`: estado actual, pendientes y próximas tareas. **Léalo antes de continuar el desarrollo, sea una persona o un agente de IA.**
