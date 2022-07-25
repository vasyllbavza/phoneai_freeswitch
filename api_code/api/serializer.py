from email.policy import default
from django.db.models import fields
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    Serializer,
    IntegerField,
)

from api.models import CallLog, CallStatus, PhoneNumber, SMSLog

class CallLogSerializer(ModelSerializer):
    class Meta:
        model = CallLog
        fields = [
            "id",
            "phone_number",
            "business_name",
            "completed",
            "attempt",
            "created_at",
            "updated_at",
        ]

    completed = CharField(source='number.completed')
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

class SMSSerializer(Serializer):

    id = IntegerField(read_only=True)
    sms_to = CharField(required=True,max_length=20)
    sms_body = CharField(required=True,max_length=140)
    callback_url = CharField(required=False,max_length=250)
    status = IntegerField(default=0)

    def create(self, validated_data):
        return SMSLog.objects.create(**validated_data)
