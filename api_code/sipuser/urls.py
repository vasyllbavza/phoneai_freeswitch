from django.db import router
from django.urls import path,include
from rest_framework.routers import SimpleRouter

from .views import ExtensionViewSet, DidNumberViewSet

router = SimpleRouter()
router.register("api/extensions", ExtensionViewSet)
router.register("api/did_numbers", DidNumberViewSet)

urlpatterns = [
    # path('api/extensions/', ExtensionsView.as_view(), name='extensions'),
]

urlpatterns += router.urls
