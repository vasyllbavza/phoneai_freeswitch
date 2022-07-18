from django.db import router
from rest_framework.routers import SimpleRouter

from .views import ContactViewSet, PhonebookViewSet, NumberLookupView, NumberCheckView
from django.urls import path


router = SimpleRouter()
router.register("api/phonebooks", PhonebookViewSet)
router.register("api/contacts", ContactViewSet)

urlpatterns = [
    path('api/number/lookup/', NumberLookupView.as_view(), name='number_lookup'),
    path('api/number/check/', NumberCheckView.as_view(), name='number_check'),
]

urlpatterns += router.urls
