from django.db import router
from django.urls import path,include
from rest_framework.routers import SimpleRouter

from .views import ExtensionViewSet, DidNumberViewSet

router = SimpleRouter()
router.register("extensions", ExtensionViewSet)
router.register("did_numbers", DidNumberViewSet)

urlpatterns = [
    # path('api/extensions/', ExtensionsView.as_view(), name='extensions'),
]

urlpatterns += router.urls
