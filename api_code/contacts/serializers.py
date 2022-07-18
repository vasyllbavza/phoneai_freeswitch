from rest_framework.serializers import ModelSerializer

from .models import Phonebook, Contacts, InboundNumbers


class PhonebookCreateSerializer(ModelSerializer):
    class Meta:
        model = Phonebook
        fields = [
            "id",
            "extension",
            "name",
        ]

    # MARK: - Properties

    # MARK: - Methods

    def create(self, validated_data):
        print(validated_data)
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class PhonebookSerializer(ModelSerializer):
    class Meta:
        model = Phonebook
        fields = [
            "id",
            "extension",
            "name",
            "created_at",
            # "updated_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class PhonebookUpdateSerializer(ModelSerializer):
    class Meta:
        model = Phonebook
        fields = [
            "extension",
            "name",
        ]


class ContactsCreateSerializer(ModelSerializer):
    class Meta:
        model = Contacts
        fields = [
            "id",
            "phonebook",
            "phonenumber",
            "active",
        ]

    # MARK: - Properties

    # MARK: - Methods

    def create(self, validated_data):
        print(validated_data)
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class ContactsSerializer(ModelSerializer):
    class Meta:
        model = Contacts
        fields = [
            "id",
            "phonebook",
            "phonenumber",
            "source",
            "active",
            "created_at",
            # "updated_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class ContactsUpdateSerializer(ModelSerializer):
    class Meta:
        model = Contacts
        fields = [
            "phonebook",
            "phonenumber",
            "active",
        ]


class InboundNumbersSerializer(ModelSerializer):
    class Meta:
        model = InboundNumbers
        fields = [
            "id",
            "phonenumber",
            "caller_type",
            "caller_carrier",
            "carrier_expired",
            "spam_risk",
            "fraud_risk",
            "unlawful_risk",
            "spam_expired",
            "created_at",
            "updated_at",
        ]
