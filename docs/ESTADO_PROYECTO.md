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
`pytest` → **35 superadas** (núcleo 32 + escena/ventana 3, render offscreen).

## Verificación manual pendiente en Windows (AC9–AC10)
1. Instalar según el README y ejecutar `pytest`.
2. `python tools\make_synthetic_case.py caso` → abrir la app → crear un proyecto → importar `caso\upper_arch.stl` y los dientes de `caso\teeth`.
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

## Próximas tareas
1. Verificación manual en Windows (AC9–AC10).
2. Cierre de la Fase 1: versiones de tratamiento con nombre, movimiento de grupos, importación del registro de mordida y manipulador por arrastre (opcional; la entrada numérica ya cumple el criterio).
3. Evaluación acotada de segmentación (Fase 2): instalar Slicer 5.12 y WSL2; probar DentalModelSeg, MeshSegNet y un modelo de 3DTeethSeg con escaneos anonimizados; registrar las licencias de código, pesos y datos.
