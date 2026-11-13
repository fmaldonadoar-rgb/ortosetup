# OrtoSetup (Fase 1: núcleo 3D) — Windows

> **Software experimental de investigación. No apto para planificación ni fabricación clínica.**

Importa escaneos intraorales (STL, PLY u OBJ) y dientes ya segmentados, permite moverlos con transformaciones numéricas de 6 grados de libertad y guarda proyectos que se reabren sin perder información.

## Instalación en Windows (doble clic)

1. **Ubicación:** descomprima o clone el repositorio en una carpeta corta, sin acentos y **fuera de OneDrive**, por ejemplo `C:\dev\ortosetup`.
2. **Instalar:** haga doble clic en **`INSTALAR.bat`**.
   - Si no tiene Python 3.12, el instalador ofrece instalarlo con winget. Después cierre la ventana y vuelva a ejecutar `INSTALAR.bat`.
   - La primera vez tarda algunos minutos. Al final debe aparecer `INSTALACION CORRECTA. Todas las pruebas pasaron.`
   - Se crean la carpeta `caso_sintetico\` (datos de prueba, sin pacientes) y el archivo `reporte_entorno.txt`.
3. **Abrir el programa:** doble clic en **`EJECUTAR.bat`**.
   1. **Nuevo proyecto** → elija una carpeta vacía (p. ej. `C:\dev\proyectos\prueba1`).
   2. **Importar arcada sup.** → `caso_sintetico\upper_arch.stl`.
   3. **Importar dientes segmentados** → seleccione todos los archivos de `caso_sintetico\teeth` (el número FDI se toma del nombre del archivo, p. ej. `11.stl`).
   4. Seleccione un diente en la lista → escriba el movimiento → **Aplicar** → **Guardar**.
4. **Volver a probar** cuando quiera: **`PROBAR.bat`** ejecuta las pruebas y actualiza `reporte_entorno.txt`.

¿Algo falló? Comparta `reporte_entorno.txt` y lo que muestra la ventana con el agente de IA.

## Desarrollo con IA en Windows (recomendado)

- Instale **Git for Windows** y **Claude Code** (aplicación de escritorio o terminal) y abra esta carpeta. El agente lee `CLAUDE.md` y puede ejecutar las pruebas en su propio Windows.
- Opcional: suba el repositorio a un repositorio **privado** de GitHub. `.github/workflows/pruebas.yml` ejecutará las pruebas en Windows en cada cambio. Las mallas (`*.stl`, `*.ply`, `*.obj`) están excluidas de Git.

## Documentación
- `docs/PROMPT_MAESTRO_v2.md`: reglas, decisiones para Windows y hoja de ruta (es el prompt para el agente).
- `docs/ESTADO_PROYECTO.md`: estado actual, pendientes y próximas tareas.
- `docs/AUDITORIA_VIABILIDAD.md`: análisis de plataformas, modelos de IA, riesgos y pruebas de aceptación.
- `docs/CONVENCIONES_EJES.md`: ejes, signos y pivotes (normativo).
- `docs/LICENCIAS.md`: registro de licencias de código, modelos y datasets.

## Instalación manual (alternativa a INSTALAR.bat)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ortosetup
```
