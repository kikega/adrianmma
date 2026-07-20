import os
import multiprocessing

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

bind = "unix:/run/adrian/adrian.sock"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
graceful_timeout = 30
keepalive = 5

user = "adrian"
group = "adrian"

errorlog = os.path.join(BASE_DIR, "logs", "gunicorn_error.log")
accesslog = os.path.join(BASE_DIR, "logs", "gunicorn_access.log")
loglevel = "info"

capture_output = True
daemon = False

raw_env = [
    "DJANGO_SETTINGS_MODULE=adrian.settings",
    "PYTHONPATH=" + BASE_DIR,
]
