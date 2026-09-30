import os
import multiprocessing
from pathlib import Path

# Directorio base del proyecto (/home/kike/proyectos/adrianmma)
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración del Socket UNIX
bind = os.getenv(
    "GUNICORN_BIND",
    "unix:/run/adrian/adrian.sock",
)

# Workers y rendimiento
workers = int(os.getenv('GUNICORN_WORKERS', 3))
worker_class = "sync"
timeout = 120
graceful_timeout = 30
keepalive = 5

# Permisos para el socket Unix: 0o000 otorga 0666, garantizando que Nginx (www-data)
# pueda comunicarse con el socket sin errores de 'Permission denied (13)'
umask = 0o000

# ==========================================
# SISTEMA DE LOGS DE GUNICORN
# ==========================================
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Registro de accesos (todas las peticiones HTTP entrantes)
accesslog = str(LOG_DIR / 'gunicorn_access.log')

# Registro de errores y eventos del proceso
errorlog = str(LOG_DIR / 'gunicorn_error.log')

# Nivel de log: 'debug' en desarrollo para registrar cualquier evento
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "debug")

# Capturar también la salida estándar (stdout y stderr) de Django en el log de Gunicorn
capture_output = True

# Formato detallado de log de accesos: IP, timestamp, método, URI, status, tiempo de respuesta en microsegundos
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" (%(D)s µs)'
