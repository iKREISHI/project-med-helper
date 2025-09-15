from django.urls import include, path

urlpatterns = [
    path('', include('api.api_v0.users.urls')),
    path('', include('api.api_v0.docs_ingest.urls'))
]