# I3 — contexto de varios archivos, una sola solicitud

En I2 el contexto era un archivo. I3 permite elegir hasta **tres** `.py` del
proyecto, uno por uno. El total de fuente sigue limitado a **12 KB** y la
estimación de entrada a **4.000 tokens**. No se recorren carpetas para incluir
archivos automáticamente. Este laboratorio se puede hacer sin clave de API.

## Antes de abrir el código

Predecí estas cuatro situaciones:

1. Seleccionás `a.py` y luego `b.py` en el árbol sin pulsar **Add selected file**.
   ¿Cuántos archivos hay en la lista de contexto?
2. Agregás `a.py`, preparás la vista previa y después agregás `b.py`. ¿Sigue
   habilitado Send? ¿Por qué?
3. Dos archivos pesan 7 KB cada uno. ¿Qué debería ocurrir aunque cada archivo
   por separado sea aceptable?
4. Preparás dos archivos, cambias de selección en el árbol sin tocar la lista ni
   la pregunta. ¿Es el mismo contexto preparado?

## Recorrido real

1. [`MainWindow._selection_changed`](../src/local_cp/gui/main_window.py) informa
   a `AIPanel` cuál archivo está seleccionado; no lo agrega.
2. [`AIPanel._add_selected`](../src/local_cp/gui/ai_panel.py) incorpora el archivo
   a una lista visible. `_remove_highlighted` lo quita. Ambas operaciones
   invalidan la vista previa.
3. [`prepare_context`](../src/local_cp/ai/context.py) vuelve a comprobar cada ruta,
   rechaza duplicados y calcula el límite **conjunto**. El orden de la lista se
   conserva en `CodeContext.files`.
4. `build_user_message` arma el texto que ves en la vista previa. El
   [transporte HTTP](../src/local_cp/ai/openai_compatible.py) llama a la misma
   función para construir el mensaje enviado. Así no hay dos formatos que puedan
   divergir accidentalmente.
5. Send entrega una copia preparada a `AssistantService`. Cambios posteriores en
   disco no alteran esa solicitud ya preparada; hay que preparar otra vista previa
   para incluir la nueva versión de un archivo.

## Experimento local, sin red

Desde PowerShell, con el entorno instalado:

```powershell
Set-Location C:\Bruze\localCP
.\.venv\Scripts\python.exe -c "from pathlib import Path; from local_cp.ai.context import prepare_context, build_user_message; root = Path.cwd(); files = [root / 'src/local_cp/analysis/models.py', root / 'src/local_cp/analysis/python_analyzer.py']; c = prepare_context(root, files, 'Compará las responsabilidades'); print([f.relative_path for f in c.files]); print(c.estimated_input_tokens); print(build_user_message('Compará las responsabilidades', c.files)[:120])"
.\.venv\Scripts\python.exe -m pytest tests/test_ai_context.py tests/test_ai_panel.py tests/test_ai_provider.py -q
```

La primera línea del resultado debe mostrar **dos rutas**, en el mismo orden que
la lista de entrada. El fragmento de mensaje empieza con la pregunta y la primera
ruta. La segunda orden prueba límites, vista previa/Send con un proveedor falso y
el contenido HTTP construido, sin efectuar una llamada real.

## Preguntas para la bitácora

- ¿Por qué el límite de 12 KB se aplica al conjunto y no a cada archivo?
- ¿Qué diferencia hay entre la selección actual del árbol y la lista preparada?
- ¿Qué riesgo habría si la vista previa mostrara una versión del texto y el
  transporte leyera otra del disco justo antes de enviar?
- ¿En qué capa cambiarías el máximo de archivos? ¿Qué pruebas deberían fallar si
  olvidaras actualizar el comportamiento de la interfaz?

Registrá tu predicción y resultado en [la bitácora](04-bitacora.md). Si probás
Send con una API real, revisá todo el texto de la vista previa y anotá el uso
informado por el proveedor; los límites elegidos por Local CP no garantizan la
cuota de una cuenta externa.
