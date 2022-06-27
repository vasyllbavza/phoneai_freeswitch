import logging

from flowroutenumbersandmessaging.flowroutenumbersandmessaging_client import FlowroutenumbersandmessagingClient

from django.conf import settings
from django.shortcuts import render
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication
)
import logging

from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import (
    FilterSet,
    CharFilter,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Domain, Extension, FsCDR, FsUser, FsProvider, FsDidNumber
from contacts.models import Phonebook

from .serializers import (
    CdrSerializer,
    ExtensionCreateSerializer,
    ExtensionSerializer,
    ExtensionUpdateSerializer,
    ExtensionRetrieveSerializer,
    DidNUmberSerializer,
    DidNUmberCreateSerializer,
    DidNumberSearchSerializer,
)
logger = logging.getLogger(__name__)


class ExtensionFilter(FilterSet):
    class Meta:
        model = Extension
        fields = []

    user_id = CharFilter(field_name="user_id", label="USER ID", method="filter_user_id",)

    # MARK: - Methods

    def filter_user_id(self, queryset, name, value):
        if value.isnumeric():
            return queryset.filter(user_id=value)

        return queryset.filter(pbx__pbx_uuid=value)


class ExtensionViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    queryset = Extension.objects.none()
    serializer_class = ExtensionSerializer
    search_fields = [
    ]
    filterset_class = ExtensionFilter
    ordering_fields = [
        "id",
    ]

    # MARK: - Overrides

    def get_permissions(self):
        if self.action in ["destroy", "list", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        return Extension.objects.all()

    def perform_create(self, serializer):
        print(self.request.user)
        fsuser = FsUser.objects.get(user_id=self.request.user.id)
        data = serializer.save(user_id=fsuser.id)
        print(data)
        phonebook = Phonebook(name="PB%s" % str(data.id))
        ext = Extension.objects.get(pk=data.id)
        phonebook.extension = ext
        phonebook.save()

    def perform_destroy(self, instance):
        print(f"User (id: {self.request.user.id}) deleted extension (id: {instance.id}).")
        instance.delete()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ExtensionRetrieveSerializer(instance)
        logger.info(f"PHI: User (id: {request.user.id}) accessed extension (id: {instance.id}).")
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "create":
            return ExtensionCreateSerializer
        if self.action in ["partial_update", "update"]:
            return ExtensionUpdateSerializer
        return super().get_serializer_class()


class DidNumberViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    queryset = FsDidNumber.objects.none()
    serializer_class = DidNUmberSerializer
    search_fields = [
    ]
    # filterset_class = ExtensionFilter
    ordering_fields = [
        "id",
    ]

    # MARK: - Overrides

    def get_permissions(self):
        if self.action in ["destroy", "list", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        return FsDidNumber.objects.all()

    def perform_create(self, serializer):
        print(self.request.user)
        print(serializer.validated_data)
        provider = FsProvider.objects.first()
        if provider.name == "Flowroute":
            basic_auth_user_name = settings.FLOWROUTE_AUTH_USER
            basic_auth_password = settings.FLOWROUTE_AUTH_PASS
            client = FlowroutenumbersandmessagingClient(basic_auth_user_name, basic_auth_password)
            numbers_controller = client.numbers
            purchasable_number = serializer.validated_data["phonenumber"]
            try:
                result = numbers_controller.purchase_a_phone_number(purchasable_number)
                print(result)

                prirouteid = settings.FLOWROUTE_ROUTE
                request_body = '{ \
                    "data": { \
                        "type": "route", \
                        "id": "' + str(prirouteid) + '" \
                    } \
                }'
                routes_controller = client.routes
                print("---Update Primary Voice Route")
                result = routes_controller.update_primary_voice_route(purchasable_number, request_body)
                if result is None:
                    print("204: No Content")
                else:
                    print(result)
                domain = Domain.objects.first()
                serializer.save(provider=provider, domain=domain)
            except:
                logger.exception("error found in purchase")

        # fsuser = FsUser.objects.get(user_id=self.request.user.id)
        # serializer.save(user_id=fsuser.id)

    def perform_destroy(self, instance):
        print(f"User (id: {self.request.user.id}) deleted extension (id: {instance.id}).")
        instance.delete()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DidNUmberSerializer(instance)
        logger.info(f"PHI: User (id: {request.user.id}) accessed extension (id: {instance.id}).")
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "create":
            return DidNUmberCreateSerializer
        # if self.action in ["partial_update", "update"]:
        #     return ExtensionUpdateSerializer
        return super().get_serializer_class()

    @action(
        methods=["get"],
        permission_classes=[IsAuthenticated],
        serializer_class=DidNumberSearchSerializer,
        detail=False,
        url_path="search",
        url_name="search",
    )
    def search(self, request, pk=None):
        npa = self.request.query_params.get('npa')
        try:
            limit = self.request.query_params.get('limit')
            if not limit:
                limit = 10
        except:
            limit = 10

        number_list = []
        provider = FsProvider.objects.first()
        if provider.name == "Flowroute":
            basic_auth_user_name = settings.FLOWROUTE_AUTH_USER
            basic_auth_password = settings.FLOWROUTE_AUTH_PASS
            client = FlowroutenumbersandmessagingClient(basic_auth_user_name, basic_auth_password)
            numbers_controller = client.numbers
            try:
                starts_with = npa
                contains = None
                ends_with = None
                # limit = 10
                offset = None
                rate_center = None
                state = None
                result = numbers_controller.search_for_purchasable_phone_numbers(starts_with, contains, ends_with, limit, offset, rate_center, state)
                # print(result)

                for row in result["data"]:
                    print(row)
                    numberinfo = {}
                    numberinfo["number"] = row["id"]
                    # numberinfo["setup_cost"] = row["attributes"]["setup_cost"]
                    # numberinfo["number_type"] = row["attributes"]["number_type"]
                    numberinfo["monthly_cost"] = row["attributes"]["monthly_cost"]
                    # numberinfo["state"] = row["attributes"]["state"]
                    number_list.append(numberinfo)

                # print(number_list)
            except:
                logger.exception("Error found")

        return Response({"data": number_list})


class CdrViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    queryset = FsCDR.objects.none()
    serializer_class = CdrSerializer
    search_fields = [
    ]
    # filterset_class = ExtensionFilter
    ordering_fields = [
        "id",
    ]

    # MARK: - Overrides

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        return FsCDR.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CdrSerializer(instance)
        logger.info(f"PHI: User (id: {request.user.id}) accessed cdr (id: {instance.id}).")
        return Response(serializer.data)

    def get_serializer_class(self):
        return super().get_serializer_class()
