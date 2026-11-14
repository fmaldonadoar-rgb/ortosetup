# Verificación manual en Windows

Evidencia de aceptación en el equipo del propietario (prompt maestro §16). Cada entrada indica fecha, commit, equipo, caso, pasos, resultado esperado y obtenido, y quién verificó.

## AC9 — Instalación y operación con el caso sintético

**Resultado: ACEPTADO CON OBSERVACIONES**

| Campo | Valor |
|---|---|
| Fecha | 13-11-2026 |
| Commit verificado | `bf11790` |
| Equipo | Windows 11 (10.0.26300), Intel 32 CPUs, NVIDIA GeForce RTX 4080 Laptop GPU (12 GB, driver 617.14) |
| Python | 3.12.10 64 bits, en `.venv` (instalado con `winget install --id Python.Python.3.12 -e`) |
| Paquetes | numpy 2.5.4 · trimesh 5.2.1 · vtk 9.7.2 · pyvista 0.49.2 · pyvistaqt 0.13.2 · PySide6 6.12.0 · pytest 9.2.0 |
| Caso usado | Sintético (`caso_sintetico`, generado por `INSTALAR.bat`). Sin datos de pacientes. |
| Verificó | Propietario, guiado por Claude |

### Pasos ejecutados y resultados
| # | Paso | Esperado | Obtenido |
|---|---|---|---|
| 1 | Instalar Git for Windows y Python 3.12 (no estaba instalado) | `git --version`, `py -3.12 --version` responden | OK (Python 3.12.10) |
| 2 | `git clone` en `C:\dev\ortosetup` | Clon sin errores | OK |
| 3 | `INSTALAR.bat` desde PowerShell | "INSTALACION CORRECTA" | OK: 40 pruebas superadas (47,7 s), caso sintético generado, render VTK offscreen OK, sin advertencias |
| 4 | `EJECUTAR.bat` → nuevo proyecto en `C:\dev\prueba proyecto` (ruta con espacio) | Proyecto creado | OK |
| 5 | Importar `upper_arch.stl` y dientes 11–17, 21–27 | FDI deducido del nombre | OK (14 dientes) |
| 6 | Diente 11: VL = 2 mm, rotación eje largo = 15°, Aplicar | Diente se desplaza | OK |
| 7 | Guardar, cerrar, abrir el proyecto | "Proyecto abierto y verificado (SHA-256)"; valores idénticos | OK: VL 2,000 mm, rot 15,000°, demás 0; mensaje de verificación presente |
| 8 | Rotar el visor con el mouse | Rotación fluida | Fluida. Parpadeo de superficies con la arcada visible; desaparece al ocultarla (ver O3). FPS no medido. |

### Observaciones (defectos y limitaciones)
- **O1 (defecto, HiDPI §5.7):** la columna "Modelo" del árbol es demasiado angosta con el escalado de la pantalla del notebook. Los FDI se ven como "..." y la arcada como "Arcad...". Solo aparece en el equipo real; el CI no lo detecta.
- **O2 (incumplimiento conocido, §8.3):** los controles se rotulan "Angulación", "Torque/inclinación" y "Rotación eje largo" sobre ejes del archivo.
- **O3 (limitación del caso sintético):** *z-fighting* (parpadeo) entre la malla de arcada, que incluye coronas, y los dientes segmentados superpuestos. Desaparece al ocultar la arcada. No es un problema de rendimiento.
- **O4 (menor):** la interfaz muestra el identificador interno `provisional_world_axes_centroid`.
- **O5 (menor):** `verificar_entorno.py` espera 20 s a `wsl -l -v` aunque WSL no está instalado.
- **O6 (reproducibilidad):** dependencias sin versión fijada (numpy 2.5.4 local vs 2.5.3 en CI).

## Correcciones O1, O2, O4, O5 (rama `correcciones-ac9`, commit `bd39365`, PR #1)

**Resultado: ACEPTADO** (13-11-2026). Mismo equipo y caso que AC9. Verificó: propietario, guiado por Claude.

| # | Paso | Esperado | Obtenido |
|---|---|---|---|
| 1 | `git switch correcciones-ac9` y `PROBAR.bat` | Reporte sin espera de 20 s en WSL | OK: "WSL distribuciones: (omitido: WSL no está instalado...)". El conteo local de pytest no fue informado; el CI en `windows-latest` y `ubuntu-latest` pasó las 44 pruebas. |
| 2 | `EJECUTAR.bat` → abrir `C:\dev\prueba proyecto` | Mensaje de verificación SHA-256 | OK |
| 3 | Lista de dientes | FDI 11–17 y 21–27 completos | OK (O1 resuelto) |
| 4 | Seleccionar diente 11 | "Movimiento cartesiano (ejes del archivo)"; Traslación Y = 2,000 mm; Rotación sobre Z = 15,000 ° | OK (O2 resuelto; el proyecto de esquema 1 se abre sin cambios) |
| 5 | Línea de referencia | Texto en lenguaje claro | OK: "provisional (ejes del archivo; pivote en el centroide del diente)" (O4 resuelto) |

## Pendiente
- AC10: rendimiento con un escaneo representativo, autorizado y desidentificado (o con malla sintética de tamaño real según §9.1). Medir FPS con un método objetivo.
