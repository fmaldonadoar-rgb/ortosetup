# Registro de licencias

Regla: el código, los pesos de modelos y los datasets se registran **por separado**. Ningún componente se integra con su licencia en estado "por verificar".

## Dependencias en uso (Fase 1)
| Componente | Uso | Licencia | Verificado |
|---|---|---|---|
| NumPy | núcleo | BSD-3 | sí |
| trimesh | lectura y análisis de mallas | MIT | sí |
| VTK | render | BSD-3 | sí |
| PyVista / pyvistaqt | render e integración con Qt | MIT | sí |
| PySide6 (Qt for Python) | interfaz | LGPL-3.0 (enlace dinámico; incluir aviso al distribuir) | sí |
| pytest | pruebas | MIT | sí |

## Candidatos de segmentación (Fase 2): NO integrados
| Candidato | Código | Pesos | Datos de entrenamiento | Estado |
|---|---|---|---|---|
| SlicerDentalModelSeg (UNC/UMich) | por verificar | por verificar | propios (~1000 IOS) | evaluar; solo Linux + CUDA |
| SlicerAutomatedDentalTools (DCBIA) | por verificar | por verificar | por verificar | evaluar |
| MeshSegNet (Lian et al.) | MIT | incluidos en el fork de Tai-Hsien: por verificar | 36 escaneos propios | referencia mínima |
| TSegFormer / soluciones 3DTeethSeg'22 | por verificar | por verificar | probablemente Teeth3DS | evaluar |
| Teeth3DS+ (dataset) | — | — | "Other" en OSF: **por verificar** (posible uso no comercial) | no usar hasta verificar |
