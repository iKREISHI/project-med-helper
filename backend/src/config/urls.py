from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import ensure_csrf_cookie

urlpatterns = [
    path('admin/', admin.site.urls),

    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', ensure_csrf_cookie(SpectacularSwaggerView.as_view(url_name='schema')), name='swagger-ui'),
    path('api/schema/redoc/', ensure_csrf_cookie(SpectacularRedocView.as_view(url_name='schema')), name='redoc'),

    # api
    path('api/v0/', include('api.api_v0.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
