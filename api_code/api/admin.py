from django.contrib import admin
from django.conf.urls import url
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import get_object_or_404,redirect

# Register your models here.
from api.models import (
    CallLog,
    CallKey,
    CallStatus,
    CallMenu
)
from api.views import freeswitch_execute

class CallLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'business_name', 'uuid', 'status', 'attempt', 'created_at', 'updated_at','hangup_link')

    actions = ['hangup_call']

    @admin.action(description='Hangup Call')
    def hangup_call(self, request, queryset):
        for qs in queryset:
            cmd = 'bgapi'
            args = f"uuid_kill {qs.uuid}"
            result = freeswitch_execute(cmd,args)
            print(result)

    def hangup_link(self, obj):
        if obj.status == CallStatus.CALLING or obj.status == CallStatus.ANSWERED:
            return format_html(
                '<a class="button" href="{}">Hangup</a>&nbsp;',
                reverse('admin:hangup-call', args=[obj.pk]),
            )
        return ""

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
    list_display = ('id', 'menu', 'keys', 'level', 'processed', 'audio_text','audio_file', 'created_at', 'updated_at')
    list_filter = [
        "menu",
        "created_at",
    ]

admin.site.register(CallKey, CallKeyAdmin)

class CallMenuAdmin(admin.ModelAdmin):

    def ivrkeys(self):
        html = ""
        for obj in CallKey.objects.filter(menu__id=self.id):
            html += '%s,' % obj.keys
        return html
    ivrkeys.allow_tags = True

    list_display = ('id', 'call', 'audio_file', 'audio_file_player', 'audio_text', ivrkeys, 'route_keys', 'created_at', 'updated_at')
    # list_filter = [
    #     "call",
    #     "created_at",
    # ]

admin.site.register(CallMenu, CallMenuAdmin)
