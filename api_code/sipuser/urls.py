from django.urls import path,include
from .views import ExtensionsView

urlpatterns = [
    path('api/extensions/', ExtensionsView.as_view(), name='extensions'),
]
