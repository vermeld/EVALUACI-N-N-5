# Plato Listo

Aplicación de ejemplo desarrollada con Kivy para la toma y recepción de pedidos en entornos gastronómicos pequeños.

**Resumen:**
Plato Listo permite a un mesero enviar pedidos desde una interfaz sencilla y al chef visualizarlos en otra pantalla. Además, el proyecto incluye una implementación básica de métricas que registra interacciones y duración de la sesión en un fichero `metrics.log`.

**Contenido de esta documentación:** instalación, ejecución, descripción de métricas, estructura del proyecto, ejemplos de uso y resolución de problemas.

## Requisitos
- **Python 3.8+** instalado.
- En Windows usar PowerShell (los comandos más abajo están listos para PowerShell v5.1).

## Instalación (PowerShell)
1. Crear y activar un entorno virtual (opcional pero recomendado):

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

2. Instalar Kivy (recomendado usar la variante base):

```powershell
# Instala Kivy (intenta con la opción base)
python -m pip install --upgrade pip
python -m pip install "kivy[base]" kivy_examples
```

Nota: en Windows la instalación de Kivy puede requerir ruedas precompiladas o dependencias adicionales (media/audio). Si la instalación por `pip` falla, consulta la guía oficial de Kivy: https://kivy.org.

## Ejecutar la aplicación

```powershell
# Desde la carpeta del proyecto
python .\main.py
```

## Estructura del proyecto
- `main.py`: lógica principal (pantallas Kivy, registro de métricas).  
- `main.kv`: definición de la interfaz (layouts y bindings).  
- `metrics.log`: archivo generado en tiempo de ejecución donde se almacenan métricas (una entrada JSON por línea).  
- `assets/`: recursos gráficos (imágenes, iconos) — vacío actualmente.

## Métricas implementadas

El proyecto ya registra las siguientes métricas y las guarda en `metrics.log` como líneas JSON:

- **Inicio App**: evento `Métrica 1: Inicio App` en `on_start()` con marca de tiempo.  
- **Duración Sesión**: evento `Métrica 1: Duración Sesión` en `on_stop()` con `start_ts`, `end_ts` y `duration_seconds`.  
- **Interacciones UI**: `Métrica 1: Botón Mesero` y `Métrica 1: Botón Chef` cuando se pulsa cada botón del menú (definido en `main.kv`).  
- **Enviar Pedido**: `Métrica 1: Enviar Pedido` con detalles `mesa` y `pedido` desde `MeseroScreen.enviar_pedido()`.

Formato (ejemplo de línea en `metrics.log`):

```json
{"timestamp":"2025-12-04T00:58:17.111859Z","event":"Métrica 1: Inicio App","details":{"ts":"2025-12-04T00:58:17.111859Z"}}
```

Las métricas se escriben usando el módulo estándar `logging` (un `FileHandler` apunta a `metrics.log`) y se generan mediante la función central `record_event(name, details=None)` en `main.py`.

## Fragmentos clave (cómo funciona)

- Logger y persistencia (en `main.py`): se configura `logging.getLogger('plato_listo_metrics')` con un `FileHandler` que escribe mensajes (JSON) en `metrics.log`.  
- `record_event(name, details)`: arma un diccionario `{'timestamp','event','details'}` y lo serializa con `json.dumps(...)`; luego hace `metrics_logger.info(msg)`.  
- Integración Kivy: en `main.kv` los botones llaman `app.record_event(...)` desde `on_press`, y `on_start`/`on_stop` gestionan el tiempo de sesión.

## Cómo añadir nuevas métricas

1. En el punto donde quieras registrar el evento (por ejemplo, dentro de un método de pantalla o dentro de un callback en KV) llama:

```python
App.get_running_app().record_event('Nombre Evento', {'clave':'valor'})
```

2. Para eventos de UI desde KV:

```kv
Button:
	on_press: app.record_event('MiEvento'); root.manager.current = 'otra_pantalla'
```

3. Si necesitas enviar métricas a un servidor en lugar de un archivo, reemplaza el `FileHandler` por un handler personalizado o añade un sender que procese la cola de métricas en background.

## Privacidad y datos registrados
- Actualmente se guardan datos mínimos: marcas de tiempo, identificadores de eventos y, en el caso de `Enviar Pedido`, el texto del pedido y la mesa.  
- Si vas a distribuir la app, considera anonimizar o evitar registrar información personal o sensible de clientes.

## Pruebas y comprobaciones rápidas

- Ver las últimas métricas en PowerShell:
```powershell
Get-Content .\metrics.log -Tail 50
```
- Si al ejecutar aparece `ModuleNotFoundError: No module named 'kivy'`, instala Kivy como se indicó arriba o activa el entorno virtual correcto.

## Troubleshooting (problemas comunes)
- Error `ModuleNotFoundError: No module named 'kivy'`: instala Kivy o activa el venv.  
- Si no se crean entradas en `metrics.log`: verifica permisos de escritura en la carpeta y que `main.py` pueda inicializar el logger (revisa la salida en consola para mensajes de error).  
- Si el UI se bloquea al escribir logs con alta frecuencia, considera cambiar a un `Queue` + thread worker o usar `RotatingFileHandler`.

## Extensiones recomendadas (futuro trabajo)
- Persistencia avanzada: `RotatingFileHandler` para rotar logs, o envío periódico a un servicio de analítica.  
- Métricas adicionales: vistas de pantalla (`screen_view`), confirmaciones por parte del chef, errores/excepciones, contadores por sesión.  
- Backend: endpoint REST para recibir métricas y agregarlas en un dashboard.

## Autor y contacto
Equipo de desarrollo - Proyecto académico

---
Documento generado automáticamente como documentación del código y de la implementación de métricas.
