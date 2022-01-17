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
    CallMenu,
    PhoneNumber
)
from api.views import freeswitch_execute

class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'business_name' ,'attempt', 'completed', 'created_at', 'updated_at')
    list_filter = [
        "attempt",
        "created_at",
    ]
    search_fields = ['number', 'business_name']

admin.site.register(PhoneNumber, PhoneNumberAdmin)

class CallLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'uuid', 'status', 'created_at', 'updated_at','hangup_link','dtmf_link',)

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

    def dtmf_link(self, obj):
        if obj.status == CallStatus.CALLING or obj.status == CallStatus.ANSWERED:
            return format_html(
                '<a class="button" href="{}">1</a>&nbsp;\
                 <a class="button" href="{}">2</a>&nbsp;\
                 <a class="button" href="{}">3</a>&nbsp;\
                 <a class="button" href="{}">4</a>&nbsp;<br>\
                 <a class="button" href="{}">5</a>&nbsp;\
                 <a class="button" href="{}">6</a>&nbsp;\
                 <a class="button" href="{}">7</a>&nbsp;\
                 <a class="button" href="{}">8</a>&nbsp;<br>\
                 <a class="button" href="{}">*</a>&nbsp;\
                 <a class="button" href="{}">9</a>&nbsp;\
                 <a class="button" href="{}">0</a>&nbsp;\
                 <a class="button" href="{}">#</a>&nbsp;',
                reverse('admin:dtmf-action', args=[obj.pk,1]),
                reverse('admin:dtmf-action', args=[obj.pk,2]),
                reverse('admin:dtmf-action', args=[obj.pk,3]),
                reverse('admin:dtmf-action', args=[obj.pk,4]),
                reverse('admin:dtmf-action', args=[obj.pk,5]),
                reverse('admin:dtmf-action', args=[obj.pk,6]),
                reverse('admin:dtmf-action', args=[obj.pk,7]),
                reverse('admin:dtmf-action', args=[obj.pk,8]),
                reverse('admin:dtmf-action', args=[obj.pk,10]),
                reverse('admin:dtmf-action', args=[obj.pk,9]),
                reverse('admin:dtmf-action', args=[obj.pk,0]),
                reverse('admin:dtmf-action', args=[obj.pk,11]),
            )
        return ""

    dtmf_link.short_description = 'DTMF'
    dtmf_link.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^hangup_call_action/(?P<pk>\d+)/$',
                self.admin_site.admin_view(self.hangup_view),
                name='hangup-call',
            ),
            url(
                r'^dtmf_action/(?P<pk>\d+)/(?P<dtmf>\d+)/$',
                self.admin_site.admin_view(self.dtmf_view),
                name='dtmf-action',
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

    def dtmf_view(self, request, pk, dtmf):
        obj = get_object_or_404(CallLog, pk=pk)
        cmd = 'bgapi'
        if dtmf == 10:
            args = f"uuid_send_dtmf {obj.uuid} *"
        elif dtmf == 11:
            args = f"uuid_send_dtmf {obj.uuid} #"
        else:
            args = f"uuid_send_dtmf {obj.uuid} {dtmf}"

        result = freeswitch_execute(cmd,args)
        print(result)
        print(args)
        return redirect('/api/admin/api/calllog/')

admin.site.register(CallLog, CallLogAdmin)

class CallKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'menu', 'keys' ,'next', 'created_at', 'updated_at')
    list_filter = [
        "menu",
        "created_at",
    ]

admin.site.register(CallKey, CallKeyAdmin)

class CallMenuAdmin(admin.ModelAdmin):

    def keys(self):
        html = ""
        for obj in CallKey.objects.filter(menu__id=self.id):
            html += '%s,' % obj.keys
        return html
    keys.allow_tags = True
    keys.name = "Keys"

    def routekeys(self):
        html = ""
        cm = CallMenu.objects.get(pk=self.id)
        firstmenu = CallMenu.objects.filter(call__number__id=cm.call.number.id).first()
        cur_menu_id = self.id
        loop_count = 1
        while firstmenu.id != cur_menu_id and loop_count < 10:
            ck = CallKey.objects.filter(next__id=cur_menu_id).first()
            if ck:
                html += '%s,' % ck.keys
                cur_menu_id = ck.menu.id
            loop_count = loop_count + 1

        return html

    routekeys.allow_tags = True


    list_display = ('id', 'call', 'completed', 'audio_file', 'audio_file_player', 'audio_text', keys, routekeys, 'created_at', 'updated_at')
    # list_filter = [
    #     "call",
    #     "created_at",
    # ]

admin.site.register(CallMenu, CallMenuAdmin)
