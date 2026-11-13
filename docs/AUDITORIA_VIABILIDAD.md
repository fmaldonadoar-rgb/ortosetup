# Auditoría técnica de viabilidad — OrtoSetup

Fecha: 13-11-2026 · Versión del software: 0.1.0-fase1 · Estado: experimental, no apto para uso clínico.

## 0. Resumen

- **Es viable como prototipo de investigación**, sin costo de licencias y con procesamiento local (RTX 4080). Lo que limita el proyecto no es el dinero (US$300 alcanzan) sino la calidad de la segmentación con escaneos reales, la definición de sistemas de referencia anatómicos y el tiempo de validación.
- **Decisión de arquitectura:** el núcleo es una biblioteca Python pura, sin interfaz gráfica, y es la fuente de verdad. La Fase 1 usa una aplicación independiente PySide6 + PyVista/VTK. 3D Slicer queda como banco de pruebas para evaluar segmentación (Fase 2) y, si conviene, como interfaz alternativa más adelante (un módulo de Slicer que importe el mismo núcleo).
- **Hallazgo crítico:** la herramienta de Slicer más directa para segmentar escaneos intraorales (DentalModelSeg / CrownSegmentation) declara funcionar **solo en Linux con CUDA**. En Windows habrá que usar WSL2 o adaptar el modelo.
- **Recomendación estratégica:** hacer pronto una **evaluación acotada de segmentación** con escaneos anonimizados de su propio escáner, sin integrarla aún. Si ningún modelo existente funciona razonablemente con sus datos, todo lo posterior (análisis, setup, staging) cambia de costo y de plazo. Conviene saberlo antes de invertir en las fases 3 a 5.

## 1. Herramientas y versiones verificadas

| Componente | Versión verificada | Notas |
|---|---|---|
| 3D Slicer | 5.12.4 estable (sept. 2026) | La 5.12 permite compilar con Qt 6 y mantiene compatibilidad con Qt 5.15. **No verificada:** la versión de Python incluida; confírmela en la consola de Python de Slicer antes de desarrollar módulos. |
| Open3D | 0.19 / 0.20 | Python 3.10–3.14, Windows 10+ de 64 bits. En Windows el paquete `open3d` es solo CPU; el de CUDA se instala aparte. **No se usa en la Fase 1.** |
| Entorno de prueba (Linux) | Python 3.13.18, NumPy 2.5.3, trimesh 5.2.1, VTK 9.7.2, PyVista 0.49.2, PySide6 6.12.0, pytest | 35 pruebas superadas. |
| Recomendado en Windows | **Python 3.12** de 64 bits | Es la versión con mayor compatibilidad cruzada (Open3D, PyTorch, VTK, PySide6). |

Licencias de la Fase 1: NumPy (BSD), trimesh (MIT), VTK (BSD), PyVista (MIT), pyvistaqt (MIT), PySide6 (LGPLv3; se puede usar en software propietario si se enlaza dinámicamente y se respeta la LGPL). Todas son compatibles con un uso experimental y con una eventual distribución.

## 2. 3D Slicer frente a aplicación independiente (Qt + VTK)

| Criterio | 3D Slicer como plataforma | Aplicación independiente (PySide6 + PyVista) |
|---|---|---|
| Visualización, transformaciones, marcadores | Incluidos y maduros | Hay que construirlos (PyVista simplifica mucho) |
| Control de la interfaz clínica | Limitado: hay que adaptarse a la interfaz de Slicer | Total |
| Pruebas automatizadas | Difíciles: el código corre dentro del intérprete de Slicer | Directas con pytest |
| Dependencias de Python | Las fija Slicer (su Python, su Qt, `pip_install` interno) | Libres |
| Ecosistema dental | Extensiones de segmentación y landmarks (DCBIA, UNC) | Hay que integrarlas a mano |
| Desarrollo por IA y mantenimiento por un no programador | Más difícil: la API de MRML es grande y está poco representada en los datos de entrenamiento | Más fácil: código Python estándar |
| Empaquetado para Windows | Instalador de Slicer + extensión | PyInstaller o un instalador propio |

**Decisión:** arquitectura híbrida.

1. `ortosetup.core` (Python puro: numpy + trimesh) contiene datos, geometría, transformaciones, persistencia y auditoría. No importa ni Qt ni VTK.
2. `ortosetup.app` es la interfaz independiente de la Fase 1.
3. Slicer se usa como herramienta externa para correr y comparar modelos de segmentación. Más adelante puede añadirse un módulo de Slicer que importe `ortosetup.core`, de modo que ninguna decisión quede atada a una plataforma.

## 3. Modelos de segmentación de escaneos intraorales

| Candidato | Entrada | Licencia y pesos | Compatibilidad con Windows | Observaciones |
|---|---|---|---|---|
| **SlicerDentalModelSeg** (CrownSegmentation, UNC/U. Michigan) | IOS en `.vtk` (inferior o superior) | Licencia **por verificar** en el repositorio; los pesos se descargan desde la extensión | **Solo Linux + CUDA** según su README → requiere WSL2 | Entrenado con ~1000 escaneos; numeración FDI o Universal; renderiza vistas 2D y luego proyecta las etiquetas a la malla. Es el candidato principal. |
| **SlicerAutomatedDentalTools** (DCBIA) | IOS y CBCT | Por verificar | Por verificar por módulo | Paquete que reúne segmentación, landmarks y orientación automática. Su módulo de orientación de IOS puede resolver el problema de los ejes (ver riesgo R1). |
| **MeshSegNet** (Lian et al., IEEE TMI 2020) | Malla reducida a ~10.000 celdas | Código **MIT**; el fork de Tai‑Hsien incluye modelos superior e inferior | Python + PyTorch: sí | Entrenado con solo **36 escaneos** y 15 clases (14 dientes + encía): no contempla terceros molares y generaliza poco. La variante iMeshSegNet reportó un DSC de 0,953, pero esos pesos no están verificados. Sirve como referencia, no como solución. |
| **TSegFormer** (MICCAI 2023) y soluciones del desafío 3DTeethSeg'22 | Nube de puntos o malla | Por verificar repositorio por repositorio | PyTorch: probable | Más modernas. Muchas fueron entrenadas con Teeth3DS. |
| **Teeth3DS+** (conjunto de datos) | 1800 escaneos de 900 pacientes, 23.999 dientes anotados y ~30.000 landmarks | En OSF figura como licencia **"Other": verificar antes de usar**, porque puede prohibir el uso comercial | — | Es la referencia para evaluar y para un posible ajuste fino. Si su licencia es no comercial, también restringe los modelos entrenados con él. |
| DentalSegmentator, CBCTToothSegmentation | **CBCT**, no IOS | Apache 2.0 (CBCTToothSegmentation) | Sí | No sirven para escaneos intraorales. Serán relevantes si más adelante se incorporan raíces desde CBCT. |

**Advertencia de licencias:** la licencia del código y la de los pesos suelen ser distintas. Antes de integrar cualquier modelo hay que registrar por separado la licencia del código, la de los pesos y la del conjunto de datos de entrenamiento.

**Plan de la Fase 2 (sin entrenar nada):** probar 2 o 3 candidatos con 10 a 20 escaneos anonimizados de su escáner, todos con el mismo protocolo: DSC por diente, exactitud FDI, tiempo de procesamiento y número de correcciones manuales. Elegir según esos datos.

## 4. Riesgos principales

| # | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| R1 | **Sistema de referencia anatómico.** Sin plano oclusal, línea media y ejes por diente, los nombres "mesiodistal" o "torque" no tienen significado clínico. Los ejes de la Fase 1 son provisionales. | Muy alto: afecta el análisis, el setup y el staging | Fase 3: ejes por diente a partir de landmarks editables; evaluar la orientación automática de IOS de DCBIA. |
| R2 | **Segmentación con datos reales** (apiñamiento, margen gingival, ausencias, dentición mixta) | Muy alto | Evaluación acotada temprana; corrección manual obligatoria; avisos de baja confianza. |
| R3 | **Registro de mordida.** Dos escaneos importados por separado no garantizan la relación oclusal. | Alto para overjet, overbite y contactos | `bite_registered=false` por defecto; importar el registro como tercer escaneo o como transformación (pendiente). |
| R4 | **Windows + CUDA + modelos que solo corren en Linux** | Medio | WSL2 con CUDA (compatible con la RTX 4080) y segmentación como proceso separado que intercambia archivos. |
| R5 | **Rendimiento:** escaneos de 300.000 a 1.000.000 de triángulos más colisiones entre 28 dientes | Medio | Copias reducidas para visualizar e interactuar; BVH o FCL para colisiones (Fase 5). |
| R6 | **Mantenimiento de código generado por IA** por una persona sin experiencia en programación | Alto | Módulos pequeños, pruebas como contrato, archivo de estado y convenciones explícitas. |
| R7 | **Regulación** (en Chile, el software con fines de diagnóstico o tratamiento puede ser dispositivo médico) | Alto si se usa con pacientes | Uso solo en investigación, aviso permanente y separación entre validación geométrica, clínica y regulatoria. |
| R8 | **Datos de prueba:** no se usan datos identificables | Medio | Mallas sintéticas (ya incluidas), muestras públicas con licencia verificada y escaneos propios anonimizados con consentimiento. |
| R9 | **Ampliación del alcance:** el setup automático y el staging son la parte más difícil (investigación abierta) | Alto en plazo | Las fases no avanzan sin entregable; el setup automático comienza como optimización con objetivos simples. |

## 5. Estructura del repositorio

```
ortosetup/
  src/ortosetup/
    core/            # sin GUI: fuente de verdad
      transforms.py  # 6 GDL, convenciones de ejes
      mesh_io.py     # lectura STL/PLY/OBJ, comprobaciones, escala
      fdi.py         # validación FDI
      project.py     # modelo de datos, persistencia, auditoría, integridad
      history.py     # deshacer/rehacer
    app/             # interfaz (PySide6 + PyVista)
      scene.py       # proyecto -> actores VTK (testeable offscreen)
      main_window.py
  tests/             # pytest (núcleo + escena + ventana)
  tools/make_synthetic_case.py   # datos sintéticos, sin pacientes
  docs/              # auditoría, convenciones, estado del proyecto
```
Módulos futuros (uno por fase, sin dependencias circulares): `core/segmentation/`, `core/analysis/`, `core/setup_opt/`, `core/staging/`, `core/export/`. La interfaz solo depende de `core`; `core` nunca depende de la interfaz.

## 6. Esquema de datos

Carpeta de proyecto:
```
Caso/
  project.json   # estado completo, legible, con schema_version
  audit.jsonl    # registro append-only: fecha, versión de software, acción, detalles
  originals/     # copias byte a byte con SHA-256; nunca se modifican
    upper__scan.stl, lower__scan.stl, teeth/11__11.stl ...
```
`project.json` (schema_version 1):
- `units: "mm"` (la única aceptada), `bite_registered: false`, `software_version`.
- `arches.{upper|lower}`: `original {rel_path, sha256, format, size_bytes, source_name}` y `geometry_report`.
- `teeth.{FDI}`:
  - `original` y `geometry_report`.
  - `frame {origin, axes (x MD, y VL, z eje largo), source}`.
  - `movement {md_mm, vl_mm, oc_mm, rot_deg, tip_deg, torque_deg}`.
  - `locked`.

**Principio:** la geometría nunca se reescribe. La posición de cada diente = malla original + movimiento absoluto respecto de la posición inicial. La matriz se recalcula de forma determinista (`W = F · T·Rz·Ry·Rx · F⁻¹`), por lo que reabrir un proyecto da una matriz idéntica bit a bit.

Pendiente para el esquema 2: versiones de setup con nombre (inicial, propuesta A, aprobada), landmarks, segmentación por vértice y registro de mordida.

## 7. MVP de la Fase 1: qué hace y qué no

**Implementado y probado:**
- Importa la arcada superior y la inferior (STL/PLY/OBJ) sin alterar el archivo y verifica su integridad con SHA-256.
- Diagnóstico geométrico: valores no finitos, triángulos degenerados, aristas no-manifold, superficie abierta, componentes separados y advertencias de escala (metros, centímetros, unidades desconocidas). Nunca reescala automáticamente.
- Importa dientes ya segmentados, uno por archivo, con el FDI tomado del nombre del archivo (o preguntado si es ambiguo) y validación ISO 3950.
- Movimientos numéricos de 6 GDL por diente, con convención documentada, bloqueo de dientes, deshacer y rehacer, y restauración de la posición inicial.
- Visualización: mostrar u ocultar elementos, transparencia, vistas predefinidas, posición inicial superpuesta y color por diente.
- Guardado atómico; reapertura con verificación de integridad; registro de auditoría.

**No implementado (y no se muestra en la interfaz como si lo estuviera):**
- Manipuladores 3D por arrastre y movimiento de grupos.
- Registro de mordida y versiones de tratamiento.
- Ejes anatómicos reales.
- Distancias interproximales y colisiones.
- Exportación.

**No verificado:** la ejecución de la interfaz con `QtInteractor` en Windows. Las pruebas corrieron en Linux sin pantalla (render offscreen). La verificación manual en Windows está en `docs/ESTADO_PROYECTO.md`.

## 8. Pruebas de aceptación de la Fase 1 (umbrales definidos)

| ID | Criterio | Umbral | Estado |
|---|---|---|---|
| AC1 | Los originales importados son idénticos a la fuente | Bytes idénticos (SHA-256) | ✅ automatizada |
| AC2 | Guardar → reabrir reproduce la transformación | Matriz 4x4 igual bit a bit; movimiento idéntico | ✅ automatizada |
| AC3 | Mover un diente no deforma la corona | Error de distancias por pares < 1e-9 mm | ✅ automatizada |
| AC4 | Se detecta un original alterado | La carga falla con un error de integridad | ✅ automatizada |
| AC5 | Se detecta un original faltante | La carga falla con un error de integridad | ✅ automatizada |
| AC6 | La matriz del render es igual a la del núcleo | `allclose` (atol 1e-8) | ✅ automatizada (offscreen) |
| AC7 | Flujo de interfaz: seleccionar → mover → deshacer → rehacer → guardar → reabrir | El movimiento se conserva | ✅ automatizada (offscreen) |
| AC8 | Se advierte una escala en metros | Hay advertencia y no se reescala | ✅ automatizada |
| AC9 | La aplicación abre en Windows y muestra un escaneo real anonimizado | Manual | ⏳ pendiente (usuario) |
| AC10 | Interacción fluida con ambas arcadas reales | ≥ 30 fps al rotar; carga < 10 s por arcada (meta inicial, ajustable) | ⏳ pendiente de medir |
