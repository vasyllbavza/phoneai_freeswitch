from django.contrib import admin

from .models import (
    Contacts,
    Phonebook,
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
