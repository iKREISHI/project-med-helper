from django.urls import include, path

urlpatterns = [
    path('', include('api.api_v0.users.urls')),
    path('', include('api.api_v0.docs_ingest.urls')),
    path('', include('api.api_v0.test_chat_api.urls')),
    path('', include('api.api_v0.semd_templates.urls')),
    path('', include('api.api_v0.chat.urls')),
]