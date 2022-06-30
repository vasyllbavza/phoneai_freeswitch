import logging

from django.conf import settings
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
from rest_framework.views import APIView
from rest_framework import status
from .models import Phonebook, Contacts

from .serializers import (
    PhonebookSerializer,
    PhonebookCreateSerializer,
    PhonebookUpdateSerializer,
    ContactsSerializer,
    ContactsCreateSerializer,
    ContactsUpdateSerializer,
)
logger = logging.getLogger(__name__)


class PhonebookViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    queryset = Phonebook.objects.none()
    serializer_class = PhonebookSerializer
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
        return Phonebook.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PhonebookSerializer(instance)
        logger.info(f"PHI: User (id: {request.user.id}) accessed phonebook (id: {instance.id}).")
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "create":
            return PhonebookCreateSerializer
        if self.action in ["partial_update", "update"]:
            return PhonebookUpdateSerializer
        return super().get_serializer_class()


class ContactFilter(FilterSet):
    class Meta:
        model = Contacts
        fields = []

    phonebook = CharFilter(field_name="phonebook_id", label="Phonebook ID", method="filter_phonebook_id")

    def filter_phonebook_id(self, queryset, name, value):
        if value.isnumeric():
            return queryset.filter(phonebook_id=value)

        return queryset.all()


class ContactViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    queryset = Contacts.objects.none()
    serializer_class = ContactsSerializer
    search_fields = [
    ]
    filterset_class = ContactFilter
    ordering_fields = [
        "id",
    ]

    # MARK: - Overrides

    def get_permissions(self):
        if self.action in ["destroy", "list", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = Contacts.objects.all()
        phonebook_id = self.request.query_params.get('phonebook')
        if phonebook_id is not None:
            queryset = queryset.filter(phonebook_id=phonebook_id)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ContactsSerializer(instance)
        logger.info(f"PHI: User (id: {request.user.id}) accessed contact (id: {instance.id}).")
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "create":
            return ContactsCreateSerializer
        if self.action in ["partial_update", "update"]:
            return ContactsUpdateSerializer
        return super().get_serializer_class()


class NumberLookupView(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get(self, request, format=None):

        import plivo
        number = request.query_params.get('number', '')
        client = plivo.RestClient(settings.PLIVO_AUTH_ID, settings.PLIVO_AUTH_TOKEN)
        response = client.lookup.get(number)
        number_type = response['carrier']['type']
        number_carrier = response['carrier']['name']

        content = {}
        content["status"] = "success"
        content["type"] = number_type
        content["carrier"] = number_carrier
        if number_type == "voip":
            content["status"] = "fail"
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        if number_carrier == "AT&T":
            return Response(content, status=status.HTTP_200_OK)
        if number_carrier == "Verizon Wireless":
            return Response(content, status=status.HTTP_200_OK)
        if number_carrier == "T-Mobile US":
            return Response(content, status=status.HTTP_200_OK)

        content["status"] = "fail"
        return Response(content, status=status.HTTP_404_NOT_FOUND)
