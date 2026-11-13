# Estado del proyecto (actualizar en cada sesión)

Última actualización: 13-11-2026 · Versión: 0.1.0-fase1 · Fase actual: **1 (núcleo 3D), implementada y pendiente de verificación en Windows**

## Arquitectura actual
Núcleo Python puro (`ortosetup.core`) + interfaz PySide6/PyVista (`ortosetup.app`). Detalle en `AUDITORIA_VIABILIDAD.md` §2 y §5.

## Dependencias (probadas en Linux, Python 3.13)
numpy 2.5.3 · trimesh 5.2.1 · vtk 9.7.2 · pyvista 0.49.2 · pyvistaqt · PySide6 6.12.0 · pytest. Recomendado en Windows: Python 3.12 de 64 bits.

## Funciones implementadas (con pruebas)
- Importación STL/PLY/OBJ de arcadas y de dientes segmentados (FDI validado); copia íntegra con SHA-256.
- Diagnóstico geométrico y advertencias de escala.
- Movimientos de 6 GDL por diente, bloqueo, deshacer/rehacer, restauración.
- Proyecto en carpeta: guardado atómico, reapertura bit a bit exacta, verificación de integridad, auditoría.
- Interfaz: árbol de modelos con visibilidad y bloqueo, transparencia, vistas, posición inicial superpuesta, edición numérica.

## Pruebas
`pytest` → **40 superadas en Linux y en Windows** (GitHub Actions, windows-latest, Python 3.12.10, 13-11-2026): núcleo 32 + escena/ventana 3 con render offscreen + soporte de plataforma 5. Pendiente: verificación manual en el equipo del propietario y ejecución real de los .bat/.ps1 (CI no los ejecuta).

## Soporte para Windows (agregado en v2 del prompt)
- `INSTALAR.bat` / `EJECUTAR.bat` / `PROBAR.bat` en la raíz; el instalador está en `scripts/windows/instalar.ps1` (verifica Python 3.12, crea `.venv`, instala, prueba, genera el caso sintético y el reporte).
- `scripts/verificar_entorno.py` → `reporte_entorno.txt` (Python, paquetes, GPU/driver, WSL, render VTK, advertencias de ruta y OneDrive).
- `.github/workflows/pruebas.yml`: CI en `windows-latest` y `ubuntu-latest` (sin ejecutar todavía; requiere subir el repositorio a GitHub).
- Guardado con reintentos ante archivos bloqueados (antivirus/OneDrive) y mensaje claro.
- `.gitattributes`: CRLF para `.bat`/`.ps1`. Los scripts de Windows se validan como ASCII en las pruebas.
- **No probados en Windows real:** los `.bat`/`.ps1` (escritos sin poder ejecutarlos aquí). Son lo primero que hay que verificar.

## Verificación manual pendiente en Windows (AC9–AC10)
1. Mover el repositorio a `C:\dev\ortosetup` → doble clic en `INSTALAR.bat` → debe terminar con "INSTALACION CORRECTA".
2. `EJECUTAR.bat` → crear un proyecto → importar `caso_sintetico\upper_arch.stl` y los dientes de `caso_sintetico\teeth`.
3. Mover el diente 11 (p. ej., 2 mm VL y 15° de rotación) → Guardar → cerrar → reabrir: los valores deben ser idénticos.
4. Repetir con un escaneo real **anonimizado** y anotar el número de triángulos, el tiempo de carga y la fluidez.

## Errores y limitaciones conocidos
- Ejes por diente provisionales (ejes del archivo). Las vistas "oclusal/frontal/lateral" también son relativas a los ejes del archivo.
- La arcada importada incluye los dientes: al mover un diente segmentado, la arcada sigue mostrando la corona en su lugar original (conviene ocultar la arcada o usar transparencia). Se resolverá con la segmentación (Fase 2), al separar la encía de las coronas.
- Sin manipuladores por arrastre, sin movimiento de grupos ni versiones de tratamiento.
- Sin importación de registro de mordida.
- Las mallas de alta resolución se dibujan completas (sin reducción): el rendimiento no está medido.

## Decisiones técnicas
- D1: núcleo independiente de la interfaz y de Slicer (ver la auditoría).
- D2: la geometría es inmutable; la posición se guarda como un movimiento paramétrico absoluto, no como una matriz acumulada.
- D3: formato de proyecto en carpeta con JSON legible, en lugar de SQLite, en la Fase 1 (más transparente y fácil de comparar). Se reevaluará si crecen las versiones o la segmentación por vértice.
- D4: sin reescalado automático; solo advertencias.
- D5: repositorio oficial https://github.com/fmaldonadoar-rgb/ortosetup (rama `main`), con CI en Windows y Linux. Visibilidad: pública. **Decisión pendiente del propietario** sobre pasarlo a privado.
- D6: prompt maestro vigente: `docs/PROMPT_MAESTRO_v2.md` (versión 2.1).

## Próximas tareas
(Hoja de ruta completa: `docs/PROMPT_MAESTRO_v2.md`, sección 6.)
1. Verificación manual en Windows (AC9–AC10) y corrección de los fallos de instalación que aparezcan.
2. Cierre de la Fase 1: versiones de tratamiento con nombre, movimiento de grupos, importación del registro de mordida y manipulador por arrastre (opcional; la entrada numérica ya cumple el criterio).
3. Evaluación acotada de segmentación (Fase 2): instalar Slicer 5.12 y WSL2; probar DentalModelSeg, MeshSegNet y un modelo de 3DTeethSeg con escaneos anonimizados; registrar las licencias de código, pesos y datos.
