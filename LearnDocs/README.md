# LearnDocs — aprender reconstruyendo Local CP

Esta carpeta es un cuaderno de aprendizaje. [docs](../docs/SPEC.md) describe el
producto y sus decisiones vigentes; acá intentamos explicar **cómo** funciona el
código que ya existe y practicar Python con experimentos pequeños. No hace falta
terminar un curso de Python antes de tocar la aplicación.

## Primer recorrido

| Orden | Lectura | Pregunta que responde |
| --- | --- | --- |
| 0 | [Arranque de Python y entorno](01-python-arranque.md) | ¿Qué Python estoy ejecutando y dónde se instalaron las dependencias? |
| 1 | [Mapa del código y decisiones](02-recorrido-y-decisiones.md) | ¿Qué ocurre desde `python -m local_cp` hasta ver un resultado? |
| 2 | [Ejercicios de la primera ronda](03-ejercicios.md) | ¿Puedo predecir y comprobar el comportamiento de una pieza? |
| 3 | [Bitácora y glosario](04-bitacora.md) | ¿Qué entendí, con qué evidencia y qué sigue abierto? |
| 4 | [Hoja de ruta](05-hoja-de-ruta.md) | ¿Qué estudiar ahora y qué dejar para después? |
| I3 | [Laboratorio: varios archivos](06-I3-contexto-multiple.md) | ¿Cómo se conserva el alcance explícito al ampliar una solicitud? |
| I4 | [Laboratorio: aviso de secretos](07-I4-aviso-secretos.md) | ¿Qué puede detectar una heurística local y qué decisión conserva el usuario? |
| I5 | [Laboratorio: paquete portátil](08-I5-empaquetado.md) | ¿Qué diferencia hay entre ejecutar el código y distribuir una aplicación? |

## Método

Antes de ejecutar, escribí qué esperás que pase. Ejecutá una sola variante,
observá el resultado y explicá la diferencia. Si modificás código, corré la prueba
relevante y mirá `git diff`; no hace falta cambiar varias capas a la vez. La
[bitácora](04-bitacora.md) distingue pruebas técnicas ya hechas de ejercicios que
todavía no realizaste vos.

El primer recorrido recomendado es **entorno → análisis local → GUI → AI optativa**.
Los ejercicios iniciales y el laboratorio I3 pueden hacerse con un proveedor
simulado, sin clave ni solicitudes externas.

Esta carpeta queda visible para Git por ahora. Si más adelante querés guardarla
sólo localmente, habrá que decidir si conservar una copia versionada o quitarla del
índice antes de agregarla a `.gitignore`; ignorar archivos ya versionados no los
desversiona.
