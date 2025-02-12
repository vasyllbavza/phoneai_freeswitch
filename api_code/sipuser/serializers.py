from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)
from django.conf import settings

from .models import Extension, FsDidNumber, FsUser, FsCDR, BridgeCall, ConferenceCenter


class ExtensionCreateSerializer(ModelSerializer):
    class Meta:
        model = Extension
        fields = [
            "id",
            "sip_username",
            "sip_password",
            "cellphone",
            "transcription",
        ]

    # MARK: - Properties

    def create(self, validated_data):
        print(validated_data)
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['domain'] = instance.user.domain.domain

        return representation


class ExtensionSerializer(ModelSerializer):
    class Meta:
        model = Extension
        fields = [
            "id",
            "user_id",
            "cellphone",
            "transcription",
            "sip_username",
            "sip_password",
            "updated_at",
            "updated_at",
        ]

    # MARK: - Properties

    # MARK: - Methods

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['domain'] = instance.user.domain.domain

        return representation


class ExtensionRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Extension
        fields = [
            "id",
            "user",
            "cellphone",
            "transcription",
            "sip_username",
            "sip_password",
            "created_at",
            "updated_at",
        ]

    # MARK: - Properties

    user = SerializerMethodField()

    # MARK: - Methods

    def get_user(self, obj):
        if obj.user_id:
            try:
                fsuser = FsUser.objects.get(pk=obj.user_id)
                return {
                    "id": fsuser.id,
                    "username": fsuser.user.username or "",
                }
            except FsUser.DoesNotExist:
                pass
        return None


class ExtensionUpdateSerializer(ModelSerializer):
    class Meta:
        model = Extension
        fields = [
            "sip_username",
            "sip_password",
            "cellphone",
            "transcription",
        ]


### FS DID number
class DidNUmberSerializer(ModelSerializer):
    class Meta:
        model = FsDidNumber
        fields = [
            "id",
            "provider",
            "phonenumber",
            "domain",
            "extension",
            "created_at",
            # "updated_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['domain'] = instance.domain.domain

        return representation


class DidNUmberCreateSerializer(ModelSerializer):
    class Meta:
        model = FsDidNumber
        fields = [
            "phonenumber",
            "extension"
        ]

    # MARK: - Properties
    extension = IntegerField(
        label="Destination Extension ID",
        min_value=1,
        max_value=2147483647,
        source="extension_id",
    )

    # def create(self, validated_data):
    #     print(validated_data)
    #     return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # representation['domain'] = instance.domain.domain

        return representation

    def validate_extension(self, value):
        try:
            Extension.objects.get(pk=value)
            return value
        except Extension.DoesNotExist:
            pass
        raise ValidationError("A valid value is required.")


class DidNumberSearchSerializer(ModelSerializer):
    class Meta:
        model = FsDidNumber
        fields = []


class CdrSerializer(ModelSerializer):
    class Meta:
        model = FsCDR
        fields = [
            "id",
            "domain",
            "call_direction",
            "call_uuid",
            "didnumber",
            "call_from",
            "call_to",
            "extension",
            "is_verified",
            "in_contact",
            "bill_duration",
            "recording",
            "transcription_text",
            "hangup_cause",
            "started_at",
            "created_at",
        ]

    # MARK: - Properties

    # MARK: - Methods

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation['domain'] = instance.domain.domain
        except:
            pass
        # representation['category'] = CategorySerializer(instance.category).data
        return representation


class BridgeCallSerializer(ModelSerializer):
    class Meta:
        model = BridgeCall
        fields = [
            "id",
            "didnumber",
            "target_number",
            "timeout",
            "active",
            "expired_at"
        ]


class ConferenceCreateSerializer(ModelSerializer):
    class Meta:
        model = ConferenceCenter
        fields = [
            "didnumber",
            "pin",
        ]

class ConferenceSerializer(ModelSerializer):
    class Meta:
        model = ConferenceCenter
        fields = [
            "didnumber",
            "pin",
        ]
