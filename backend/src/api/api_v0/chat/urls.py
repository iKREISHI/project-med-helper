from rest_framework.routers import DefaultRouter
from api.api_v0.chat.views.dialog import DialogViewSet


router = DefaultRouter(trailing_slash=False)
router.register(r"chat/dialogs", DialogViewSet, basename="dialog")

urlpatterns = router.urls
