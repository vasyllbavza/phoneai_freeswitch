import logging
from datetime import datetime, timedelta
from django.utils import timezone
import requests
import plivo

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
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from .models import Phonebook, Contacts, InboundNumbers
from sipuser.models import FsCDR

from .serializers import (
    PhonebookSerializer,
    PhonebookCreateSerializer,
    PhonebookUpdateSerializer,
    ContactsSerializer,
    ContactsCreateSerializer,
    ContactsUpdateSerializer,
    InboundNumbersSerializer,
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
        number_carrier = number_carrier.lower()

        content = {}
        content["status"] = "success"
        content["type"] = number_type
        content["carrier"] = number_carrier
        if number_type == "voip":
            content["status"] = "fail"
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        if number_carrier.find("at&t") > -1:
            return Response(content, status=status.HTTP_200_OK)
        if number_carrier.find("t-mobile") > -1:
            return Response(content, status=status.HTTP_200_OK)
        if number_carrier.find("verizon") > -1:
            return Response(content, status=status.HTTP_200_OK)
        if number_carrier.find("xfinity") > -1:
            return Response(content, status=status.HTTP_200_OK)
        if number_carrier.find("spectrum") > -1:
            return Response(content, status=status.HTTP_200_OK)
        if number_carrier.find("us cellular") > -1:
            return Response(content, status=status.HTTP_200_OK)

        # if number_carrier.find("Visible") > -1:
        #     return Response(content, status=status.HTTP_200_OK)
        # if number_carrier.find("Mint") > -1:
        #     return Response(content, status=status.HTTP_200_OK)
        # if number_carrier.find("Red Pocket") > -1:
        #     return Response(content, status=status.HTTP_200_OK)

        content["status"] = "fail"
        return Response(content, status=status.HTTP_404_NOT_FOUND)


def carrier_valid(carrier_type, carrier_name):
    if carrier_type == "voip":
        return False

    if carrier_name.find("at&t") > -1:
        return True
    if carrier_name.find("t-mobile") > -1:
        return True
    if carrier_name.find("verizon") > -1:
        return True
    if carrier_name.find("xfinity") > -1:
        return True
    if carrier_name.find("spectrum") > -1:
        return True
    if carrier_name.find("us cellular") > -1:
        return True

    return False


class NumberCheckView(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get(self, request, format=None):
        content = {}
        content["status"] = "fail"

        number = request.query_params.get('number', '')
        stir_shaken = request.query_params.get('stir_shaken', '0')

        number = number.lower()
        if number == "anonymous" or number == "unavailable":
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        number = number[-10:]

        carrier_lookup = False
        spam_lookup = False

        inbound_number = InboundNumbers.objects.filter(phonenumber=number).first()
        if not inbound_number:
            inbound_number = InboundNumbers(
                phonenumber=number
            )
            carrier_lookup = True
            spam_lookup = True
        else:
            if inbound_number.carrier_expired < timezone.now():
                carrier_lookup = True

            if inbound_number.spam_expired < timezone.now():
                spam_lookup = True

        if carrier_lookup:
            try:
                client = plivo.RestClient(settings.PLIVO_AUTH_ID, settings.PLIVO_AUTH_TOKEN)
                response = client.lookup.get("1%s" % number)
                number_type = response['carrier']['type']
                number_carrier = response['carrier']['name']
                number_carrier = number_carrier.lower()
                inbound_number.caller_type = number_type
                inbound_number.caller_carrier = number_carrier
                inbound_number.carrier_expired = datetime.now() + timedelta(days=365)
            except:
                logger.exception("plivo lookup error")
                inbound_number.carrier_expired = datetime.now() + timedelta(hours=-1)
                inbound_number.caller_type = ""
                inbound_number.caller_carrier = ""

        if spam_lookup:
            try:
                spam_url = "%s/%s" % (settings.SPAM_URL, number)
                sheaders = {"DataApiSid": settings.SPAM_API_SID, "DataApiKey": settings.SPAM_API_KEY}
                sheaders["User-Agent"] = "PhoneAI v1.0"
                resp = requests.get(spam_url, headers=sheaders)
                if resp.status_code == 200:
                    resp_data = resp.json()
                    if resp_data["responseMessage"] == "Successful":
                        lookup = resp_data["lookup"]
                        if lookup:
                            try:
                                inbound_number.spam_risk = lookup["spamRisk"]["level"]
                                if inbound_number.spam_risk == 0:
                                    inbound_number.spam_expired = datetime.now() + timedelta(days=30)
                                else:
                                    inbound_number.spam_expired = datetime.now() + timedelta(days=365)
                            except:
                                pass
                            try:
                                inbound_number.fraud_risk = lookup["fraudRisk"]["level"]
                            except:
                                pass
                            try:
                                inbound_number.unlawful_risk = lookup["unlawfulRisk"]["level"]
                            except:
                                pass
            except:
                logger.exception("spam lookup error")
        inbound_number.save()

        serializer = InboundNumbersSerializer(inbound_number)

        content["caller_in_contact"] = 0
        content["data"] = serializer.data

        require_catcha = 0

        # invalid carier
        if not carrier_valid(inbound_number.caller_type, inbound_number.caller_carrier):
            require_catcha = 1

        # spammer
        if inbound_number.spam_risk > 0:
            require_catcha = 1

        # check call history

        # stire-shaken
        if stir_shaken == 0:
            cdr = FsCDR.objects.filter(is_verified=True).first()
            if cdr:
                return Response(content, status=status.HTTP_404_NOT_FOUND)

        # user's phonebook
        contact = Contacts.objects.filter(phonenumber=number).filter(~Q(source="captcha")).first()
        if contact:
            content["status"] = "success"
            content["caller_in_contact"] = 1
            return Response(content, status=status.HTTP_200_OK)

        if require_catcha == 1:
            cdrs = FsCDR.objects.filter(call_from=number).order_by('-created_at')[:5]
            for cdr in cdrs:
                if cdr.captcha_verified:
                    require_catcha = 0
                    break
                if cdr.bill_duration >= 120:
                    require_catcha = 0
                    break

        if require_catcha == 1:
            content["status"] = "fail"
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        content["status"] = "success"
        return Response(content, status=status.HTTP_200_OK)
