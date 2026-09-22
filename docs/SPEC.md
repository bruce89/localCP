# SPEC de Local CP

Estado: iteración 2, prueba de concepto de asistencia de IA para un archivo.

## Problema y propuesta

El usuario necesita entender un archivo de un proyecto local sin recorrer todo el
repositorio ni depender siempre de un proveedor de IA. Local CP ofrece exploración
y análisis local; cuando el usuario lo decide, envía una pregunta y un archivo
revisado a un proveedor configurable.

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

## Iteración 2 — prototipo actual

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

## Iteración 3 — candidatos

- [ ] Selección explícita de varios archivos con presupuesto agregado.
- [ ] Señales locales de posibles secretos antes de enviar.
- [ ] Proveedor alternativo implementando el mismo contrato.
- [ ] Cancelación de solicitud y mejor manejo de estados de carga.
- [ ] Conteo preciso de tokens cuando el proveedor lo permita.
- [ ] Empaquetado y pruebas de instalación para Windows 11.

## Referencias de integración

- [Compatibilidad OpenAI de Gemini](https://ai.google.dev/gemini-api/docs/openai)
- [Límites de la API de Gemini](https://ai.google.dev/gemini-api/docs/rate-limits)
