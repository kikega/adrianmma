import os
import multiprocessing
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

bind = os.getenv(
    "GUNICORN_BIND",
    "unix:/run/kike/adrian.sock",
)

workers = int(
    os.getenv(
        "GUNICORN_WORKERS",
        multiprocessing.cpu_count(),
    )
)

worker_class = "sync"

timeout = 120
graceful_timeout = 30
keepalive = 5

loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

capture_output = True
