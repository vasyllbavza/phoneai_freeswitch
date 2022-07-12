from django.db import router
from rest_framework.routers import SimpleRouter

from .views import CdrViewSet, ExtensionViewSet, DidNumberViewSet, BridgeCallViewSet

router = SimpleRouter()
router.register("api/cdrs", CdrViewSet)
router.register("api/extensions", ExtensionViewSet)
router.register("api/did_numbers", DidNumberViewSet)
router.register("api/bridge_calls", BridgeCallViewSet)

urlpatterns = [
    # path('api/extensions/', ExtensionsView.as_view(), name='extensions'),
]

urlpatterns += router.urls
