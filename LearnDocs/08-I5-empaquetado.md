# I5 — del código al programa portátil

Al ejecutar `python -m local_cp`, tu Python busca `local_cp` y carga PySide6.
Al ejecutar `LocalCP.exe` del ZIP, PyInstaller inicia una copia empaquetada de
Python y las bibliotecas necesarias. El mismo código de la app corre en ambos
casos, pero la forma de **entregarlo** cambia.

## Antes de probar, predecí

1. ¿Qué pasa si copiás solamente `LocalCP.exe` y dejás atrás `_internal/`?
2. ¿Necesita el usuario final ejecutar `pip install`? ¿Y quien construye el ZIP?
3. ¿Por qué un ZIP que inicia en tu PC no demuestra que funcione en otra PC?
4. ¿Qué garantiza una prueba offscreen y qué no puede mostrarte de la interfaz?

## Recorrido y ejercicio

Leé [`pyproject.toml`](../pyproject.toml): `PySide6` es una dependencia de la
aplicación; `pyinstaller` está en el grupo opcional `package`, porque sólo se
necesita para construir. Después leé [`build_windows.ps1`](../scripts/build_windows.ps1)
y [`smoke_portable.ps1`](../scripts/smoke_portable.ps1). El primero construye y
comprime; el segundo **extrae** en otra carpeta y comprueba el arranque.

Si tenés una `.venv` preparada:

```powershell
Set-Location C:\Bruze\localCP
.\.venv\Scripts\python.exe -m pip install -e ".[dev,package]"
.\scripts\build_windows.ps1 -Python ".\.venv\Scripts\python.exe"
```

Si el paquete ya existe, consultá la [guía de empaquetado](../docs/packaging.md)
antes de reconstruir. No hace falta pedir una clave de IA: el smoke test sólo
crea la ventana y analiza una clase Python ficticia. El `PATH` restringido de
ese proceso permite detectar dependencias accidentales del Python instalado,
pero no equivale a una segunda máquina limpia.

Extraé el ZIP y usá la interfaz de forma manual. En tu bitácora, anotá qué
archivo abriste, si el análisis funcionó y si hubo alguna advertencia de Windows.
Compará esa evidencia con la prueba automática: **inicio técnico** y **uso
visual** son observaciones distintas.
