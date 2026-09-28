# SPEC de Local CP

El recorrido pedagógico, separado de la especificación del producto, está en
[LearnDocs](../LearnDocs/README.md).

Estado: iteración 4, aviso local de posibles secretos antes del envío.

## Problema y propuesta

El usuario necesita entender partes de un proyecto local sin recorrer todo el
repositorio ni depender siempre de un proveedor de IA. Local CP ofrece exploración
y análisis local; cuando el usuario lo decide, envía una pregunta y archivos
revisados a un proveedor configurable.

## Principios

1. El análisis local funciona sin credenciales ni conexión.
2. Ningún archivo se envía por abrirlo, seleccionarlo o analizarlo.
3. El contenido enviado debe verse antes de pulsar **Send**.
4. Proveedores y modelos son configurables, sin dependencia de la GUI en un SDK.
5. Los límites de entrada y salida se aplican por solicitud.
6. Los errores nunca contienen claves ni fuente enviada.

## Iteración 1 — completada

- [x] Abrir un proyecto y explorar archivos.
- [x] Mostrar fuente de texto y estadísticas.
- [x] Extraer clases, funciones e imports de Python con `ast`.
- [x] Ejecutar tareas de análisis fuera del hilo principal.
- [x] Probar el núcleo de análisis automáticamente.

## Iteración 2 — completada

- [x] Contrato `AIProvider` y transporte HTTP compatible con OpenAI.
- [x] Configuración de URL y modelo sin guardar la clave.
- [x] Lectura de `GEMINI_API_KEY` de la variable de usuario de Windows.
- [x] Una pregunta sobre un archivo Python seleccionado.
- [x] Vista previa del contenido exacto y envío explícito.
- [x] Límites de bytes, pregunta, estimación de tokens y salida.
- [x] Solicitud en segundo plano y respuesta legible.
- [x] Pruebas sin red del ensamblado del contexto y del transporte.
- [ ] Validación manual del recorrido visual en Windows.
- [x] Registrar resultado de una solicitud real de extremo a extremo.

### Validación de extremo a extremo (2026-09-22)

Desde la ventana PySide6 de Local CP se abrió el propio proyecto, se seleccionó
`src/local_cp/analysis/models.py`, se preparó la vista previa y se pulsó Send.
La consulta a `gemini-3.5-flash-lite` respondió correctamente a una pregunta sobre
`FunctionInfo`. La vista previa estimó 555 tokens de entrada; el uso informado por
la API fue 272 tokens de entrada y 51 de salida. Se realizó una sola solicitud,
sin reintentos. La prueba se ejecutó con Qt en modo offscreen; queda pendiente una
revisión visual interactiva de la pestaña AI.

### Criterios de aceptación

1. Sin `GEMINI_API_KEY`, la aplicación inicia y el análisis local funciona.
2. Preparar la vista previa no hace ninguna solicitud de red.
3. Enviar un archivo pequeño produce respuesta en la pestaña AI.
4. Un archivo externo, demasiado grande o no Python se rechaza antes de la red.
5. La clave no aparece en Git ni en los mensajes de error.

## Iteración 3 — corte actual

- [x] Selección explícita de hasta tres archivos `.py`, agregados uno por uno.
- [x] Vista previa conjunta con pregunta, rutas y fuente exacta a enviar.
- [x] Presupuesto agregado: 12 KB de fuente y ~4.000 tokens de entrada estimados.
- [x] Agregar/quitar archivos o cambiar la pregunta invalida la vista previa.
- [x] Prueba de la GUI con proveedor simulado y pruebas del presupuesto conjunto.
- [ ] Validación visual interactiva en Windows.
- [x] Solicitud real de dos archivos pequeños desde Local CP.

### Validación de extremo a extremo I3 (2026-09-25)

Desde la ventana PySide6 de Local CP se agregaron manualmente
`src/local_cp/analysis/models.py` y `src/local_cp/analysis/python_analyzer.py`,
se revisó la vista previa con ambos y se pulsó Send una vez. La respuesta de
`gemini-3.5-flash-lite` explicó la relación entre `FunctionInfo` y el analizador,
citando ambos archivos. Estimación local: 1.270 tokens de entrada; uso informado
por la API: 929 tokens de entrada y 111 de salida. La prueba se ejecutó con Qt
offscreen; la revisión interactiva de diseño en Windows sigue pendiente.

### Criterios de aceptación I3

1. Seleccionar en el árbol no agrega archivos ni hace red automáticamente.
2. La lista admite entre uno y tres archivos, sin duplicados y en orden visible.
3. Un archivo fuera del proyecto, demasiado grande o no Python se rechaza antes
   de la solicitud.
4. La vista previa muestra el mismo cuerpo de mensaje que recibe el transporte.
5. Send hace una única solicitud con los archivos preparados; el análisis local
   continúa funcionando sin credenciales.

## Iteración 4 — corte actual

- [x] Buscar patrones evidentes de credenciales en la pregunta y los archivos
  preparados, sin llamadas de red.
- [x] Mostrar sólo ubicación, línea y tipo de posible secreto, nunca el valor.
- [x] Exigir una confirmación adicional antes de habilitar Send si hay hallazgos.
- [x] Invalidar los hallazgos y la confirmación al cambiar pregunta o lista.
- [x] Probar hallazgos, ausencia de falsos positivos comunes y flujo de GUI con
  un proveedor simulado.
- [ ] Revisión visual interactiva en Windows.

### Criterios de aceptación I4

1. Preparar el contexto analiza localmente los mismos textos que se mostrarán en
   la vista previa; el detector no lee otros archivos ni envía nada.
2. Un hallazgo impide Send hasta que el usuario revise la vista previa y marque
   la confirmación de esa preparación concreta.
3. Los avisos no copian valores sospechosos; incluyen ruta o «question» y línea.
4. Cambiar pregunta o archivos borra la confirmación anterior.
5. El detector es una ayuda parcial, no un certificado de ausencia de secretos.

## Candidatos posteriores

- [ ] Proveedor alternativo implementando el mismo contrato.
- [ ] Cancelación de solicitud y mejor manejo de estados de carga.
- [ ] Conteo preciso de tokens cuando el proveedor lo permita.
- [ ] Empaquetado y pruebas de instalación para Windows 11.

## Referencias de integración

- [Compatibilidad OpenAI de Gemini](https://ai.google.dev/gemini-api/docs/openai)
- [Límites de la API de Gemini](https://ai.google.dev/gemini-api/docs/rate-limits)
