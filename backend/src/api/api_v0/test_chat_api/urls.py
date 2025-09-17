from rest_framework.routers import DefaultRouter
from .views import ChatViewSet

router = DefaultRouter()
router.register(
    r"test_chat_api",
    ChatViewSet,
    basename="test-chat-api",
)

urlpatterns = router.urls
