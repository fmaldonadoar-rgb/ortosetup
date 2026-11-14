# Estado del proyecto (actualizar en cada sesión)

Última actualización: 13-11-2026 · Versión: 0.1.0-fase1 · Fase actual: **1 (núcleo 3D). AC9 y AC10 aceptados en Windows; falta el esquema 2 para cerrar la Fase 1.**

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
`pytest` → **40 superadas** en GitHub Actions (Windows y Linux) **y en el equipo del propietario** (47,7 s, 13-11-2026, commit `bf11790`). Desde el PR #1: **44 superadas** en Linux y en el CI (Windows y Linux). Desde el PR #2: **47** (cabecera STL, reporte sin datos identificables e iluminación de la escena).

## Verificación manual en Windows
- **AC9: ACEPTADO CON OBSERVACIONES** (13-11-2026, commit `bf11790`). Evidencia en `VERIFICACION_MANUAL.md`. `INSTALAR.bat`, `EJECUTAR.bat`, la creación del proyecto en una ruta con espacio, la importación, el movimiento, el guardado y la reapertura verificada por SHA-256 funcionan en el equipo real.
- **AC10: ACEPTADO** (13-11-2026, PR #2). Escaneo de la propia boca del propietario (209.238 triángulos). Con la NVIDIA: carga total de 1,35 s y FPS muy por sobre 30; con la Intel integrada: ≈ 4,8 s y 135 FPS. Evidencia en `VERIFICACION_MANUAL.md`.

## Defectos de AC9
- **O1 (HiDPI): corregido y aceptado en Windows (PR #1).** La columna "Modelo" del árbol se estira y ya no recorta el FDI.
- **O2: corregido y aceptado en Windows (PR #1).** Los controles dicen "Movimiento cartesiano (ejes del archivo)", Traslación X/Y/Z y Rotación sobre X/Y/Z.
- **O3:** *z-fighting* entre la arcada sintética (con coronas) y los dientes. Limitación del caso sintético; mitigable con transparencia por defecto de la arcada al haber dientes segmentados.
- **O4: corregido y aceptado en Windows (PR #1).** El origen de los ejes se muestra en lenguaje claro.
- **O5: corregido y aceptado en Windows (PR #1).** `verificar_entorno.py` omite `wsl -l -v` si WSL no está instalado.
- **O6:** dependencias sin versión fijada (reproducibilidad).
- **O7: corregido y aceptado (PR #2).** La escena perdía las luces al cargar un proyecto (siluetas planas).
- **O8 (equipo):** Windows usaba la GPU Intel integrada; hay que configurar "Alto rendimiento" para los dos `python.exe`. Pendiente documentarlo en `INSTALAR.bat` o en el README.
- **O9 (optimización):** unir vértices solo para visualizar (regla 7.19) para acelerar la preparación.

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
- D6: prompt maestro vigente: `docs/PROMPT_MAESTRO_v2.md` (versión 2.5.1, 13-11-2026). **Prompt congelado** salvo correcciones factuales. Sincronizado en `main` mediante el PR #1 (antes, `main` tenía el prompt 2.1).
- D7 (**propuesta en v2.5, pendiente de confirmación del propietario**): en el esquema 2 la fuente de verdad pasa de los 6 parámetros a las matrices `M` y `F`, con `T_proyecto_desde_escaneo` por escaneo y migración transaccional con manifiesto.
- D8 (13-11-2026): F se define sobre la pose inicial P0; L y sus parámetros expresan el movimiento total desde la posición inicial, en los ejes iniciales del diente (§8.1).

## Brechas de modelo de datos y seguridad
- `Project.load` no valida que `original.rel_path` quede dentro de la carpeta del proyecto → política de rutas del §18.
- El esquema 1 no tiene `T_proyecto_desde_escaneo` ni matrices como fuente de verdad → esquema 2 (§8.1, §8.2).
- `Project.save` es atómico para un solo archivo, pero no hay manifiesto para migraciones de varios archivos (regla 7.18).
- Verificar si `Project.save` hace `fsync` antes de `os.replace`, y si `Project.load` rechaza `schema_version` futuras (regla 7.18).

## Datos
- `docs/DATOS.md`: estado de la Ley 21.719 (vigente desde el 1-12-2026, salvo que se apruebe la postergación en trámite; consulta del 13-11-2026), origen y tratamiento del escaneo de AC10. Escaneos de terceros: no autorizados aún.

## Próximas tareas
(Orden obligatorio: `docs/PROMPT_MAESTRO_v2.md`, §21.)
1. **Esquema 2** con versiones del setup, matrices M y F como fuente de verdad, `T_proyecto_desde_escaneo` y migrador transaccional desde el esquema 1. Es lo único que falta para cerrar la Fase 1. Antes: confirmar la decisión D7.
2. Pruebas de robustez y política de rutas (§16, §18).
3. Menores: O6 (fijar versiones), O8 (documentar la GPU), O9 (unir vértices para visualizar).
