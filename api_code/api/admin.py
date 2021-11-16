from django.contrib import admin

# Register your models here.
from api.models import (
    CallLog,
    CallKey,
)

class CallLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'uuid', 'status', 'created_at', 'updated_at')

admin.site.register(CallLog, CallLogAdmin)

class CallKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'call', 'parent', 'keys', 'level', 'processed', 'created_at', 'updated_at')

admin.site.register(CallKey, CallKeyAdmin)
