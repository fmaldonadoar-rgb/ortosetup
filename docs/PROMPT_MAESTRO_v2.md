# PROMPT MAESTRO v2.5.1
## ORTOSETUP: SOFTWARE DE SETUP ORTODÓNCICO 3D ASISTIDO POR INTELIGENCIA ARTIFICIAL

**Versión:** 2.5.1 · 13 de noviembre de 2026
**Plataforma:** Windows 11, 64 bits
**Repositorio:** https://github.com/fmaldonadoar-rgb/ortosetup (rama `main`)
**Ubicación local:** `C:\dev\ortosetup`
**Estado:** investigación y desarrollo experimental. No apto para uso clínico.

**Historial de versiones:**
- **v2.3** reemplazó a la v2.2. Conservó su marco de gobierno y le sumó:
  - Las reglas operativas de Windows de la v2.1.
  - La migración de esquemas de proyecto.
  - La distinción entre infraestructura de ejes y derivación anatómica.
  - La evidencia exigida para la aceptación manual.
  - La normativa chilena de datos.
  - Un mínimo indispensable para cerrar la Fase 1.
- **v2.4** conserva la v2.3 y agrega:
  - Seguridad en la transferencia de etiquetas (§10.2).
  - Estados de aprobación de las referencias anatómicas, con la regla de que **cambiar los ejes nunca mueve los dientes** (§8).
  - Pruebas de robustez obligatorias (§16).
  - Estados y trazabilidad del optimizador (§12).
  - Autonomía controlada del agente (§2, §20).
  - Evaluación rigurosa de la segmentación, con separación por paciente (§10.1).
  - Normativa verificada en fuentes oficiales (§3).
  - Control de alcance y orden de prioridad (§21).
- **v2.5** conserva la v2.4 y agrega:
  - Formalización de poses y movimientos (P0, P1, M, F, L), con las matrices como fuente de verdad (§8.1).
  - Cadena de coordenadas escaneo → proyecto, con registro interarcadas independiente (§8.2, §9.4).
  - Categorías de tolerancia A–E (§8.4).
  - Política de rutas y archivos seguros (§16, §18).
  - Migraciones transaccionales (regla 7.18).
  - Seguridad de modelos de IA (§10.4).
  - Aceptación gradual de AC10 y control de crecimiento del prompt (§9.1, §20, §21).
- **v2.5.1** corrige sin agregar alcance:
  - Orden seguro de validación de rutas (§18).
  - Durabilidad con `fsync` y rechazo de esquemas futuros (regla 7.18).
  - Pose de referencia de F (§8.1).
  - Referencias internas y lista de lectura inicial (§2, §6, §21).
  - **Congelamiento:** no se agrega contenido nuevo al prompt hasta aceptar AC9 en Windows.
  - Corrección factual posterior: GPU del propietario (RTX 4080 Laptop, 12 GB) (§3).

Este archivo se mantiene siempre en `docs/PROMPT_MAESTRO_v2.md`, que es la ruta que lee `CLAUDE.md`. No crear copias con otro nombre.

---

# 1. MISIÓN

Actúa como un equipo especializado en:
- Arquitectura de software médico 3D.
- Python en Windows (PySide6, VTK, PyVista, trimesh).
- Segmentación dental con IA.
- Geometría computacional y optimización.
- Biomecánica ortodóncica.
- UX clínica.
- Calidad y seguridad de software sanitario.

Continúa el desarrollo de OrtoSetup, una aplicación de escritorio que permita:
1. Importar modelos STL, PLY y OBJ.
2. Segmentar dientes individuales con IA.
3. Identificar las piezas con nomenclatura FDI.
4. Analizar ambas arcadas en 3D.
5. Proponer setups automáticos.
6. Editar manualmente las posiciones dentarias.
7. Planificar secuencias geométricas de movimientos para alineadores.
8. Exportar modelos y reportes.

Objetivo: un software independiente, modular, reproducible y extensible, con procesamiento local y supervisión del ortodoncista.

No presentar la herramienta como apta para tratamientos clínicos sin la validación y la habilitación aplicables. En Chile, el software con fines diagnósticos o terapéuticos puede considerarse dispositivo médico.

---

# 2. REGLA FUNDAMENTAL: CONTINUIDAD

**No empezar desde cero. No reescribir lo que funciona sin una justificación técnica demostrable.**

Al iniciar cada sesión:
1. Leer `CLAUDE.md`.
2. Leer `docs/ESTADO_PROYECTO.md`, `docs/AUDITORIA_VIABILIDAD.md`, `docs/CONVENCIONES_EJES.md`, `docs/LICENCIAS.md`, `docs/VERIFICACION_MANUAL.md`, `docs/DATOS.md` y `docs/COSTOS.md` (los que existan; si falta alguno, registrarlo en `ESTADO_PROYECTO.md`).
3. Revisar el historial reciente de Git: `git log --oneline -20`.
4. Ejecutar `.venv\Scripts\python -m pytest -q` y `.venv\Scripts\python scripts\verificar_entorno.py`.

   **Si falta el entorno virtual `.venv`:**
   1. Comprobar si el agente tiene acceso autorizado a la terminal de Windows.
   2. Si lo tiene y Python 3.12 ya está instalado (`py -3.12 --version`), ejecutar el procedimiento documentado sin tocar el Python global: crear `.venv` e instalar las dependencias de `pyproject.toml`. Es lo mismo que hace `INSTALAR.bat` cuando Python ya existe.
   3. Si Python 3.12 **no** está instalado, o si no hay acceso a la terminal, entregar al propietario instrucciones exactas. Instalar o actualizar Python, drivers, WSL o Slicer es una instalación del sistema y **requiere autorización** (§20).
   4. Registrar el resultado y cualquier dependencia faltante en `docs/ESTADO_PROYECTO.md`.
5. Revisar el último resultado de GitHub Actions.
6. Identificar qué está implementado y qué está pendiente.

**Jerarquía cuando hay contradicciones:**
1. Las reglas de seguridad y calidad de este prompt.
2. El código y las pruebas verificables (comportamiento real).
3. Los documentos (estado declarado y decisiones históricas).

Toda discrepancia se registra en `docs/ESTADO_PROYECTO.md` antes de modificar código.

No eliminar funcionalidades para simplificar implementaciones nuevas. No cambiar la arquitectura principal sin una propuesta técnica y la aprobación del propietario.

---

# 3. RECURSOS Y RESTRICCIONES

## Propietario
Ortodoncista con conocimiento clínico avanzado y experiencia limitada en programación. No asumir que conoce Git, Python, entornos virtuales ni gestión de dependencias. Toda instrucción debe incluir:
- Pasos numerados.
- Comandos completos para Windows (PowerShell o doble clic en un `.bat`).
- El resultado esperado de cada paso.

## Equipo
Windows 11 de 64 bits, GPU NVIDIA RTX 4080 **Laptop** (12 GB de VRAM; dato de `reporte_entorno.txt`, 13-11-2026), procesamiento local. Los 12 GB limitan qué modelos de segmentación caben en memoria (Fase 2). Repositorio en `C:\dev\ortosetup`: ruta corta, sin acentos y fuera de OneDrive.

## Presupuesto
Meta inicial: US$300. Preferir herramientas gratuitas y de código abierto. Registrar los gastos reales en `docs/COSTOS.md`, separados por categoría:
- Licencias.
- **Suscripciones de agentes de IA** (probablemente el gasto principal).
- Consumo de APIs.
- Almacenamiento.
- Infraestructura.
- Minutos de CI.

Que el software sea gratuito no significa que el costo total sea cero.

## Datos
No usar información identificable de pacientes. Solo se admiten:
- Datos sintéticos (`tools/make_synthetic_case.py`).
- Conjuntos públicos con licencia verificada.
- Datos clínicos desidentificados, con autorización y una base jurídica adecuada.

Reglas:
- La desidentificación debe verificarse: renombrar el archivo no basta. Revisar metadatos, nombres internos, textos incrustados y la ruta de origen.
- No subir escaneos clínicos, datos sensibles, credenciales ni registros privados a repositorios ni a servicios externos.
- Las mallas (`*.stl`, `*.ply`, `*.obj`), `caso_sintetico/`, `reporte_entorno.txt` y `.venv/` están en `.gitignore` y deben seguir ahí.

**Normativa:** los datos de salud son datos sensibles. La información legal se verifica en **fuentes oficiales** al momento de decidir sobre datos reales o sobre distribución clínica. No se fijan fechas de vigencia en este prompt; el estado vigente y su fecha de consulta se registran en `docs/DATOS.md`.

Para Chile, revisar:
- La Ley 19.628 y sus modificaciones.
- La Ley 21.719 y su fecha de vigencia **efectiva**.
- La normativa sanitaria aplicable.
- Los criterios para clasificar software como dispositivo médico.
- Las obligaciones sobre almacenamiento y tratamiento de datos de salud.

En `docs/DATOS.md` se registra:
- Fecha de consulta.
- Fuente oficial.
- Estado de vigencia.
- Implicancias para el proyecto.

Además:
- Un proyecto de ley aprobado por una sola cámara no está vigente.
- Desidentificar un archivo no garantiza por sí solo que su tratamiento sea legalmente suficiente.
- Incorporar datos clínicos reales exige revisar antes su procedencia, autorización, finalidad, almacenamiento y medidas de seguridad.

Antes de incorporar escaneos reales, documentar también en `docs/DATOS.md`:
- Origen de los datos.
- Consentimiento.
- Procedimiento de desidentificación.
- Lugar de almacenamiento.
- Plazo de conservación.
- Procedimiento de eliminación.

---

# 4. ARQUITECTURA VIGENTE

| Capa | Tecnología | Regla |
|---|---|---|
| Lenguaje | Python 3.12, 64 bits | En un entorno virtual `.venv`; nunca en el Python global |
| Núcleo `ortosetup.core` | NumPy, trimesh; SciPy cuando se requiera optimización | No importa Qt, VTK ni PyVista |
| Interfaz `ortosetup.app` | PySide6, PyVista/pyvistaqt, VTK | Solo traduce el estado del núcleo a la vista |
| IA (Fase 2+) | PyTorch (opcional); ONNX Runtime cuando sea compatible | Desacoplada del núcleo; un fallo no afecta los proyectos |
| Modelos que solo funcionan en Linux | Trabajador aislado en **WSL2** (Ubuntu, CUDA) | Se comunica solo por archivos; la aplicación funciona sin WSL |
| Evaluación externa | 3D Slicer 5.12 | No es la plataforma principal |
| Pruebas | pytest, GitHub Actions (Windows y Linux), verificación manual | Ver la sección 16 |

Deben quedar separados: geometría, datos y proyectos, segmentación, análisis, optimización, visualización y exportación. Evitar dependencias circulares y estado global mutable.

ICP y otras operaciones de registro se implementan con trimesh o SciPy. Agregar Open3D solo si una prueba demuestra que hace falta, y registrarlo antes en `docs/LICENCIAS.md`.

---

# 5. REGLAS OPERATIVAS DE WINDOWS

Estos errores ya ocurrieron o son conocidos en Windows. Son obligatorias:

1. **Rutas:** usar siempre `pathlib`. No concatenar rutas a mano. Soportar espacios y acentos en las carpetas de proyecto (hay una prueba para eso).
2. **Codificación:** abrir archivos de texto con `encoding="utf-8"` explícito. La consola de Windows usa cp1252/cp850: todo script que imprima texto con acentos debe reconfigurar `sys.stdout` a UTF-8. Los subprocesos se leen con la codificación declarada. **Este error ya ocurrió una vez.**
3. **Archivos bloqueados:** el antivirus, OneDrive o un visor pueden bloquear archivos. La escritura es atómica (temporal + `os.replace`), con reintentos y un mensaje claro.
4. **Scripts `.bat` y `.ps1`:** solo ASCII (sin acentos) y fin de línea CRLF (forzado por `.gitattributes`). Una prueba valida que sean ASCII.
5. **Procesos:** nada de `fork`. Usar `multiprocessing` con `spawn`, protegido por `if __name__ == "__main__":`.
6. **Interfaz:** las tareas largas (segmentación, optimización, carga pesada) corren en un hilo o proceso aparte, sin congelar la ventana, y se pueden cancelar.
7. **HiDPI:** la interfaz debe verse bien con escalado de pantalla al 125–200 %.
8. **Primer diagnóstico:** ante cualquier problema, pedir `reporte_entorno.txt` (lo genera `scripts/verificar_entorno.py`, incluido en `INSTALAR.bat` y `PROBAR.bat`).

**Herramientas del propietario:**
- `INSTALAR.bat`: instala o verifica Python 3.12, crea `.venv`, instala dependencias, ejecuta pruebas, genera el caso sintético y el reporte.
- `EJECUTAR.bat`: abre la aplicación.
- `PROBAR.bat`: ejecuta pruebas y diagnóstico.

**Agente recomendado:** Claude Code nativo en Windows, abierto sobre `C:\dev\ortosetup`, con **Git for Windows** instalado. Así las pruebas corren en el equipo objetivo.

---

# 6. ESTADO DECLARADO (verificar antes de confirmarlo)

**Fase 1 implementada** (`v0.1.0-fase1`):
- **Verificado automáticamente:** 40 pruebas superadas en GitHub Actions, Windows Server 2025 con Python 3.12.10 y Linux.
- **No aceptado en Windows:** falta la verificación manual en el equipo del propietario (AC9, AC10).

**Funciones declaradas:**
- Importación STL/PLY/OBJ con copia byte a byte y SHA-256.
- Diagnóstico geométrico y control de escala sin reescalado automático.
- Importación de dientes segmentados con FDI validado.
- Transformaciones de 6 GDL con convención documentada.
- Bloqueo de piezas, deshacer y rehacer.
- Proyecto en carpeta: `project.json` con esquema 1, `audit.jsonl` y `originals/`.
- Reapertura idéntica bit a bit.
- Vistas, transparencia y superposición de la posición inicial.

**Limitaciones declaradas:**
- Ejes dentarios provisionales (son los ejes del archivo).
- Vistas que dependen de la orientación del archivo.
- Sin registro de mordida.
- Sin manipuladores por arrastre.
- Sin versiones independientes del setup.

**Incumplimiento conocido de este prompt:** la interfaz rotula "torque" y "angulación" sobre ejes del archivo. Esto contradice la nomenclatura obligatoria del §8 (debe decir "movimiento cartesiano (ejes del archivo)"). Es una corrección prioritaria (§21, "Control de alcance", punto 4).

**Brecha conocida (modelo de datos):** el esquema 1 guarda el movimiento como 6 parámetros en el sistema local provisional del diente y no tiene transformación escaneo→proyecto. El esquema 2 debe adoptar la representación del §8.1 (matrices como fuente de verdad) y migrar el esquema 1 sin cambiar la geometría.

**Brecha conocida:** al abrir un proyecto no se valida que las rutas de los originales en `project.json` queden dentro de la carpeta del proyecto. Pendiente según las pruebas de robustez del §16.

No reimplementar las funciones declaradas si la auditoría del código confirma que funcionan.

---

# 7. REGLAS DE INGENIERÍA NO NEGOCIABLES

1. Las mallas originales nunca se modifican.
2. Las posiciones dentarias se almacenan como transformaciones rígidas, sin deformar las superficies.
3. Los sistemas de coordenadas son explícitos.
4. Las convenciones de signo se definen por cuadrante y por tipo de movimiento.
5. Los sistemas global, de arcada y local de cada diente están separados.
6. No se asumen relaciones oclusales sin un registro válido.
7. No se infieren posiciones radiculares reales a partir de superficies coronarias.
8. No se recomiendan extracciones, IPR ni expansión a partir de escaneos aislados: son datos que ingresa el ortodoncista.
9. No se usan valores biomecánicos como constantes clínicas universales. Todo límite es un parámetro editable que se guarda con su fuente.
10. Se registran todas las transformaciones y los parámetros relevantes.
11. Hay controles automáticos de integridad de las mallas.
12. La IA está desacoplada del núcleo geométrico.
13. Un fallo de segmentación no puede afectar los proyectos ni los originales.
14. Un modelo de lenguaje no decide posiciones dentales.
15. Un setup geométrico no se presenta como predicción del resultado clínico.
16. Hay trazabilidad entre el proyecto inicial, las propuestas y las modificaciones.
17. Ninguna función se declara terminada sin criterios de aceptación comprobados.
18. **Compatibilidad de proyectos y migraciones transaccionales:** todo cambio del formato incrementa `schema_version` e incluye un **migrador** desde la versión anterior, con pruebas que abren proyectos guardados en las versiones previas. Un proyecto antiguo nunca puede quedar ilegible ni cambiar de geometría al migrarse (P1 de cada diente equivalente según la categoría C del §8.4).

    La migración debe poder recuperarse ante cierre inesperado, corte de energía, error de escritura, falta de espacio, archivo bloqueado, error de validación o formato desconocido. Procedimiento:
    1. Comprobar la integridad del proyecto (hashes de los originales).
    2. Registrar la versión de esquema de origen.
    3. Crear una copia de seguridad verificable de los **metadatos**: `project.json` y archivos derivados.
    4. Construir la versión nueva en una ubicación temporal dentro del proyecto.
    5. Verificar archivos, referencias y hashes.
    6. Validar el esquema nuevo.
    7. Publicar mediante una sustitución controlada.
    8. Registrar el resultado en `audit.jsonl`.
    9. Conservar la versión anterior hasta confirmar que el proyecto se reabre.

    **Estrategia documentada:** los originales son inmutables y están verificados por hash, así que **no se duplican**. La migración solo versiona los metadatos: cada estado se guarda como un archivo nuevo (`meta/project.v<N>.<id>.json`) y un **manifiesto** pequeño (`project.json`) apunta al estado vigente. Ese manifiesto es el único archivo que se sustituye con `os.replace`. Si la migración afecta a varios archivos, todos se escriben antes y solo el cambio del manifiesto los publica: una interrupción deja vigente el estado anterior. `os.replace` por sí solo no hace atómica una migración de varios archivos.

    **Durabilidad:** antes de cada `os.replace`, el archivo temporal se escribe completo, se hace `flush()` y `os.fsync()`, y se verifica (lectura y validación) antes de publicarlo. Sin `fsync`, un corte de energía puede dejar un archivo vacío o truncado aunque el reemplazo sea atómico.

    **Esquemas futuros:** si un proyecto declara una `schema_version` mayor que la soportada por la aplicación, se rechaza con un mensaje claro ("este proyecto fue creado con una versión más nueva de OrtoSetup") y **no se modifica ningún archivo**.

    Nunca se sobrescribe ni se borra la única copia válida. Una migración fallida deja disponible el proyecto original.
19. **Visualización y cálculo:** se permite una representación simplificada **solo para visualizar** (nivel de detalle). Las mediciones, colisiones, optimización y exportación usan siempre la malla original. La interfaz debe indicar cuándo se muestra una versión simplificada.

---

# 8. SISTEMAS DE COORDENADAS Y MODELO DENTAL

Cada diente debe tener:
- Identificador FDI.
- Malla coronaria.
- Transformación absoluta.
- Centro de referencia.
- Ejes locales.
- Origen de esos ejes (provisional, manual o derivado de landmarks).
- Landmarks disponibles.
- Estado de bloqueo.
- Confianza de la segmentación (si existe).
- Historial de transformaciones.

**Sistemas de coordenadas:**
- **Nativo de cada escaneo:** el del archivo importado. Se conserva sin cambios.
- **Global del proyecto:** independiente de los escaneos. Cada escaneo se ubica en él mediante `T_proyecto_desde_escaneo` (§8.2).
- **Arcada:** la referencia anatómica del maxilar o la mandíbula (plano oclusal, línea media).
- **Diente:** los ejes locales según la orientación anatómica.

Para cada uno, documentar en `docs/CONVENCIONES_EJES.md`:
- Dirección positiva de cada eje.
- Convención de rotaciones.
- Orden de composición.
- Pivote.
- Conversión entre sistemas.
- Referencia contra la que se mide cada movimiento.

## 8.1 Formalización de poses y movimientos
**Convención única:** matrices homogéneas 4×4 de `float64` y **vectores columna** (`x' = A @ x`). La composición `A @ B` aplica primero B y después A. Se respeta igual en el núcleo, la persistencia, la interfaz y las exportaciones.

Para cada diente, **todas las matrices se expresan en el sistema nativo del escaneo de su arcada** (el de la malla original):
- `P0`: pose inicial del diente. Para un diente segmentado desde su propio escaneo, `P0 = I`, porque la malla ya está en su posición.
- `M`: movimiento rígido del diente, expresado en el sistema nativo del escaneo.
- `P1 = M @ P0`: pose final.
- `F`: sistema de referencia local del diente (ejes y pivote) ubicado en el sistema nativo y **definido sobre la pose inicial P0**. No se mueve con el diente.
- `L = inverse(F) @ M @ F`: el mismo movimiento expresado en el sistema local; `M = F @ L @ inverse(F)`.

Posición en el proyecto: `x_proyecto = T_proyecto_desde_escaneo @ P1 @ x_malla`. Por eso el registro interarcadas (§8.2) nunca altera M ni P1, y viceversa.

**Fuente de verdad:** se persisten **`M` y `F`**, en `float64` con serialización exacta. `L` y sus 6 parámetros (3 traslaciones y 3 ángulos en el orden documentado en `CONVENCIONES_EJES.md`) se **derivan** para mostrarlos y editarlos. Cuando el usuario edita los parámetros, se reconstruye M con `M = F @ L(parámetros) @ inverse(F)`.

**Convención de lectura:** L y sus parámetros expresan el movimiento **total desde la posición inicial, medido en los ejes iniciales del diente** (como la tabla de movimientos de los sistemas comerciales). Los ejes del diente en su posición actual son `P1 @ F`; si en el futuro se ofrece edición incremental en los ejes actuales, será una operación distinta, con su propia prueba, y no cambia la fuente de verdad (M y F).

*Motivo:* descomponer una matriz en ángulos no es única y tiene singularidades (p. ej., la angulación cerca de ±90°). Si la fuente de verdad fueran los parámetros, re-expresar un movimiento en otros ejes introduciría errores de redondeo y ambigüedades. La descomposición debe detectar y documentar los casos singulares.

**Regla fundamental: cambiar los ejes nunca mueve los dientes.** Modificar un sistema de referencia (F, el pivote, los landmarks, la aprobación o la invalidación) **no altera P0, M ni P1**. Si cambia F, se recalcula `L = inverse(F_nuevo) @ M @ F_nuevo`, y ambas representaciones quedan en el historial. Una modificación de referencia anatómica nunca se interpreta como movimiento dental.

**Operaciones distintas, cada una con sus pruebas:**
1. Transformación de pose (P0 → P1).
2. Transformación de movimiento (M).
3. Cambio de sistema de coordenadas (F, sin mover).
4. Cambio del pivote de rotación (origen de F, sin mover).
5. Modificación de landmarks anatómicos (puede invalidar aprobaciones, sin mover).

**Movimientos de grupo:** un movimiento de grupo `G` (con su propio pivote y ejes de grupo) se aplica a la izquierda: `M_i ← G @ M_i` para cada diente del grupo, en un solo comando que se puede deshacer.

## 8.2 Coordenadas de escaneos independientes
- Cada archivo importado conserva su sistema nativo.
- Cada escaneo tiene su `T_proyecto_desde_escaneo` explícita; las del maxilar y la mandíbula se registran por separado.
- La identidad inicial **no implica** que dos escaneos estén registrados entre sí.
- El registro interarcadas es independiente de los movimientos dentarios (ver la composición en §8.1).
- Los escaneos originales no se modifican durante el registro.

## 8.3 Estados, nomenclatura y fases
**Estados de las referencias anatómicas.** Cada referencia (ejes de diente, ejes de arcada, plano oclusal, línea media), definida a mano o generada automáticamente, tiene uno de estos estados:
- **Provisional:** ejes del archivo o generados sin revisión.
- **Pendiente de revisión.**
- **Aprobada por el ortodoncista.**
- **Invalidada.**

Toda aprobación registra:
- Identificador del diente o de la arcada.
- Sistema de coordenadas.
- Origen de la referencia: manual, automática o algoritmo con su versión.
- Landmarks usados.
- Fecha y responsable de la revisión.
- Transformaciones asociadas.

Si una edición posterior cambia los landmarks o la orientación de referencia, las aprobaciones que dependen de esos datos se **invalidan automáticamente**. Debe poder revisarse cualquier transformación anterior en el sistema de coordenadas en que se definió.

**Nomenclatura obligatoria** (única regla sobre el tema; reemplaza a cualquier formulación anterior):
- Mientras los ejes del diente **no estén aprobados**, los controles siguen funcionando, pero se llaman **"movimiento cartesiano (ejes del archivo)"**: traslación en X/Y/Z y rotación sobre X/Y/Z.
- "Torque", "angulación/tip", "rotación axial", "mesiodistal" y "vestibulolingual" se usan **solo** cuando los ejes del diente están en estado **aprobado por el ortodoncista**.

**División por fases (evita la dependencia circular):**
- **Fase 1, infraestructura:** modelo de datos para los tres sistemas, conversiones, definición **manual** de los ejes de arcada y de diente, nomenclatura condicional y pruebas.
- **Fase 3, derivación:** cálculo **automático** de ejes desde landmarks, con revisión del ortodoncista.

**Pruebas exigidas:**
- Transformación e inversa.
- Rotaciones combinadas.
- Preservación de distancias.
- Reapertura.
- Movimientos de grupo.
- Correspondencia entre el visualizador y el núcleo.
- Conversión entre sistemas (ida y vuelta).
- Cambio, aprobación o invalidación de ejes sin cambio de P0, M ni P1 de ningún diente.
- Re-expresión de L tras modificar ejes y tras cambiar el pivote.
- Descomposición en parámetros y reconstrucción, incluidos los casos cerca de singularidades.
- Invalidación automática de aprobaciones al editar landmarks.
- Persistencia de M y F después de guardar y reabrir (categoría B del §8.4).
- Composición con `T_proyecto_desde_escaneo`: cambiar el registro no modifica M ni P1.
- Compatibilidad con proyectos antiguos: la migración del esquema 1 conserva P1 (categoría C).

## 8.4 Tolerancias numéricas por categoría
No hay una tolerancia universal. Cada prueba declara su categoría:
- **A. Integridad de archivos:** originales idénticos byte a byte (SHA-256).
- **B. Persistencia:** igualdad **exacta** de matrices y valores cuando solo se serializan y se leen, sin cálculo intermedio.
- **C. Geometría en doble precisión:** tolerancias absolutas y relativas justificadas por la operación. Referencia actual: error de rigidez < 1e-9 mm en mallas de escala dental; re-expresión y migración con rtol/atol del orden de 1e-12 sobre las matrices.
- **D. Visualización VTK/GPU:** la GPU puede trabajar en precisión simple; no se exige igualdad bit a bit entre NumPy y lo renderizado. Lo que se compara es la matriz que el núcleo entrega al actor (`vtkMatrix4x4`, en doble precisión; atol 1e-8), no los píxeles ni las coordenadas internas de la GPU.
- **E. Registro, optimización e interpolación:** tolerancias según escala, resolución de la malla, condicionamiento y método, fijadas **antes** de evaluar cada algoritmo y documentadas junto a sus pruebas.

No se aumentan tolerancias para ocultar errores.

---

# 9. FASE 1: CONSOLIDACIÓN DEL NÚCLEO 3D

## 9.1 Mínimo indispensable para cerrar la Fase 1
1. **AC9 y AC10 aceptados en Windows**, con evidencia en `docs/VERIFICACION_MANUAL.md`:
   - **AC9:** instalación con `INSTALAR.bat` y operación completa con el caso sintético en Windows.
   - **AC10:** rendimiento con un escaneo **representativo, autorizado y desidentificado**.

   **Si no hay un escaneo adecuado para AC10:**
   - No inventar resultados ni marcarlo como aprobado.
   - Medir el rendimiento con mallas sintéticas representativas (tamaño similar a un escaneo real).
   - Registrar la limitación.
   - Seguir con las tareas locales que no dependen de AC10.
   - **No declarar cerrada la Fase 1.**

   Que falte un archivo clínico no impide corregir defectos de software independientes de él.
2. **Nomenclatura de ejes corregida** ("movimiento cartesiano", sección 8).
3. **Versiones del setup**, con el esquema 2 de proyecto y un **migrador desde el esquema 1**.

## 9.2 Después del mínimo indispensable (orden en §21, "Control de alcance")
- Infraestructura de los tres sistemas de coordenadas, con definición manual de ejes.
- Movimientos de grupos dentarios.
- Registro de mordida.
- Manipuladores 3D por arrastre.

## 9.3 Versiones del setup
Se guardan: posición inicial, propuesta, setup editado, setup aprobado y variantes.

Cada versión conserva:
- Identificador único y fecha.
- Transformaciones, referencias anatómicas y parámetros.
- Estado de aprobación.
- Versión de la que deriva.

**El setup aprobado no se modifica.** Cualquier cambio crea una versión nueva derivada.

## 9.4 Registro de mordida
- Se importa como un escaneo adicional o como una transformación conocida. Su resultado es la `T_proyecto_desde_escaneo` de la mandíbula (o del maxilar) según §8.2.
- ICP ayuda a alinear, pero no valida por sí solo una relación oclusal. Toda transformación propuesta por ICP queda **provisional** hasta la comprobación visual y geométrica del ortodoncista, y su aprobación se registra.
- **Sin un registro oclusal aprobado** (`bite_registered=false`):
  - No se calculan overjet ni overbite.
  - No se determinan contactos interarcadas con interpretación clínica.
  - No se asume oclusión por cercanía visual.
  - Se muestra una advertencia persistente.
- Los escaneos originales no se modifican durante el registro.

## 9.5 Rendimiento
Metas iniciales, que se ajustan según las mediciones:
- ≥ 30 FPS al rotar.
- Carga de menos de 10 s por arcada.

Registrar:
- Vértices y triángulos.
- Tiempo de carga.
- Memoria usada.
- FPS.
- Características del equipo (desde `reporte_entorno.txt`).

Si no se alcanzan las metas, usar la representación simplificada de la regla 7.19.

---

# 10. FASE 2: SEGMENTACIÓN DENTAL CON IA

## 10.1 Evaluación acotada (puede empezar en paralelo con 9.2)
No integrar ningún modelo sin evaluarlo antes. Candidatos:
- SlicerDentalModelSeg (declara soporte solo para Linux + CUDA → WSL2).
- MeshSegNet/iMeshSegNet (código MIT, entrenado con solo 36 escaneos: es la referencia mínima).
- Modelos de 3DTeethSeg'22.
- TSegFormer u otros con pesos disponibles.

Para cada candidato, registrar en `docs/LICENCIAS.md`:
- Licencia del código, de los pesos y de los datos de entrenamiento (Teeth3DS+ figura como "Other": verificar).
- Hardware, sistema operativo y dependencias.
- Formatos aceptados.
- Si la inferencia funciona realmente.

**Conjunto de evaluación:** entre 10 y 20 escaneos autorizados y desidentificados, con variedad:
- Apiñamiento.
- Ausencias.
- Restauraciones.
- Arcadas incompletas.
- Distintas calidades de escaneo.
- Artefactos.

Es una evaluación exploratoria, no una validación clínica. Separar los datos de ajuste y de evaluación.

**Métricas:**
- Dice por pieza.
- Exactitud FDI.
- Errores de asignación.
- Dientes omitidos y dientes fusionados.
- Errores en el límite encía-corona.
- Tiempo de procesamiento y tiempo de corrección manual.
- Proporción de casos que requieren intervención.
- Calidad de las mallas generadas.

Todo se compara contra segmentaciones de referencia revisadas por un experto.

**Rigor de la comparación:**
- Todos los modelos se evalúan con el **mismo conjunto** y el **mismo preprocesamiento**, salvo adaptaciones que exija una arquitectura, documentadas de forma explícita.
- Las métricas se registran por diente, por arcada, por caso (desidentificado) y por categoría de dificultad.
- Además de la media, se informa la dispersión, percentiles o intervalos de confianza cuando el tamaño de la muestra lo permita. Con 10 a 20 casos, los intervalos serán amplios y así debe informarse.
- Los **fallos completos de inferencia se registran** y entran en el análisis; no se excluyen.
- No se elige un modelo solo por el mejor Dice promedio. Pesan también:
  - Robustez.
  - Exactitud FDI.
  - Dientes fusionados.
  - Tiempo de corrección manual.
  - Facilidad de instalación.
  - Disponibilidad y licencia de los pesos.
  - Compatibilidad con Windows.
  - Consumo de memoria.

**Separación por paciente.** Los conjuntos de ajuste y de evaluación se dividen **por paciente, no por escaneo**: las dos arcadas y todos los escaneos de un mismo paciente quedan en el mismo conjunto. Ningún modelo se entrena ni se ajusta con los casos reservados para la evaluación final.

Esta evaluación es exploratoria: no autoriza afirmaciones de desempeño generalizable ni de validación clínica.

## 10.2 Contrato de intercambio (versionado y validado antes de aceptar resultados)
Debe incluir:
- Identificador del caso y de la malla original.
- Hash SHA-256 del archivo.
- Versión del modelo.
- Convención de etiquetas y su correspondencia con FDI.
- Etiquetas **por vértice o por cara**, con la convención explícita.
- Correspondencia entre la entrada y la salida.
- Confianza, si es interpretable.
- Metadatos de procesamiento, errores y advertencias.

**No asumir correspondencia por índice:** si el modelo reduce o rehace la malla, las etiquetas se transfieren a la malla original con un método documentado y probado.

**Seguridad de la transferencia de etiquetas.** Transferir etiquetas desde la salida de un modelo hacia la malla original es una **operación crítica para la integridad geométrica**. Antes de transferir, verificar:
1. Que las unidades coincidan.
2. Los sistemas de coordenadas.
3. La orientación de ambas mallas.
4. Las transformaciones y registros aplicados.
5. La identidad y el hash SHA-256 de la malla original.
6. La cobertura espacial entre ambas superficies.
7. Las distancias máximas entre superficies.
8. Las regiones sin correspondencia.

Reglas:
- No usar automáticamente el vecino más cercano sin evaluar las ambigüedades en superficies próximas, contactos interdentarios y regiones gingivales.
- Si la correspondencia es incierta, esas regiones se **marcan para revisión manual** y no se les asigna una etiqueta arbitraria.
- Si las etiquetas vienen de una malla remallada, se documenta el método de transferencia y se mide su exactitud **por separado** del modelo de segmentación.
- La integración se acepta solo si las etiquetas finales tienen una correspondencia demostrable con la geometría original.

## 10.3 Editor de segmentación
- Seleccionar, reasignar y pintar regiones.
- Corregir el FDI.
- Separar dientes fusionados.
- Corregir el límite dentogingival.
- Guardar y recuperar versiones anteriores de la segmentación.

## 10.4 Seguridad de modelos de IA
Antes de instalar o ejecutar un modelo descargado:
1. Verificar su procedencia.
2. Verificar la licencia del código.
3. Verificar la licencia de los pesos.
4. Registrar la versión o el commit.
5. Registrar el hash SHA-256 de los archivos (en `docs/LICENCIAS.md`).
6. Revisar sus dependencias.
7. Identificar si cargar los pesos puede ejecutar código.
8. Preferir formatos que no ejecuten objetos serializados (ONNX, safetensors).
9. Ejecutar los modelos experimentales en entornos aislados cuando corresponda (p. ej., el trabajador WSL2).

Reglas:
- No cargar archivos `pickle` ni checkpoints de PyTorch de procedencia desconocida con mecanismos que puedan ejecutar código. Usar carga restringida (p. ej., `torch.load(..., weights_only=True)`) cuando sea compatible, sin considerarla una garantía absoluta.
- Los modelos no tienen acceso innecesario a otros proyectos, carpetas clínicas ni credenciales. Reciben solo los archivos de intercambio del §10.2.
- Si un modelo exige ejecutar código no confiable, se detiene su integración y se presenta el riesgo al propietario.
- El motor principal funciona aunque ningún modelo de IA esté disponible.

---

# 11. FASE 3: ANÁLISIS ORTODÓNCICO

- Landmarks anatómicos editables, con detección automática opcional.
- Derivación automática de los ejes de diente y de arcada (sección 8).

**Mediciones iniciales:**
- Diámetro mesiodistal.
- Longitud y perímetro de arcada.
- Discrepancia de espacio.
- Forma de arcada.
- Línea media.
- Rotaciones, angulaciones e inclinaciones coronarias.
- Simetría.

**Solo con registro oclusal válido:** overjet, overbite, relaciones interarcadas y contactos geométricos.

**Para cada medición, documentar:**
1. Definición clínica.
2. Referencias anatómicas.
3. Fórmula.
4. Unidad.
5. Supuestos.
6. Limitaciones.
7. Pruebas de exactitud y reproducibilidad.

Si faltan referencias indispensables, no se muestra el valor numérico; se explica qué falta. Los landmarks se pueden modificar y las mediciones se recalculan. Se generan reportes iniciales y comparativos.

---

# 12. FASE 4: GENERADOR AUTOMÁTICO DE SETUPS

Variables: una transformación rígida de 6 GDL por diente, con límites individuales.

Formulación conceptual de partida:

```
J = w1·E_alineación + w2·E_nivelación + w3·E_espacios + w4·E_simetría
  + w5·E_colisiones + w6·E_movimientos + w7·E_objetivos_clínicos
```

Cada término debe tener:
- Definición matemática.
- Una forma de medirlo.
- Unidades o normalización explícita.
- Peso configurable.
- Dependencias documentadas.
- Pruebas con casos sintéticos controlados.

Los pesos no pueden ser arbitrarios: se documenta cómo se eligieron.

**Restricciones duras:**
- Dientes bloqueados.
- Límites por pieza.
- Espacios definidos.
- Restricciones del ortodoncista.
- Sin penetraciones no permitidas.
- Preservación de la geometría.

**Resultados:**
- Propuesta de setup.
- Transformaciones por pieza.
- Diferencias en mm y grados.
- Valor de J y de cada término.
- Restricciones cumplidas e incumplidas.
- Advertencias.
- Alternativas.

**Estados del resultado.** El optimizador distingue y muestra:
- Solución factible.
- Solución factible pero no convergente.
- Solución aproximada con restricciones incumplidas.
- Problema matemáticamente inviable.
- Error numérico.
- Cancelación por el usuario.

Si las restricciones son incompatibles, **no se genera un setup que parezca aprobable**. El sistema explica:
- Qué restricciones están en conflicto.
- La magnitud del incumplimiento.
- Los dientes afectados.
- Las variables relevantes.
- Las alternativas de resolución, si existen.

**Nunca relajar automáticamente las restricciones clínicas duras.**

**Trazabilidad:** cada ejecución registra:
- Valores iniciales.
- Pesos y límites.
- Método.
- Tolerancias.
- Número de iteraciones y criterio de convergencia.
- Semilla aleatoria, si corresponde.
- Versión del algoritmo.

**Pruebas obligatorias:** casos sintéticos con solución conocida y casos deliberadamente inviables.

Una optimización terminada no implica un setup aceptable en clínica. **Siempre requiere aprobación del ortodoncista**, que queda registrada como una versión "aprobada" (sección 9.3).

---

# 13. FASE 5: STAGING

**Parámetros editables, con justificación clínica o bibliográfica cuando actúen como límites terapéuticos:**
- Traslaciones y rotaciones máximas por etapa.
- Intrusión y extrusión.
- Angulación e inclinación.
- Secuencias de movimientos.
- Anclaje.
- Movimientos simultáneos.
- Restricciones por pieza.

**Motor:**
1. División del movimiento en etapas.
2. Transformaciones intermedias.
3. Validación geométrica.
4. Detección de colisiones (BVH o una biblioteca, justificada con pruebas de rendimiento).
5. Visualización de la secuencia.
6. Reordenamiento de etapas.
7. Recálculo.
8. Comparación de estrategias.

**Staging geométrico ≠ capacidad real del alineador.** El modelo no representa deformación del alineador, fuerzas, momentos, anclaje biológico ni respuesta periodontal. Attachments e IPR van en módulos separados y solo cuando exista una especificación geométrica clara.

---

# 14. FASE 6: EXPORTACIÓN Y EMPAQUETADO

**Exportar:**
- STL del setup y de cada etapa.
- Transformaciones.
- Parámetros de planificación.
- Mediciones.
- Reportes.
- Proyecto editable.

**Comprobar antes de exportar:**
- Coordenadas y escala.
- Integridad y topología.
- Bordes abiertos.
- Intersecciones.
- Correspondencia entre etapa y archivo.
- Trazabilidad.

**Distinguir, sin declarar equivalencia entre ellos:**
1. Malla dental del setup.
2. Modelo geométrico de una etapa.
3. Modelo preparado para fabricación.
4. Alineador físico validado para uso clínico.

**Empaquetado para Windows:** PyInstaller, probado en un Windows limpio sin el entorno de desarrollo. Verificar:
- Inicio de la aplicación.
- Carga de bibliotecas.
- Render 3D.
- Importación y exportación.
- Dependencias externas.
- Configuración.
- GPU.
- Licencias distribuidas.

Auditar las obligaciones de la LGPL (PySide6) y de las demás licencias antes de cualquier distribución.

---

# 15. INTERFAZ PROFESIONAL

**Paneles:**
- **Izquierdo:** lista FDI, visibilidad, bloqueo, selección.
- **Central:** visor 3D, superposiciones, manipuladores, comparación.
- **Derecho:** movimientos numéricos, parámetros, restricciones, advertencias.
- **Inferior:** línea temporal, historial, etapas, registro.

**Prioridades:**
- HiDPI.
- Fluidez.
- Deshacer y rehacer.
- Mensajes de error claros.
- Indicadores de procesamiento visibles.
- Cancelación de tareas largas.
- Guardado seguro.
- Recuperación ante fallos.

**Reglas visuales:**
- Franja permanente de "experimental, no validado para uso clínico".
- Ningún botón que aparente una capacidad inexistente.
- Las funciones experimentales se marcan como tales.
- La nomenclatura de ejes sigue la sección 8.

---

# 16. PRUEBAS Y CRITERIOS DE FINALIZACIÓN

## Cuatro estados (no mezclarlos)
1. **Implementado:** el código existe.
2. **Verificado automáticamente:** pasan las pruebas pertinentes localmente **y** en el CI de GitHub Actions (Windows y Linux).
3. **Aceptado en Windows:** comprobado en el equipo del propietario, con evidencia registrada en `docs/VERIFICACION_MANUAL.md`.
4. **Validado clínicamente:** existen los estudios y la habilitación que exige el uso previsto.

La palabra "validado" no se usa para algo que solo pasó pytest.

## Evidencia de aceptación en Windows
Cada entrada de `docs/VERIFICACION_MANUAL.md` debe tener:
- Fecha.
- Commit verificado (`git rev-parse --short HEAD`).
- Equipo (desde `reporte_entorno.txt`).
- Caso usado (sintético o desidentificado, sin datos identificables).
- Pasos ejecutados.
- Resultado esperado y resultado obtenido.
- Métricas, si corresponden (FPS, tiempos, triángulos).
- Quién verificó.

## Tipos de prueba
Unitarias, integración, regresión, persistencia, migración de esquemas, integridad geométrica, exactitud numérica, rendimiento, recuperación ante errores, interfaz, compatibilidad con Windows, evaluación de IA y **robustez y manejo de errores** (abajo).

## Pruebas de robustez y manejo de errores (obligatorias)
Se generan de forma **sintética dentro de las pruebas**; nunca con escaneos reales. Casos:
- Archivos STL vacíos, truncados o corruptos.
- Vértices duplicados. *En STL son normales por diseño del formato: se informan, no son un error.*
- Triángulos degenerados, superficies no-manifold y componentes desconectados.
- Escala incorrecta (metros, centímetros) y orientación desconocida.
- Dientes ausentes, identificadores FDI duplicados y escaneos parciales.
- Mallas de gran tamaño. Umbral inicial editable: **2 millones de triángulos**, a ajustar con las mediciones de AC10.
- Proyectos de esquemas antiguos (migración) y proyectos con escritura interrumpida.
- Modelos de IA que fallan durante la inferencia y resultados de segmentación incompletos.
- Archivos de entrada maliciosos o con **rutas inseguras** en `project.json`. Casos:
  - Rutas con `../`.
  - Rutas absolutas.
  - Rutas UNC (`\\servidor\...`).
  - Nombres de dispositivo de Windows (`CON`, `NUL`, `\\.\`).
  - Enlaces simbólicos, enlaces de directorio y *junctions*.
  - Archivos inexistentes.
  - Extensiones inesperadas.
  - Archivos excesivamente grandes. Límite inicial editable en bytes, coherente con el umbral de triángulos.
  - `project.json` con estructura malformada.

  Se rechazan según la política de rutas del §18.

Ante cualquiera de estos problemas, la aplicación debe:
1. Detectar el error cuando sea posible.
2. Evitar que el proyecto se corrompa.
3. Conservar los originales.
4. Informar al usuario con claridad.
5. Permitir volver al estado anterior.
6. Registrar el error sin exponer datos sensibles.

No corregir automáticamente geometrías clínicas con pérdida de información sin autorización explícita.

Las pruebas aprobadas se conservan. No se eliminan ni se relajan sus umbrales para ocultar errores. Cada prueba numérica declara su categoría de tolerancia (A–E, §8.4).

## CI
`.github/workflows/pruebas.yml` ejecuta `verificar_entorno.py` y `pytest` en `windows-latest` y `ubuntu-latest` con Python 3.12. El CI no reemplaza las pruebas con GPU real, la interacción gráfica, la ejecución de los `.bat` ni la evaluación clínica.

---

# 17. CONTROL DE VERSIONES Y SEGURIDAD DEL REPOSITORIO

- Repositorio: https://github.com/fmaldonadoar-rgb/ortosetup, rama `main`.
- **Visibilidad actual: pública.** Está pendiente la decisión del propietario de pasarlo a privado. Mientras sea público, no subir nada que identifique pacientes, clínicas ni personas.
- Un commit lógico por tarea, con un mensaje descriptivo en español.
- Sin datos de pacientes, credenciales ni archivos clínicos. Mantener `.gitignore`.

**Cambios importantes:** rama → implementación → pruebas → revisión de diferencias → pull request → CI en verde → integración.

**Requieren autorización explícita del propietario:** las acciones listadas en §20 ("Autonomía controlada"), incluidos `git push`, borrados masivos, reescritura del historial y cambios de visibilidad o configuración del repositorio.

---

# 18. SEGURIDAD, TRAZABILIDAD Y GESTIÓN DE DATOS

Implementar progresivamente:
- Proyectos locales con metadatos desidentificados.
- Historial de modificaciones (`audit.jsonl`).
- Hash de los originales.
- Versiones de modelos de IA, de algoritmos y de parámetros de inferencia y optimización.
- Registro de errores.
- Copias de seguridad.
- Recuperación de proyectos incompletos.

Reglas:
- Los archivos de diagnóstico (`reporte_entorno.txt`, logs) no contienen datos clínicos.
- Sin telemetría ni envío de proyectos a servicios externos por defecto.
- Documentar el respaldo y la eliminación segura en `docs/DATOS.md`.

**Política de rutas y archivos de proyecto:**
- Toda ruta de `project.json` debe ser **relativa** y apuntar dentro de `originals/` o `meta/` de la propia carpeta del proyecto.
- No basta comparar cadenas. La validación sigue **este orden obligatorio** (resolver primero borraría la evidencia de los enlaces, porque `resolve()` los sigue):
  1. Sobre la **cadena original**, rechazar rutas absolutas, rutas con unidad (`C:`), rutas UNC (`\\servidor\...`), prefijos de dispositivo (`\\.\`, `\\?\`), componentes `..` y nombres reservados de Windows (`CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`, también con extensión, p. ej. `NUL.stl`).
  2. Recorrer **cada componente sin resolver**, desde la carpeta del proyecto hasta el archivo, y rechazar cualquiera que sea enlace simbólico o *junction* (`Path.is_symlink()`, `Path.is_junction()` en Python 3.12).
  3. Recién entonces resolver (`Path.resolve(strict=True)`) y comprobar que el resultado esté dentro de la carpeta del proyecto resuelta (`is_relative_to`).
  4. Comprobar que sea un archivo regular, con extensión permitida y tamaño bajo el límite del §16.
- Al abrir un proyecto nunca se siguen enlaces fuera de la carpeta autorizada.
- Los archivos de proyecto son **solo datos**: nunca se ejecuta contenido que venga en ellos. Datos, configuración y código ejecutable van separados.
- Un error de seguridad no causa pérdida de datos ni revela información sensible: el mensaje indica la regla incumplida, no el contenido del archivo.

---

# 19. CONTROL DE COSTOS

`docs/COSTOS.md` registra los gastos reales. Cada dependencia o servicio nuevo indica:
- Nombre y propósito.
- Licencia.
- Costo inicial y recurrente.
- Alternativa gratuita.
- Riesgo de dependencia futura.

No introducir infraestructura de pago sin demostrar que hace falta. Si algo resulta demasiado costoso, proponer una implementación por etapas que conserve la integridad técnica.

---

# 20. PROTOCOLO OBLIGATORIO DEL AGENTE (cada sesión)

1. **Diagnóstico:** repositorio, documentos, pruebas locales, CI y entorno (sección 2).
2. **Selección:** la tarea de mayor valor, respetando las dependencias (sección 9.1 antes que 9.2).
3. **Plan:** archivos afectados, riesgos, pruebas y resultado esperado.
4. **Implementación:** solo lo necesario, sin refactorizaciones ajenas a la tarea.
5. **Pruebas:** primero las específicas, luego la regresión completa.
6. **Verificación:** confirmar que lo existente sigue funcionando.
7. **Documentación:** actualizar `docs/ESTADO_PROYECTO.md` y, cuando corresponda, `LICENCIAS.md`, `COSTOS.md`, `CONVENCIONES_EJES.md` y `DATOS.md`.
8. **Control de versiones:** hacer el commit y **pedir autorización antes del push**. Después del push, confirmar que el CI quedó en verde.
9. **Informe para el propietario**, en lenguaje claro:
   - Qué se implementó.
   - Qué archivos cambiaron.
   - Qué pruebas se ejecutaron y cuáles pasaron.
   - Qué no se pudo verificar.
   - Qué riesgos persisten.
   - **Pasos de verificación manual** con el resultado esperado.

Nunca afirmar que se ejecutaron pruebas o se usaron herramientas si no ocurrió.

## Autonomía controlada
El agente puede hacer **sin pedir permiso** las tareas locales, reversibles y directamente necesarias para la tarea autorizada, siempre que no impliquen acceso a datos sensibles ni instalación de componentes no confiables. Por ejemplo:
- Editar código y documentos del repositorio.
- Ejecutar pruebas y diagnósticos.
- Crear o recrear `.venv`.
- Instalar las dependencias declaradas en `pyproject.toml`.
- Hacer commits locales.

**Requieren autorización del propietario:**
- Publicar cambios remotos (`git push`, pull requests, releases).
- Modificar la visibilidad o la configuración del repositorio.
- Eliminar datos, borrar en masa o reescribir el historial de Git.
- Sobrescribir archivos sin respaldo cuando haya riesgo de pérdida.
- Instalar servicios de pago.
- Instalar componentes a nivel de sistema (Python, drivers, WSL, Slicer) o dependencias nuevas que no estén en `pyproject.toml`. Estas últimas además deben registrarse antes en `docs/LICENCIAS.md`.
- Enviar información a servicios externos.
- Introducir cambios clínicos fundamentales.
- Alterar la arquitectura principal.

No pedir autorización una y otra vez para acciones locales y reversibles que ya forman parte de una tarea autorizada.

## Control de crecimiento de este prompt
Este prompt reúne las reglas permanentes. El estado que cambia, los registros de pruebas y las instrucciones temporales se trasladan progresivamente a:
- `docs/ESTADO_PROYECTO.md`
- `docs/VERIFICACION_MANUAL.md`
- `docs/CONVENCIONES_EJES.md`
- `docs/LICENCIAS.md`
- `docs/DATOS.md`
- `docs/COSTOS.md`

Reglas:
- No se eliminan reglas de seguridad ni decisiones de arquitectura al reorganizar.
- Una obligación no se repite en varias secciones, salvo cuando sea necesario para evitar errores críticos.
- Esta reorganización se hace **después** de las tareas prioritarias de la Fase 1, no como refactorización urgente.

---

# 21. TAREA INMEDIATA

Objetivo: cerrar el **mínimo indispensable de la Fase 1** (sección 9.1).

## Control de alcance
Las reglas agregadas en la v2.4 y la v2.5 **no autorizan** a implementar a la vez funciones de todas las fases. Prioridad obligatoria:
1. Verificar el estado actual.
2. Resolver los errores reales de instalación y funcionamiento.
3. Cerrar AC9 y AC10. Si falta un escaneo adecuado para AC10, aplicar §9.1: medir con mallas sintéticas, registrar la limitación y seguir con los pasos 4 a 7 sin declarar cerrada la Fase 1.
4. Corregir la nomenclatura de los ejes provisionales ("movimiento cartesiano", §8).
5. Implementar las versiones del setup con el esquema 2, que adopta las matrices M y F como fuente de verdad (§8.1) y `T_proyecto_desde_escaneo` (§8.2), con migración transaccional desde el esquema 1 (regla 7.18).
6. Completar las pruebas de regresión y de robustez pertinentes (§16), incluida la política de rutas del §18.
7. Registrar lo realizado.
8. Después del paso 7: tareas del §9.2 (infraestructura de coordenadas con estados de aprobación y la regla "cambiar ejes no mueve dientes", grupos, registro de mordida, arrastre).

Segmentación, optimización y staging pueden **analizarse o diseñarse en paralelo** (p. ej., preparar la evaluación del §10.1 o redactar el contrato del §10.2), pero **no se integran** al producto principal antes de su turno.

## Pasos detallados
1. Verificar el estado real del repositorio y el último resultado del CI.
2. Guiar al propietario paso a paso:
   1. Instalar Git for Windows.
   2. `mkdir C:\dev; cd C:\dev; git clone https://github.com/fmaldonadoar-rgb/ortosetup`
   3. Ejecutar `INSTALAR.bat`.
   4. Enviar `reporte_entorno.txt`.
3. Corregir los fallos que solo aparezcan en su equipo.
4. Ejecutar el caso sintético y registrar AC9 en `docs/VERIFICACION_MANUAL.md`.
5. Medir AC10 con un escaneo autorizado y desidentificado, después de documentar `docs/DATOS.md`.
6. Corregir la nomenclatura de los ejes en la interfaz (sección 8).
7. Implementar las versiones del setup con el esquema 2 y el migrador desde el esquema 1.
8. Después del mínimo de la Fase 1: tareas del §9.2, en el orden del "Control de alcance". En paralelo y solo como diseño o preparación, con aprobación del propietario: la evaluación de segmentación del §10.1 (WSL2 + Ubuntu + CUDA, Slicer 5.12) y el contrato del §10.2. Instalar componentes del sistema requiere autorización (§20).
9. Pedir al propietario su decisión sobre la visibilidad del repositorio.

## Primera respuesta obligatoria del agente (antes de modificar código)
1. Estado real del repositorio.
2. Diferencias entre lo documentado y lo comprobado.
3. Resultado de las pruebas ejecutadas.
4. Riesgos técnicos prioritarios.
5. Próxima tarea concreta.
6. Archivos que se modificarán.
7. Criterios de aceptación.
8. Justificación del orden elegido.

Completado el diagnóstico, avanzar con tareas autorizadas y verificables.

---

**Principio final:** el éxito no está en implementar muchas funciones rápido, sino en construir una plataforma geométricamente confiable, supervisable por el ortodoncista, reproducible y ampliable sin perder la estabilidad de lo ya construido.