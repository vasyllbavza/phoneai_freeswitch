"""phoneai_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api-auth/', include('rest_framework.urls'))
# ]

from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from api.views import (
    HelloView,
    MakeCallView,
    ScanCallView,
    ShowCallMenu,
    PhonenumberView,
    MakeCallSubMenuView,
    SendSMSView,
    SMSDLRView,
)
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.staticfiles.urls import static


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# from views import FreeswitchStatus

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('status/'), FreeswitchStatus.as_view()),
    path('api/hello/', HelloView.as_view(), name='hello'),
    path('api/phonenumber/',PhonenumberView.as_view()),
    path('api/makecall/',MakeCallView.as_view()),
    path('api/makecall_submenu/',MakeCallSubMenuView.as_view()),
    path('api/scan/',ScanCallView.as_view()),
    path('api/callmenu/',ShowCallMenu.as_view()),
    path('api/sendsms/',SendSMSView.as_view()),
    path('api/sms/callback/',SMSDLRView.as_view()),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)