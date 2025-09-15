import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()
from apps.docs_ingest.tasks import pipeline_index_document


app = Celery('config', broker=settings.CELERY_BROKER_URL)

app.config_from_object(settings.CELERY)
app.conf.broker_connection_retry_on_startup = True
app.conf.beat_schedule = {
    "warm-embeddings-model-every-30min": {
        "task": "apps.docs_ingest.tasks.warm_embeddings_model",
        # Для локальной отладки оставим частый прогрев. В проде увеличить интервал.
        "schedule": crontab(minute="*/15"),
    },
    "enqueue-pending-docs-every-2min": {
        "task": "apps.docs_ingest.tasks.enqueue_pending_documents",
        "schedule": crontab(minute="*/2"),
        "args": (),
    },
}
app.autodiscover_tasks()