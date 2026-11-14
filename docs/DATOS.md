# Datos: normativa, origen y tratamiento

Registro exigido por el prompt maestro §3 antes de usar datos reales. La información legal se verifica en fuentes oficiales al momento de decidir; esto **no es asesoría legal**.

## 1. Estado normativo (consulta: 13-11-2026)

| Norma | Estado a la fecha de consulta | Fuente |
|---|---|---|
| Ley 19.628 (protección de la vida privada) | Vigente. | BCN / Diario Oficial |
| Ley 21.719 (reforma la 19.628 y crea la Agencia de Protección de Datos Personales) | Publicada el 13-12-2024. **Entra en vigencia el 1-12-2026** según su artículo primero transitorio. | Oficiales: Cámara de Diputados (camara.cl, "Ley de Protección de Datos Personales"); Gobierno Digital (wikiguias.digital.gob.cl, "Guía práctica de implementación"). |
| Proyecto de ley que posterga la Ley 21.719 al 1-12-2027 (boletín informado como 18.623-07) | **En tramitación, no vigente.** Mientras no se apruebe y publique, la fecha legal sigue siendo el 1-12-2026. | Fuentes secundarias (Garrigues, prensa especializada). **Pendiente: confirmar en senado.cl antes de cualquier uso de datos de terceros.** |

**Implicancias para el proyecto:**
- Los datos de salud son **datos sensibles** en ambos regímenes.
- Desde el 1-12-2026 (si no se posterga), cualquier tratamiento de escaneos de **terceros** exige base de licitud, finalidad declarada y medidas de seguridad. Esto incluye pacientes del hospital o de la práctica privada.
- El software sigue siendo **experimental**, sin uso diagnóstico ni terapéutico. Su eventual clasificación como dispositivo médico (ISP) no se ha evaluado.

## 2. Escaneo usado en AC10

| Campo | Registro |
|---|---|
| Origen | Escaneo intraoral **de la propia boca del propietario del proyecto**. No involucra pacientes ni terceros. |
| Consentimiento | El titular de los datos es el propio propietario, que decide usarlos para el desarrollo de este software (13-11-2026). |
| Formato | STL. |
| Finalidad | Exclusivamente medir el rendimiento técnico (AC10): triángulos, tiempo de carga, FPS y memoria. |
| Desidentificación | 1) Copiar el archivo con un nombre neutro (p. ej., `ac10_superior.stl`). 2) `MEDIR_RENDIMIENTO.bat` revisa si la cabecera del STL contiene texto, como el software, la fecha o un nombre. 3) El reporte `rendimiento_ac10.txt` omite el nombre, la ruta y el texto de la cabecera. |
| Almacenamiento | **Solo en el equipo del propietario**, fuera del repositorio: `C:\dev\datos_ac10\`. Las mallas (`*.stl`, `*.ply`, `*.obj`) y `rendimiento_ac10.txt` están en `.gitignore`. |
| Qué se comparte | **Solo** el texto de `rendimiento_ac10.txt` (sin datos identificables). El escaneo **no** se sube a GitHub, ni a Claude, ni a ningún servicio externo. |
| Conservación | Mientras sea útil para medir rendimiento en la Fase 1 y para repetir AC10 tras cambios de rendimiento. |
| Eliminación | El propietario borra `C:\dev\datos_ac10\` cuando ya no sea necesario. No existen otras copias generadas por el proyecto. |

## 3. Antes de usar escaneos de terceros (pendiente; no autorizado aún)
- Confirmar en fuentes oficiales el estado de la Ley 21.719 y del proyecto de postergación.
- Consentimiento escrito y específico para investigación o desarrollo de software.
- Si los datos vienen de una institución (p. ej., el hospital): autorización institucional y, si corresponde, comité de ética.
- Procedimiento de desidentificación verificado, almacenamiento cifrado y plazos de conservación y eliminación.
