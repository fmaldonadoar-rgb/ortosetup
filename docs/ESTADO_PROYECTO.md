# Estado del proyecto (actualizar en cada sesión)

Última actualización: 13-11-2026 · Versión: 0.1.0-fase1 · Fase actual: **1 (núcleo 3D). AC9 aceptado en Windows con observaciones; AC10 pendiente.**

## Arquitectura actual
Núcleo Python puro (`ortosetup.core`) + interfaz PySide6/PyVista (`ortosetup.app`). Detalle en `AUDITORIA_VIABILIDAD.md` §2 y §5.

## Dependencias
- CI y Linux: numpy 2.5.3 · trimesh 5.2.1 · vtk 9.7.2 · pyvista 0.49.2 · pyvistaqt · PySide6 6.12.0 · pytest.
- Equipo del propietario (13-11-2026): numpy 2.5.4 · trimesh 5.2.1 · vtk 9.7.2 · pyvista 0.49.2 · pyvistaqt 0.13.2 · PySide6 6.12.0 · pytest 9.2.0. Las versiones no están fijadas (ver O6).

## Equipo del propietario
Windows 11 (10.0.26300), Intel con 32 CPUs, **NVIDIA RTX 4080 Laptop GPU, 12 GB** (driver 617.14). Corregido en el prompt 2.5.1 (§3). Python 3.12.10 instalado con winget. WSL no instalado.

## Funciones implementadas (con pruebas)
- Importación STL/PLY/OBJ de arcadas y de dientes segmentados (FDI validado); copia íntegra con SHA-256.
- Diagnóstico geométrico y advertencias de escala.
- Movimientos de 6 GDL por diente, bloqueo, deshacer/rehacer, restauración.
- Proyecto en carpeta: guardado atómico, reapertura bit a bit exacta, verificación de integridad, auditoría.
- Interfaz: árbol de modelos con visibilidad y bloqueo, transparencia, vistas, posición inicial superpuesta, edición numérica.

## Pruebas
`pytest` → **40 superadas** en GitHub Actions (Windows y Linux) **y en el equipo del propietario** (47,7 s, 13-11-2026, commit `bf11790`). Rama `correcciones-ac9`: **44 superadas en Linux** (4 nuevas: O1, O2, O4, O5); pendiente CI y equipo del propietario.

## Verificación manual en Windows
- **AC9: ACEPTADO CON OBSERVACIONES** (13-11-2026, commit `bf11790`). Evidencia en `VERIFICACION_MANUAL.md`. `INSTALAR.bat`, `EJECUTAR.bat`, la creación del proyecto en una ruta con espacio, la importación, el movimiento, el guardado y la reapertura verificada por SHA-256 funcionan en el equipo real.
- **AC10: pendiente.** Rendimiento con un escaneo real desidentificado o, si no hay, con una malla sintética de tamaño real (§9.1). Medir FPS con un método objetivo.

## Defectos de AC9
- **O1 (HiDPI): corregido en `correcciones-ac9`, pendiente de aceptación en Windows.** La columna "Modelo" del árbol se estira y ya no recorta el FDI.
- **O2: corregido en `correcciones-ac9`, pendiente de aceptación en Windows.** Los controles dicen "Movimiento cartesiano (ejes del archivo)", Traslación X/Y/Z y Rotación sobre X/Y/Z.
- **O3:** *z-fighting* entre la arcada sintética (con coronas) y los dientes. Limitación del caso sintético; mitigable con transparencia por defecto de la arcada al haber dientes segmentados.
- **O4: corregido en `correcciones-ac9`.** El origen de los ejes se muestra en lenguaje claro.
- **O5: corregido en `correcciones-ac9`.** `verificar_entorno.py` omite `wsl -l -v` si WSL no está instalado.
- **O6:** dependencias sin versión fijada (reproducibilidad).

## Errores y limitaciones conocidos
- Ejes por diente provisionales (ejes del archivo). Las vistas "oclusal/frontal/lateral" también son relativas a los ejes del archivo.
- La arcada importada incluye los dientes: al mover un diente segmentado, la arcada sigue mostrando la corona en su lugar original. Se resolverá con la segmentación (Fase 2).
- Sin manipuladores por arrastre, sin movimiento de grupos ni versiones de tratamiento.
- Sin importación de registro de mordida.
- Las mallas de alta resolución se dibujan completas (sin reducción): el rendimiento no está medido.

## Decisiones técnicas
- D1: núcleo independiente de la interfaz y de Slicer (ver la auditoría).
- D2: la geometría es inmutable; la posición se guarda como un movimiento paramétrico absoluto, no como una matriz acumulada.
- D3: formato de proyecto en carpeta con JSON legible, en lugar de SQLite, en la Fase 1. Se reevaluará si crecen las versiones o la segmentación por vértice.
- D4: sin reescalado automático; solo advertencias.
- D5: repositorio oficial https://github.com/fmaldonadoar-rgb/ortosetup (rama `main`), con CI en Windows y Linux. Visibilidad: pública. **Decisión pendiente del propietario** sobre pasarlo a privado.
- D6: prompt maestro vigente: `docs/PROMPT_MAESTRO_v2.md` (versión 2.5.1, 13-11-2026). **Prompt congelado** salvo correcciones factuales. Sincronizado en el repositorio en la rama `correcciones-ac9` (antes, `main` tenía el prompt 2.1).
- D7 (**propuesta en v2.5, pendiente de confirmación del propietario**): en el esquema 2 la fuente de verdad pasa de los 6 parámetros a las matrices `M` y `F`, con `T_proyecto_desde_escaneo` por escaneo y migración transaccional con manifiesto.
- D8 (13-11-2026): F se define sobre la pose inicial P0; L y sus parámetros expresan el movimiento total desde la posición inicial, en los ejes iniciales del diente (§8.1).

## Brechas de modelo de datos y seguridad
- `Project.load` no valida que `original.rel_path` quede dentro de la carpeta del proyecto → política de rutas del §18.
- El esquema 1 no tiene `T_proyecto_desde_escaneo` ni matrices como fuente de verdad → esquema 2 (§8.1, §8.2).
- `Project.save` es atómico para un solo archivo, pero no hay manifiesto para migraciones de varios archivos (regla 7.18).
- Verificar si `Project.save` hace `fsync` antes de `os.replace`, y si `Project.load` rechaza `schema_version` futuras (regla 7.18).

## Próximas tareas
(Orden obligatorio: `docs/PROMPT_MAESTRO_v2.md`, §21.)
1. Integrar `correcciones-ac9` (CI en verde) y aceptar O1, O2, O4 y O5 en el equipo del propietario.
2. AC10: medición de rendimiento (escaneo desidentificado o malla sintética de tamaño real).
3. Esquema 2 con versiones del setup y migrador transaccional desde el esquema 1.
4. Pruebas de robustez y política de rutas (§16, §18).
