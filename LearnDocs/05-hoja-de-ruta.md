# Hoja de aprendizaje

No es un temario para estudiar de corrido. Cada etapa termina cuando podés
**explicar y demostrar** un comportamiento de Local CP. Si ya dominás una parte,
hacé el ejercicio de comprobación y avanzá.

## A — entorno y ejecución

Conceptos: intérprete, `.venv`, `pip`, `pyproject.toml`, módulo, paquete, import y
entry point. Ejercicio: [identificar el Python activo](03-ejercicios.md#1-qué-python-ejecuta-el-proyecto).
Dominio: explicar por qué instalar PySide6 en otro Python no lo hace visible aquí
y seguir `python -m local_cp` hasta `MainWindow`.

## B — datos y errores

Conceptos: función, `Path`, colecciones, `dataclass`, `None`, anotaciones y
excepciones. Ejercicio: comparar una lectura de archivo que puede fallar con
`analyze_python_source`, que transforma texto en `PythonAnalysis`. Dominio:
predecir qué devuelve una fuente inválida y qué caso levanta una excepción.

## C — análisis local

Conceptos: `ast`, estructura de un módulo, sintaxis frente a ejecución,
exploración de carpetas y límites de archivos. Ejercicio: seguir
[`python_analyzer.py`](../src/local_cp/analysis/python_analyzer.py) con una clase y
un método propio. Dominio: explicar qué información detecta y qué no puede saber
sin ejecutar el programa o hacer análisis más profundo.

## D — interfaz y concurrencia

Conceptos: eventos, señales Qt, hilo principal, `QThreadPool` y estado de la
pantalla. Ejercicio: seguir selección → análisis → resultado. Dominio: indicar
qué función trabaja fuera de la GUI y dónde se muestra un error.

## E — red opcional y proveedores

Conceptos: request/response, JSON, timeout, límite de entrada, token estimado,
variable de entorno, `Protocol` y fake. Ejercicio: preparar contexto sin red y
leer [`test_ai_service.py`](../tests/test_ai_service.py). Dominio: explicar qué
acción envía fuente, cómo se reemplaza el proveedor y por qué una prueba con fake
no demuestra que la API externa esté disponible hoy.

## F — contexto de varios archivos (I3)

Conceptos: lista ordenada, copia de datos para una vista previa, validación por
elemento frente a presupuesto agregado, y estado inválido después de un cambio.
Ejercicio: [laboratorio I3](06-I3-contexto-multiple.md). Dominio: demostrar que
seleccionar en el árbol no envía ni agrega archivos, y que cambiar la lista obliga
a preparar otra vista previa.

## G — advertencia local de secretos (I4)

Conceptos: heurística, falsos positivos y negativos, función pura, línea de
origen y confirmación ligada a una vista previa. Ejercicio:
[laboratorio I4](07-I4-aviso-secretos.md). Dominio: explicar por qué un resultado
vacío del detector no demuestra que el archivo sea seguro para compartir.

## H — siguiente iteración de producto

Elegir **una** mejora del [SPEC](../docs/SPEC.md), formular un caso observable,
escribir la prueba que la haría verificable y recién después implementar. Algunas
opciones actuales: cancelación o conteo más preciso de tokens. No sumes
abstracciones por anticipado: primero
encontrá el cambio concreto que las necesita.

Al cerrar cada etapa, completá una [ficha de sesión](04-bitacora.md) y dibujá de
memoria el recorrido de datos. Si una flecha todavía es “acá hace magia”, ése es
un buen tema para la próxima sesión.
