# Convenciones de ejes, signos y pivotes

Este documento es normativo. Si el código y este documento discrepan, es un error. La implementación está en `src/ortosetup/core/transforms.py` y las pruebas en `tests/test_transforms.py`.

## Unidades
- Longitud: **milímetros**. Ángulos: **grados** en la interfaz y en `project.json`.
- Coordenadas de escaneo: las del archivo original, sin reescalar ni reorientar.

## Sistema local por diente (`ToothFrame`)
| Eje | Significado | Positivo hacia |
|---|---|---|
| x | mesiodistal | mesial |
| y | vestibulolingual | vestibular |
| z | eje largo | oclusal / incisal |

- Los ejes son columnas ortonormales y forman un sistema dextrógiro (se valida al cargar).
- **Pivote** = `origin` (todas las rotaciones son en torno a este punto).
- **Fase 1 (provisional):** `origin` = centroide de superficie de la malla del diente; ejes = ejes del archivo (`source = "provisional_world_axes_centroid"`). Por lo tanto, en la Fase 1 "mesiodistal" significa realmente "eje X del archivo". Los nombres clínicos solo serán correctos cuando la Fase 3 defina los ejes desde landmarks.

## Movimiento (`Movement6DOF`), absoluto respecto de la posición inicial
| Campo (formato del proyecto) | Tipo | Eje | Etiqueta en la interfaz con ejes provisionales | Nombre clínico (solo con ejes aprobados) |
|---|---|---|---|---|
| `md_mm` | traslación | x | Traslación X | mesiodistal |
| `vl_mm` | traslación | y | Traslación Y | vestibulolingual |
| `oc_mm` | traslación | z | Traslación Z | extrusión (+) / intrusión (−) |
| `rot_deg` | rotación | z | Rotación sobre Z | rotación axial |
| `tip_deg` | rotación | y | Rotación sobre Y | angulación (tip) |
| `torque_deg` | rotación | x | Rotación sobre X | inclinación (torque) |

- **Nomenclatura (prompt maestro §8.3):** mientras los ejes del diente no estén aprobados por el ortodoncista, la interfaz muestra el grupo como "Movimiento cartesiano (ejes del archivo)" y usa solo las etiquetas cartesianas. Los nombres de los campos internos no cambian porque son el formato del proyecto (esquema 1).

- Signo de las rotaciones: **regla de la mano derecha** sobre el eje local.
- Orden: `L = T · Rz(rot) · Ry(tip) · Rx(torque)`; en coordenadas de escaneo, `W = F · L · F⁻¹`.
- Como x apunta a mesial en todos los cuadrantes, el mismo número de torque o rotación puede tener un significado clínico distinto según el cuadrante. La tabla de signos clínicos por cuadrante se definirá en la Fase 3, y hasta entonces no se interpretan clínicamente.
- Los movimientos son **coronarios y virtuales**: no representan movimientos radiculares reales.
