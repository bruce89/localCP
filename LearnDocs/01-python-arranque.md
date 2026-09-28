# Python desde cero, usando Local CP

Esta guía asume **PowerShell en Windows 11** y el proyecto en `C:\Bruze\localCP`.
El objetivo no es memorizar comandos: es saber qué intérprete ejecuta la app y
dónde encuentra sus bibliotecas.

## Si ya preparaste el proyecto: tres pasos en cada consola nueva

```powershell
Set-Location C:\Bruze\localCP
.\.venv\Scripts\Activate.ps1
python -m local_cp
```

El primero te ubica en el proyecto; el segundo activa **para esta consola** el
Python de `.venv`; el tercero abre Local CP. Cerrar la consola termina la
activación, pero no borra `.venv` ni los paquetes instalados. Por eso no hace
falta repetir `py -m venv` ni `pip install` cada vez. Para salir del entorno sin
cerrar la consola, usá `deactivate`.

## 1. Ubicarse y comprobar Python

```powershell
Set-Location C:\Bruze\localCP
py --version
Get-Location
```

`py` es el lanzador de Python de Windows. `Get-Location` muestra el directorio
actual: varios comandos posteriores usan rutas relativas a este proyecto. Local CP
declara Python **3.11 o superior** en [`pyproject.toml`](../pyproject.toml).

## 2. Crear el entorno virtual

```powershell
py -m venv .venv
```

Leé el comando de izquierda a derecha: `py` elige un intérprete, `-m venv` ejecuta
el módulo estándar `venv`, y `.venv` es la carpeta que se crea. Ahí quedan un
`python.exe`, `pip` y los paquetes que instales para este proyecto. El entorno no
contiene una copia de tu código fuente ni instala automáticamente las dependencias.

`.venv` es sólo un nombre habitual para esa carpeta. **`.env` suele ser un archivo
de variables de entorno**, no el comando para crear un entorno virtual. Local CP
ignora `.venv/` en Git; no guardes claves en un `.env` del repositorio.

Podés activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
```

El resultado debería terminar en `C:\Bruze\localCP\.venv\Scripts\python.exe`.
Activar ajusta el `PATH` de **esta sesión de PowerShell** para que `python` y `pip`
apunten al entorno. No es obligatorio; podés llamar al ejecutable directamente,
lo cual además evita problemas con la política de ejecución de scripts:

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
```

Si `Activate.ps1` está bloqueado, usá esta segunda forma. Al terminar una sesión
activada, `deactivate` restaura el `PATH`; cerrar la terminal también termina esa
activación. No borra la carpeta `.venv`.

## 3. Instalar el proyecto y sus herramientas

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

`-m pip` usa el `pip` del **mismo intérprete** que aparece antes de `-m`; así no
instalás PySide6 en otro Python por accidente. `-e` instala Local CP en modo
editable: el entorno apunta al código de `src/local_cp`, y los cambios en esos
archivos se ven sin reinstalar el paquete. `.[dev]` pide el proyecto actual (`.`)
y el grupo opcional `dev` (`pytest`, `pytest-cov` y `ruff`). Las dependencias están
declaradas en [`pyproject.toml`](../pyproject.toml).

Una declaración como `PySide6>=6.8,<7` permite varias versiones; no fija por sí
sola una instalación idéntica en todas las máquinas. Este proyecto aún no tiene
un archivo de versiones resueltas (*lockfile*).

Comprobá de dónde se importa el paquete:

```powershell
.\.venv\Scripts\python.exe -c "import sys, local_cp; print(sys.executable); print(local_cp.__file__)"
```

Deberías ver primero el Python de `.venv` y después un archivo bajo
`C:\Bruze\localCP\src\local_cp`.

## 4. Ejecutar y verificar

```powershell
.\.venv\Scripts\python.exe -m local_cp
```

`-m local_cp` busca el paquete y ejecuta [`__main__.py`](../src/local_cp/__main__.py),
que llama a [`app.py`](../src/local_cp/app.py). La aplicación abre una ventana Qt;
cerrarla devuelve el control a PowerShell.

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

Las pruebas verifican comportamiento; Ruff revisa reglas de estilo y errores
frecuentes. Ninguno de estos comandos necesita la clave de Gemini. Si algo falla,
anotá **el comando, el intérprete, el primer error completo y tu hipótesis** antes
de cambiar código.

## Cinco conceptos para llevarte de esta sesión

| Concepto | En este proyecto |
| --- | --- |
| Intérprete | El `python.exe` que ejecuta cada comando |
| Entorno virtual | `.venv`, instalación de dependencias aislada del Python general |
| Paquete | `local_cp`, carpeta importable bajo `src` |
| Módulo | Un archivo como `analysis/python_analyzer.py` |
| Dependencia | Biblioteca externa declarada en `pyproject.toml`, como PySide6 |

Una anotación como `path: Path` documenta el tipo esperado y ayuda a herramientas,
pero Python no convierte ni valida automáticamente todos los valores al ejecutar.
Un `dataclass` genera métodos útiles para datos estructurados; tampoco valida por
sí solo el JSON que llega de una API. Lo veremos sobre ejemplos reales en el
[recorrido del código](02-recorrido-y-decisiones.md).
