# Paquete portátil de Windows (I5)

Local CP usa [PyInstaller en modo *onedir*](https://pyinstaller.org/en/stable/operating-mode.html):
se distribuye la carpeta completa con el ejecutable, un intérprete Python
embebido y sus dependencias. El usuario final no tiene que instalar Python.
No es un instalador: no crea accesos directos, no se registra en Windows y no
actualiza la aplicación automáticamente.

## Construir en Windows 11 x64

Desde `C:\Bruze\localCP`, con el entorno virtual creado como explica el
[arranque de Python](../LearnDocs/01-python-arranque.md):

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,package]"
.\scripts\build_windows.ps1 -Python ".\.venv\Scripts\python.exe"
```

El script construye `dist\LocalCP\`, comprime esa carpeta en
`dist\LocalCP-windows-x64.zip` y ejecuta la prueba portátil. Si ya existen la
carpeta o el ZIP, se detiene para no sobreescribirlos. Guardá o borrá **sólo**
esos dos artefactos generados antes de repetir el build. `build/` y `dist/` no
se versionan. El nombre `x64` presupone que el build se realiza con Python x64.
PyInstaller empaqueta la versión de Python y dependencias **activas**; no compila
para otras plataformas ni arquitecturas.

El script usa las opciones `--onedir` y `--windowed` de
[PyInstaller](https://www.pyinstaller.org/en/stable/usage.html). Por ahora no hay
lockfile ni firma de código: una reconstrucción futura puede obtener otras
versiones compatibles, y Windows puede mostrar una advertencia al abrir un
ejecutable sin firma.
Durante el build, el script limita temporalmente `PATH` al Python elegido y a
Windows para evitar incluir DLL de otras herramientas instaladas en la PC.

## Verificar y usar

La prueba automática de `scripts/smoke_portable.ps1` extrae el ZIP en una carpeta
temporal nueva, ejecuta `LocalCP.exe --smoke-test` con Qt offscreen y sin Python
en el `PATH` de ese proceso, verifica el código de salida y elimina **esa**
carpeta temporal. El modo de prueba crea la ventana y ejecuta un análisis AST
pequeño; no usa la API de IA. También se puede repetir con:

```powershell
.\scripts\smoke_portable.ps1 -Archive ".\dist\LocalCP-windows-x64.zip"
```

Para la revisión manual: extraé el ZIP completo en otra carpeta, ejecutá
`LocalCP\LocalCP.exe`, abrí un proyecto pequeño, elegí un `.py` y pulsá
**Analyze Python File**. Confirmá que la pestaña AI puede abrirse aunque no
haya clave; no pulses Send si no querés hacer una solicitud externa. Para una
prueba más fuerte, repetí estos pasos en otra PC Windows 11 sin Python instalado.

El empaquetado no incorpora `GEMINI_API_KEY`, URL ni clave en los archivos.
La aplicación sigue leyendo la variable de usuario de Windows en tiempo de
ejecución, y el envío de fuente sigue requiriendo la acción explícita del usuario.
