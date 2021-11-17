from django.contrib import admin
from django.conf.urls import url
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import get_object_or_404,redirect

# Register your models here.
from api.models import (
    CallLog,
    CallKey,
)
from api.views import freeswitch_execute

class CallLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'uuid', 'status', 'created_at', 'updated_at','hangup_link')

    actions = ['hangup_call']

    @admin.action(description='Hangup Call')
    def hangup_call(self, request, queryset):
        for qs in queryset:
            cmd = 'bgapi'
            args = f"uuid_kill {qs.uuid}"
            result = freeswitch_execute(cmd,args)
            print(result)

    def hangup_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Hangup</a>&nbsp;',
            reverse('admin:hangup-call', args=[obj.pk]),
        )

    hangup_link.short_description = 'Hangup Call'
    hangup_link.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^hangup_call_action/(?P<pk>\d+)/$',
                self.admin_site.admin_view(self.hangup_view),
                name='hangup-call',
            ),
        ]
        return custom_urls + urls

    # @permission_required('CallLog.can_change')
    def hangup_view(self, request, pk):
        obj = get_object_or_404(CallLog, pk=pk)
        cmd = 'bgapi'
        args = f"uuid_kill {obj.uuid}"
        result = freeswitch_execute(cmd,args)
        print(result)
        print(args)
        return redirect('/api/admin/api/calllog/')

admin.site.register(CallLog, CallLogAdmin)

class CallKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'call', 'parent', 'keys', 'level', 'processed', 'created_at', 'updated_at')

admin.site.register(CallKey, CallKeyAdmin)
