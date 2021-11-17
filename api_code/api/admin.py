from django.contrib import admin

# Register your models here.
from api.models import (
    CallLog,
    CallKey,
)
from api.views import freeswitch_execute

class CallLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'uuid', 'status', 'created_at', 'updated_at')

    actions = ['hangup_call']

    @admin.action(description='Hangup Call')
    def hangup_call(self, request, queryset):
        # queryset.update(status='p')
        for qs in queryset:
            cmd = 'bgapi'
            args = f"uuid_kill {qs.uuid}"
            result = freeswitch_execute(cmd,args)
            print(result)

admin.site.register(CallLog, CallLogAdmin)

class CallKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'call', 'parent', 'keys', 'level', 'processed', 'created_at', 'updated_at')

admin.site.register(CallKey, CallKeyAdmin)
