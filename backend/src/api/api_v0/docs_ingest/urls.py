from rest_framework.routers import DefaultRouter

from api.api_v0.docs_ingest.views.document import DocumentViewSet
from api.api_v0.docs_ingest.views.search_chunk import SearchViewSet

router = DefaultRouter()
router.register(r'document', DocumentViewSet, basename="document")
router.register(r'search', SearchViewSet, basename="search")

urlpatterns = [] + router.urls