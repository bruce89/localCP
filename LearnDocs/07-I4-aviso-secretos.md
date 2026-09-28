# I4 — avisos locales antes de Send

I4 agrega una ayuda para revisar el contexto preparado. Busca unos pocos patrones
evidentes de credenciales en la **pregunta** y en los archivos ya elegidos. Corre
en la máquina, durante **Prepare context**, antes de cualquier solicitud HTTP.
Si encuentra algo, la interfaz muestra ubicación, línea y motivo, y exige marcar
una casilla adicional para habilitar Send.

## Predecir antes de ejecutar

1. ¿Debería marcarse `API_KEY = os.environ.get("GEMINI_API_KEY")`? Ahí se lee una
   variable de entorno, pero el valor no aparece en el archivo.
2. ¿Debería marcarse `API_KEY = "sample-secret-value"`? ¿Qué parte del texto
   debería aparecer en el aviso y qué parte no?
3. Preparaste un archivo marcado y confirmaste; después cambiaste la pregunta.
   ¿Sigue habilitado Send?
4. El detector no encuentra nada. ¿Eso prueba que no hay secretos?

## Recorrido en el código

[`scan_request`](../src/local_cp/ai/secret_scan.py) recibe la pregunta y un
`CodeContext` ya preparado. Recorre líneas y devuelve `SecretFinding` con
`location`, `line` y `reason`. No devuelve la coincidencia ni el texto de la
línea. Sus patrones cubren encabezados de clave privada, algunas formas de clave
conocidas y asignaciones de literales a nombres como `api_key`, `token` o
`password`.

[`AIPanel._prepare`](../src/local_cp/gui/ai_panel.py) ejecuta ese escaneo sobre
la misma copia que se verá en la vista previa. Si hay hallazgos, `_update_send_button`
requiere que la casilla esté marcada. `_invalidate_preview` borra tanto los
hallazgos como la confirmación cuando cambian la pregunta o la lista de archivos.
La protección también está en `_send`: si falta la confirmación, no inicia el
trabajo de red aunque alguien llamara al método directamente.

## Laboratorio sin clave ni red

```powershell
Set-Location C:\Bruze\localCP
.\.venv\Scripts\python.exe -m pytest tests/test_secret_scan.py tests/test_ai_panel.py -q
```

Leé [los casos del detector](../tests/test_secret_scan.py) y
[el caso de la interfaz](../tests/test_ai_panel.py). El primero demuestra que el
resultado no incluye el valor ficticio. El segundo demuestra que no se llama al
proveedor simulado hasta marcar la confirmación.

## Límite deliberado

Una expresión regular ve formas de texto, no entiende si un valor está activo,
si un ejemplo de prueba es ficticio o si un secreto usa un formato desconocido.
Por eso puede advertir de más o de menos. El aviso es una oportunidad de revisar,
no una autorización automática para compartir ni una certificación de seguridad.

Para la [bitácora](04-bitacora.md): elegí un falso positivo plausible y un falso
negativo plausible. Proponé una mejora pequeña y una prueba que mostraría su
beneficio sin hacer que el aviso exponga el propio valor que intenta proteger.
