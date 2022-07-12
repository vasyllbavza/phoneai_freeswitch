from django.contrib import admin


from sipuser.models import (
    Domain,
    Extension,
    FsCDR,
    FsProvider,
    FsDidNumber,
    FsUser,
    BridgeCall,
)


# Register your models here.
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'description', 'created_at', 'updated_at')
    list_filter = [
        "created_at",
    ]

    search_fields = ['domain', 'description']


admin.site.register(Domain, DomainAdmin)


class FsUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'domain', 'email', 'cellphone', 'created_at', 'updated_at')
    list_filter = [
        'domain',
        "created_at",
    ]

    search_fields = ['email', 'cellphone']


admin.site.register(FsUser, FsUserAdmin)


class ExtensionAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'sip_username', 'sip_password', 'cellphone', 'created_at', 'updated_at')
    list_filter = [
        "created_at",
    ]

    search_fields = ['sip_username']


admin.site.register(Extension, ExtensionAdmin)


class FsProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider_type', 'acl', 'created_at', 'updated_at')
    list_filter = [
        "created_at",
    ]

    search_fields = ['name', 'provider_type', 'acl']


admin.site.register(FsProvider, FsProviderAdmin)


class FsDidNumberAdmin(admin.ModelAdmin):
    list_display = ('provider_name', 'phonenumber', 'extension', 'created_at')
    list_filter = [
        "domain",
        "created_at",
    ]

    search_fields = ['phonenumber', 'domain']


admin.site.register(FsDidNumber, FsDidNumberAdmin)


class FsCDRAdmin(admin.ModelAdmin):
    list_display = (
        'domain',
        'call_uuid',
        'call_direction',
        'caller_type',
        'caller_carrier',
        'is_verified',
        'in_contact',
        'captcha_verified',
        'call_from',
        'call_to',
        'didnumber',
        'extension',
        'recording_player',
        'created_at'
    )
    # list_filter = [
    #     "domain",
    #     'didnumber',
    #     "created_at",
    # ]

    search_fields = ['call_uuid'', call_from', 'call_to']


admin.site.register(FsCDR, FsCDRAdmin)


class BridgeCallAdmin(admin.ModelAdmin):
    list_display = ('id', 'didnumber', 'target_number', 'active', 'timeout', 'expired_at', 'created_at')

    search_fields = ['didnumber', 'target_number']


admin.site.register(BridgeCall, BridgeCallAdmin)
