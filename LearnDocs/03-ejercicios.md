# Primera ronda de ejercicios

Cada ejercicio tiene una **predicción**, una **observación** y una **explicación**.
Hacé los primeros tres sin editar código. La bitácora está en
[04-bitacora.md](04-bitacora.md). Todos los comandos de esta página son locales:
no llaman al proveedor de IA.

Antes de empezar, prepará el entorno según [01-python-arranque.md](01-python-arranque.md).
En PowerShell:

```powershell
Set-Location C:\Bruze\localCP
```

## 1. ¿Qué Python ejecuta el proyecto?

**Predecí:** ¿qué ruta imprimirá cada comando? ¿Por qué una dependencia instalada
en `.venv` podría no estar disponible al llamar a otro `python`?

```powershell
py -c "import sys; print(sys.executable)"
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
.\.venv\Scripts\python.exe -c "import local_cp; print(local_cp.__file__)"
```

**Observá:** el segundo ejecutable debe vivir dentro de `.venv`. El paquete debe
apuntar a `src/local_cp` tras `pip install -e ".[dev]"`. Si el primer comando usa
otro ejecutable, eso no implica que esté mal: son instalaciones diferentes.

**Dominio:** explicar con tus palabras qué cambió al activar un entorno y qué no
cambió en los archivos del repositorio.

## 2. Una función que no ejecuta el código que lee

**Predecí:** ¿cuántos imports, funciones y clases encontrará el analizador en su
propio archivo? ¿Qué pasa si le pasás fuente con sintaxis inválida?

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from local_cp.analysis.python_analyzer import analyze_python_file; r = analyze_python_file(Path('src/local_cp/analysis/python_analyzer.py')); print('imports:', len(r.imports), 'funciones:', [f.name for f in r.functions], 'clases:', [c.name for c in r.classes])"
.\.venv\Scripts\python.exe -c "from local_cp.analysis.python_analyzer import analyze_python_source; r = analyze_python_source('def rota(:'); print(r.syntax_error)"
```

**Observá:** el segundo resultado es un error de sintaxis como **dato**, no una
excepción que cierre la aplicación. La función analiza el texto; no lo importa ni
lo ejecuta. Leé [`python_analyzer.py`](../src/local_cp/analysis/python_analyzer.py)
y encontrá el `try/except SyntaxError`.

**Dominio:** distinguir `ast.parse(source)` de `import` y de `exec(source)`.

## 3. Alcance de una solicitud AI, sin usar la red

**Predecí:** ¿qué ruta relativa y cuántos tokens estimados devolverá la preparación
de un archivo pequeño? ¿En qué punto se leería la clave?

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from local_cp.ai.context import prepare_context; root = Path.cwd(); c = prepare_context(root, [root / 'src/local_cp/analysis/models.py'], 'Explicá FunctionInfo'); print(c.files[0].relative_path, c.estimated_input_tokens)"
.\.venv\Scripts\python.exe -m pytest tests/test_ai_context.py tests/test_ai_service.py -q
```

**Observá:** `prepare_context` devuelve texto y metadatos localmente. La clave
sólo se resuelve más tarde en `AssistantService.ask`, después de un envío explícito
desde la GUI. No imprimas la clave como parte del experimento.

**Dominio:** señalar qué línea impide seleccionar un archivo fuera del proyecto y
qué línea impone el límite de tamaño.

La versión con varios archivos tiene un [laboratorio siguiente](06-I3-contexto-multiple.md).

## 4. Cambiar una regla pequeña (cuando quieras editar)

Propuesta: agregar una extensión a `LANGUAGE_BY_SUFFIX` en
[`explorer.py`](../src/local_cp/project/explorer.py) y un caso a
[`test_project_explorer.py`](../tests/test_project_explorer.py). Antes de editar,
decidí qué etiqueta debería aparecer. Después:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_project_explorer.py -q
.\.venv\Scripts\python.exe -m ruff check .
git diff
```

**Dominio:** explicar por qué el cambio afecta a la estadística del proyecto pero
no agrega análisis estructural para ese lenguaje. Si el ejercicio era temporal,
revertí sólo tus cambios de práctica después de revisar `git diff`; no borres
trabajo ajeno ni restaures todo el repositorio a ciegas.

## 5. Seguir una acción de la ventana

Abrí Local CP y un proyecto pequeño. Seleccioná un `.py`, pulsá **Analyze Python
File** y, en el código, seguí:

`_selection_changed` → `_analyze_selected` → `Worker.run` →
`analyze_python_file` → `_show_analysis`.

**Predecí:** ¿qué mensaje verías si el archivo tiene un error de sintaxis? ¿Qué
ocurriría con la ventana si el análisis corriera en el hilo principal? La
segunda pregunta es de razonamiento; no hace falta introducir una pausa artificial
ni romper la aplicación para responderla.

## Cierre

Elegí un ejercicio, registrá hipótesis, comando, resultado y explicación. Si
todo salió como esperabas, cambiá una sola condición; ahí suelen aparecer las
preguntas más útiles.
