from django.db import router
from rest_framework.routers import SimpleRouter

from .views import ContactViewSet, PhonebookViewSet

router = SimpleRouter()
router.register("api/phonebooks", PhonebookViewSet)
router.register("api/contacts", ContactViewSet)

urlpatterns = [
    # path('api/extensions/', ExtensionsView.as_view(), name='extensions'),
]

urlpatterns += router.urls
