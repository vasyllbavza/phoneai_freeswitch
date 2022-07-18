from django.contrib import admin

from .models import (
    Contacts,
    Phonebook,
    InboundNumbers,
)


class PhonebookAdmin(admin.ModelAdmin):
    list_display = ('extension', 'name', 'created_at', 'updated_at')

    search_fields = ['extension', 'name']


admin.site.register(Phonebook, PhonebookAdmin)


class ContactsAdmin(admin.ModelAdmin):
    list_display = ('phonebook', 'phonenumber', 'source', 'active', 'created_at', 'updated_at')
    list_filter = [
        "phonebook",
    ]

    search_fields = ['phonebook', 'phonenumber']


admin.site.register(Contacts, ContactsAdmin)


class InboundNumbersAdmin(admin.ModelAdmin):
    list_display = (
        'phonenumber',
        'caller_type',
        'caller_carrier',
        'carrier_expired',
        'spam_risk',
        'spam_expired',
        'created_at',
        'updated_at'
    )
    list_filter = [
        "caller_carrier",
        "spam_risk",
    ]

    search_fields = ['phonenumber', 'caller_type', 'caller_carrier']


admin.site.register(InboundNumbers, InboundNumbersAdmin)
