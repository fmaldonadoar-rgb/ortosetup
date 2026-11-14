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

## AC10 — Rendimiento con escaneo real

**Resultado: ACEPTADO** (13-11-2026). Rama `ac10-medicion` (commit `be8728e`, PR #2). Verificó: propietario, guiado por Claude.

| Campo | Valor |
|---|---|
| Caso | Escaneo intraoral de la **propia boca del propietario** (arcada superior), STL binario de 10,0 MB. Ver `docs/DATOS.md`. |
| Cabecera STL | Contiene solo "3Shape" (marca del escáner); sin datos personales. |
| Malla | 209.238 triángulos; 627.714 vértices (STL sin vértices unidos: 3 por triángulo). 1 advertencia geométrica: superficie abierta (2.054 aristas de borde), habitual en escaneos intraorales. |
| Herramienta | `MEDIR_RENDIMIENTO.bat` (render offscreen a 1600x1000, 180 cuadros, sincronizado con la GPU). |

| Métrica | GPU Intel integrada (por defecto de Windows) | GPU NVIDIA RTX 4080 Laptop (configurada) | Meta §9.5 |
|---|---|---|---|
| Lectura + diagnóstico | 0,10 + 0,53 s | 0,10 + 0,53 s | — |
| Preparación para visualizar | 4,02 s (arranque en frío) | 0,60 s | — |
| Carga total hasta ver la arcada | ≈ 4,8 s (calculada a mano; la versión inicial de la herramienta solo medía la lectura) | 1,35 s | < 10 s: **cumple** |
| FPS al rotar (mediana) | 134,8 (p95: 121) | ≈ 2.900 (sobre el límite de resolución de la medición) | ≥ 30: **cumple** |
| Memoria máxima del proceso | no medida (defecto de la herramienta, corregido) | 389 MB | — |

Fluidez en la ventana interactiva (a ojo): **buena**.

**Hallazgos de AC10:**
- **O7 (defecto, corregido y aceptado):** `Scene.clear()` eliminaba las luces (`plotter.clear()` de PyVista también las borra). Todas las mallas se veían como siluetas planas, sin relieve; afectaba también a AC9. Verificado con captura del escaneo real: relieve visible.
- **O8 (configuración del equipo):** Windows ejecutaba Python con la GPU Intel integrada. Se configuró "Alto rendimiento" para `C:\dev\ortosetup\.venv\Scripts\python.exe` y para el Python base (Configuración → Sistema → Pantalla → Gráficos). Debe documentarse en la instalación.
- **O9 (optimización futura):** la preparación para visualizar es la etapa más lenta (0,6 a 4,0 s) porque el STL no trae vértices unidos. Unirlos **solo para visualizar** (regla 7.19) reduciría tiempo y memoria. No bloquea.
- **Límite de representatividad:** una sola arcada de tamaño moderado. Escaneos de mayor resolución o dos arcadas pueden pesar 2 a 4 veces más; el margen frente a las metas es amplio.
