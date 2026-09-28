# Bitácora y glosario

Esta página es una **plantilla**. Las verificaciones técnicas registradas en el
[SPEC](../docs/SPEC.md) no significan que ya hayas realizado estos ejercicios.
Copiá una ficha por sesión o agregá secciones debajo; escribí resultados
observados, no resultados esperados como si hubieran ocurrido.

## Ficha de sesión

```text
Fecha / corte / commit:
Pregunta concreta:
Hipótesis antes de ejecutar:
Archivo o función que voy a mirar:
Comando o acción en la GUI:
Resultado observado:
Evidencia (salida, test, diff o captura):
Explicación de la diferencia:
Concepto de Python que quedó más claro:
Qué aún no puedo explicar:
Siguiente experimento pequeño:
```

## Mapa a completar sin mirar el recorrido

| Acción | Archivo y función | Entrada | Salida o error |
| --- | --- | --- | --- |
| `python -m local_cp` | Pendiente | Pendiente | Pendiente |
| Abrir proyecto | Pendiente | Pendiente | Pendiente |
| Seleccionar archivo | Pendiente | Pendiente | Pendiente |
| Analizar Python | Pendiente | Pendiente | Pendiente |
| Preparar contexto AI | Pendiente | Pendiente | Pendiente |
| Enviar pregunta | Pendiente | Pendiente | Pendiente |

Podés usar [el recorrido](02-recorrido-y-decisiones.md) para corregirlo después
de intentar completarlo de memoria.

## Glosario aplicado

| Término | Significado en Local CP |
| --- | --- |
| Intérprete | Programa que ejecuta código Python; elegir otro puede cambiar los paquetes disponibles |
| `venv` | Módulo que crea un entorno virtual |
| `.venv` | Carpeta local de ese entorno; el nombre es una convención |
| `.env` | Nombre habitual de un archivo de variables; no crea un entorno virtual |
| `pip` | Instalador de paquetes; usar `python -m pip` lo ata a un intérprete concreto |
| Paquete | Carpeta importable como `local_cp` |
| Módulo | Archivo Python importable como `local_cp.analysis.python_analyzer` |
| Entry point | Función o módulo por donde empieza la ejecución |
| `dataclass` | Clase de datos con métodos generados; no valida tipos por sí misma |
| Type hint | Anotación de tipo para lectores y herramientas; no impone todo en runtime |
| `ast` | Árbol de sintaxis de Python; permite inspeccionar sin ejecutar la fuente |
| Excepción | Señal de que una operación no pudo completar su contrato |
| `Protocol` | Contrato basado en los métodos que ofrece un objeto |
| `QThreadPool` | Ejecuta trabajo fuera del hilo de la ventana |
| Señal Qt | Mensaje que comunica resultado o error al hilo de la interfaz |
| Fixture/fake | Datos o componente controlado para probar sin depender de una API real |
| Contexto AI | Archivo y pregunta que la app prepara para un envío explícito |
| Token estimado | Aproximación de tamaño de entrada; puede diferir del conteo del proveedor |

## Preguntas para futuras rondas

1. ¿Dónde termina una preferencia no secreta y dónde empieza una credencial?
2. ¿Qué prueba fallaría si `prepare_context` incluyera un segundo archivo?
3. ¿Por qué `QThreadPool` mantiene fluida la ventana pero no cancela por sí solo HTTP?
4. ¿Qué cambia si mañana reemplazamos Gemini por otro proveedor compatible?
5. ¿Qué evidencia justificaría incorporar un parser de otro lenguaje?
