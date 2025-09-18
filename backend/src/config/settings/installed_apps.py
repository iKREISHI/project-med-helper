INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Dependence
    'rest_framework',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'minio_storage',
    'django_celery_beat',
    'django_celery_results',

    # Apps
    'apps.users.apps.UsersConfig',
    'apps.docs_ingest.apps.DocsIngestConfig',
    'apps.llm.apps.LlmConfig',
    'apps.semd_templates.apps.SemdTemplatesConfig',

    # api
    'api.api_v0.apps.ApiV0Config',
]