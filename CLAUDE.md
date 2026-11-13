# Instrucciones para agentes de IA (Claude Code u otros)

Este repositorio es **OrtoSetup**, un software experimental de setup ortodóncico 3D para Windows. El propietario es ortodoncista y no programa: explícale todo en español, paso a paso y con comandos exactos para Windows.

## Al iniciar cada sesión
1. Lee `docs/PROMPT_MAESTRO_v2.md` (reglas y hoja de ruta), `docs/ESTADO_PROYECTO.md` (estado real) y `docs/CONVENCIONES_EJES.md` (ejes y signos; es normativo).
2. Ejecuta `.venv\Scripts\python -m pytest -q` y `.venv\Scripts\python scripts\verificar_entorno.py`. Si `.venv` no existe, pide al propietario que ejecute `INSTALAR.bat`.

## Reglas
- `src/ortosetup/core` no importa Qt, VTK ni PyVista. La interfaz vive en `src/ortosetup/app`.
- Los originales importados y la geometría de los dientes son inmutables. Las posiciones se guardan como `Movement6DOF` absolutos.
- Toda función nueva lleva pruebas. No declares nada terminado sin que `pytest` pase **en Windows**.
- No uses datos de pacientes. Usa `tools/make_synthetic_case.py` o mallas generadas en las pruebas.
- No incrustes valores clínicos o biomecánicos sin una fuente citada: deben ser parámetros editables.
- Registra las licencias de código, pesos y datasets en `docs/LICENCIAS.md` antes de agregar una dependencia o un modelo.
- En Windows: usa `pathlib`, `encoding="utf-8"` y `multiprocessing` con `spawn`. Los `.bat` y `.ps1` van sin acentos y con CRLF.
- Al terminar: actualiza `docs/ESTADO_PROYECTO.md`, haz un commit por tarea y entrega al propietario los pasos de verificación manual con el resultado esperado.
