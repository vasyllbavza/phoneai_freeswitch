from django.db.models import fields
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
)

from api.models import CallLog, CallStatus, PhoneNumber

class CallLogSerializer(ModelSerializer):
    class Meta:
        model = CallLog
        fields = [
            "id",
            "phone_number",
            "business_name",
            "status",
            "attempt",
            "created_at",
            "updated_at",
        ]

    status = CharField(source='get_status_display')
    phone_number = CharField(source='number.number')
    business_name = CharField(source='number.business_name')
    attempt = CharField(source='number.attempt')


class PhonenumberSerializer(ModelSerializer):

    class Meta:
        model = PhoneNumber
        fields = [
            "id",
            "number",
            "business_name",
            "created_at",
            "updated_at",
        ]
