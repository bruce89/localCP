# Recorrido real del código y decisiones recuperadas

Esta es una fotografía de las iteraciones 1 y 2. El [SPEC](../docs/SPEC.md) y el
[diagrama vivo](../docs/architecture.md) son la referencia de producto. Acá
reconstruimos el camino de una acción concreta y el motivo práctico de cada
frontera, sin presentar propuestas futuras como si ya estuvieran implementadas.
La ampliación a varios archivos de I3 tiene su [laboratorio propio](06-I3-contexto-multiple.md).

## Lo que se construyó

**Iteración 1:** abrir un proyecto, explorar archivos, mostrar texto, contar tipos
de archivo y extraer imports, funciones y clases de Python con `ast`. Funciona sin
credenciales. **Iteración 2:** una pregunta opcional sobre un `.py` seleccionado,
con vista previa, límite de contexto y envío explícito a una API compatible con
OpenAI. Se verificó una solicitud real; eso no convierte a la IA en requisito del
análisis local.

## Mapa de responsabilidades

| Archivo | Qué observar |
| --- | --- |
| [`pyproject.toml`](../pyproject.toml) | Dependencias, versión mínima, entrada `local-cp` y paquete bajo `src` |
| [`__main__.py`](../src/local_cp/__main__.py) y [`app.py`](../src/local_cp/app.py) | Entrada de `python -m local_cp`, creación de `QApplication` y ventana |
| [`main_window.py`](../src/local_cp/gui/main_window.py) | Árbol, visor, acciones, pestañas y coordinación |
| [`explorer.py`](../src/local_cp/project/explorer.py) | Recorrido del directorio, clasificación y lectura segura |
| [`python_analyzer.py`](../src/local_cp/analysis/python_analyzer.py) | `ast.parse` y extracción de símbolos sin ejecutar el archivo |
| [`models.py`](../src/local_cp/analysis/models.py) | Resultado estructurado del análisis con `dataclass` |
| [`workers.py`](../src/local_cp/gui/workers.py) | Trabajo fuera del hilo de GUI y señales de éxito/error |
| [`ai_panel.py`](../src/local_cp/gui/ai_panel.py) | Pregunta, vista previa, botón Send y respuesta |
| [`context.py`](../src/local_cp/ai/context.py) | Lista explícita de archivos, límite agregado y estimación de tokens |
| [`service.py`](../src/local_cp/ai/service.py) y [`provider.py`](../src/local_cp/ai/provider.py) | Creación del proveedor y contrato reemplazable |
| [`openai_compatible.py`](../src/local_cp/ai/openai_compatible.py) | Construcción HTTP y lectura de la respuesta |
| [`settings.py`](../src/local_cp/config/settings.py) y [`credentials.py`](../src/local_cp/config/credentials.py) | Preferencias no secretas y lectura de clave en tiempo de ejecución |

## Recorrido A: analizar un archivo sin IA

1. `MainWindow.open_project` apunta el árbol al directorio y pide a un `Worker`
   ejecutar `scan_project` para calcular estadísticas.
2. Elegir un archivo llama a `_selection_changed`, que usa `read_text_file` para
   mostrarlo. El visor es de solo lectura.
3. Pulsar **Analyze Python File** ejecuta `analyze_python_file` en un `Worker`.
4. `read_text_file` limita tamaño y evita binarios típicos. `ast.parse` construye
   un árbol sintáctico sin importar ni ejecutar el archivo analizado.
5. El analizador devuelve `PythonAnalysis`; la GUI lo convierte en texto visible.
   Un `SyntaxError` queda representado en ese resultado.

Una pregunta útil: ¿por qué abrir un archivo no debería ejecutar su `import` o su
`main()`? Revisá la diferencia entre **leer bytes**, **parsear sintaxis** y
**ejecutar código**.

## Recorrido B: una pregunta con IA

1. Seleccionar un `.py` habilita **Add selected file**. Agregarlo a la lista aún
   no hace red; tampoco cambia la lista al seleccionar otro archivo en el árbol.
2. `prepare_context` comprueba cada archivo y el presupuesto conjunto. Guarda una
   copia del texto de cada uno para la vista previa.
3. Cambiar la lista o la pregunta invalida esa copia. Pulsar **Send previewed
   files and question** usa los archivos revisados.
4. `AssistantService` obtiene `GEMINI_API_KEY` del proceso o de la variable de
   usuario de Windows y construye un `AIProvider`.
5. `OpenAICompatibleProvider` hace la solicitud HTTP en un `Worker` y devuelve
   `AIResponse` a la pestaña. No hay reintentos automáticos.

La URL y el modelo se guardan como preferencias no secretas. La clave no se
escribe en el repositorio ni en `QSettings`. El transporte concreto puede
sustituirse en el servicio; la GUI y el analizador AST no conocen el protocolo HTTP.

## Decisiones observables y sus límites

| Decisión | Problema que resuelve ahora | Límite que conviene recordar |
| --- | --- | --- |
| PySide6 | Ventana, árbol de archivos y señales para el trabajo de fondo | Empaquetar para Windows sigue pendiente |
| `ast` estándar | Símbolos Python sin instalar parsers ni ejecutar fuente | No analiza semántica ni otros lenguajes en profundidad |
| `QThreadPool` | Evita bloquear la ventana durante escaneo y HTTP | No implica cancelación automática de solicitudes |
| `src/` y `pip -e` | Importaciones claras y cambios locales visibles | Requiere instalar el paquete en el entorno elegido |
| `AIProvider` | Permite cambiar transporte sin editar la GUI | Hoy sólo hay una implementación real |
| Contexto explícito | Evita subir un repositorio entero por accidente | La estimación de tokens no es exacta |

Los límites actuales del prototipo AI son hasta tres archivos, 12.000 bytes de
fuente en conjunto, 1.000 caracteres
de pregunta, ~4.000 tokens de entrada estimados y 384 tokens de salida solicitados.
Son políticas del proyecto para una prueba pequeña; no describen una cuota gratis
garantizada por Google.

## Dónde mirar pruebas

[`test_python_analyzer.py`](../tests/test_python_analyzer.py) muestra estructura y
errores de sintaxis; [`test_project_explorer.py`](../tests/test_project_explorer.py)
verifica estadísticas y lectura; [`test_ai_context.py`](../tests/test_ai_context.py)
comprueba la lista y el presupuesto agregado; [`test_ai_panel.py`](../tests/test_ai_panel.py)
recorre la interfaz con un proveedor falso; [`test_ai_provider.py`](../tests/test_ai_provider.py)
simula HTTP; [`test_ai_service.py`](../tests/test_ai_service.py) sustituye el
proveedor. Leer una prueba es preguntar: «¿qué cambio la haría fallar?».
