import os
import platform
from celery.schedules import crontab
from .locale import TIME_ZONE

# Брокер/резалты (важно!)
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

CELERY = {
    'broker_url': CELERY_BROKER_URL,
    'worker_hijack_root_logger': False,
    'timezone': TIME_ZONE,
    # Внимание: здесь должен быть словарь расписания, а не строка.
    # Ранее здесь по ошибке указывался путь к шедулеру, что ломало celery beat.
    'beat_schedule': None,  # временно заполним ниже корректным значением
}

# На macOS (Darwin) использование пулла по умолчанию (prefork) может приводить к краху
# при инициализации библиотек на базе Objective‑C/Metal (PyTorch/MPS):
# "+[MPSGraphObject initialize] ... when fork() was called ... Crashing instead".
# Чтобы исключить fork(), переключаем пул воркеров на потоки.
if platform.system() == "Darwin":
    CELERY['worker_pool'] = 'threads'  # альтернатива: 'solo' для полной однопроцессности
