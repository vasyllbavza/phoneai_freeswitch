from rest_framework.serializers import (
    CharField,
    ModelSerializer,
)

from api.models import CallLog, CallStatus

class CallLogSerializer(ModelSerializer):
    class Meta:
        model = CallLog
        fields = [
            "id",
            "number",
            "status",
            "attempt",
            "created_at",
            "updated_at",
        ]

    status = CharField(source='get_status_display')