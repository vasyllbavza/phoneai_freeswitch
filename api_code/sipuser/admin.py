from django.contrib import admin

from sipuser.models import  (
    Domain,
    FsProvider,
    FsDidNumber,
    FsUser,
    Extension
)


# Register your models here.
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain','description', 'created_at', 'updated_at')
    list_filter = [
        "created_at",
    ]

    search_fields = ['domain', 'description']

admin.site.register(Domain, DomainAdmin)

class FsUserAdmin(admin.ModelAdmin):
    list_display = ('user','domain', 'email', 'cellphone', 'created_at', 'updated_at')
    list_filter = [
        'domain',
        "created_at",
    ]

    search_fields = ['email', 'cellphone']

admin.site.register(FsUser, FsUserAdmin)

class ExtensionAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'sip_username', 'sip_password', 'created_at', 'updated_at')
    list_filter = [
        "created_at",
    ]

    search_fields = ['sip_username',]

admin.site.register(Extension, ExtensionAdmin)

class FsProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider_type','acl', 'created_at', 'updated_at')
    list_filter = [
        "created_at",
    ]

    search_fields = ['name', 'provider_type', 'acl',]

admin.site.register(FsProvider, FsProviderAdmin)

class FsDidNumberAdmin(admin.ModelAdmin):
    list_display = ('provider_name','phonenumber', 'extension', 'created_at')
    list_filter = [
        "domain",
        "created_at",
    ]

    search_fields = ['phonenumber','domain',]

admin.site.register(FsDidNumber, FsDidNumberAdmin)

