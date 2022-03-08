import uuid

from django.shortcuts import render
from api.models import CallKey, CallMenu
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status

import json

from api.models import (
    AgentCallLog,
    CallLog,
    CallStatus,
    PhoneNumber,
    SMSLog,
)
from api.utils import (
    TreeNode,
    send_sms,
)
from api.serializer import (
    CallLogSerializer,
    PhonenumberSerializer,
    SMSSerializer,
)

from phoneai_api import settings

try:
    from freeswitchESL import ESL
except ImportError:
    ESL = None

class HelloView(APIView):

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

def freeswitch_execute(cmd,params):

    result = {}
    if not ESL:
        result['status'] = -1
        result['message'] = "ESL not loaded"
        return result
    else:
        # reload(ESL)
        c = ESL.ESLconnection(settings.ESL_HOSTNAME, settings.ESL_PORT, settings.ESL_SECRET)
        if c.connected() != 1:
            result['status'] = 0
            result['message'] = "Switch Connection error"
            return result
        ev = c.api(str(cmd),str(params))

        c.disconnect()
        fs_result = ''
        if ev:
            fs_result = ev.serialize()
            res = fs_result.split('\n\n',1)
            if res[1]:
                fs_result = res[1]

        result['status'] = 1
        result['message'] = ""
        result['fs_output'] = fs_result
        return result

class MakeCallView(APIView):

    def get(self,request,format=None):

        content = {}

        dial_number = request.query_params.get('number','')
        caller_id = request.query_params.get('caller_id','14582037530')
        is_new_call = request.query_params.get('new','1')
        business_name = request.query_params.get('business_name','')

        number, isnew = PhoneNumber.objects.get_or_create(number=dial_number)
        if business_name:
            number.business_name = business_name
        number.retry_auto = 1
        number.save()
        is_new_call = "0"
        call_menu_id = 0
        call_uuid = str(uuid.uuid4())
        if is_new_call == "1":
            call = CallLog(number=number,status=CallStatus.PENDING)
            call.business_name = business_name
            call.uuid = call_uuid
            call.save()
            call_id = call.id
        else:
            call = CallLog.objects.filter(number=number).order_by('-id').first()
            if call:
                call = CallLog.objects.get(pk=call.id)
                call.uuid = call_uuid
                call.save()

                call_id = call.id

            else:
                call = CallLog(number=number,status=CallStatus.PENDING)
                call.uuid = call_uuid
                call.save()
                call_id = call.id

            firstmenu = CallMenu.objects.filter(call__number=number, completed=False).first()
            if firstmenu:
                call_menu_id = firstmenu.id
            else:
                menu_completed = CallMenu.objects.filter(call__number=number, completed=True).first()
                if menu_completed:
                    call.number.completed = True
                    call.number.save()

                    content['status'] = "fail"
                    content['message'] = "crawl is completed already"
                    content['fs_output'] = ""
                    return Response(content)

        cmd = 'bgapi'
        phonenumber_info = "is_new_call=%s,phoneai_number_id=%s,phoneai_call_id=%s,call_menu_id=%s" % (str(is_new_call),str(number.id),str(call_id), str(call_menu_id))
        callParams = "{%s,ignore_early_media=true,origination_caller_id_name=phoneAI,origination_caller_id_number=%s,origination_uuid=%s}" % (phonenumber_info,caller_id,call_uuid)
        args = "originate %ssofia/gateway/58e29eb4-bc1e-4c3d-bf30-25ff961b1b99/69485048*%s &lua(phoneai.lua)" %(callParams,dial_number)
        print( "%s %s" %(cmd,args) )
        result = freeswitch_execute(cmd,args)
        if result['status'] < 1:
            content['status'] = "fail"
            content['message'] = result['message']
            content['fs_output'] = ""
            return Response(content)

        content['dial_number'] = dial_number
        content['status'] = "success"
        content['call_uuid'] = call_uuid
        content['message'] = result['message']
        content['fs_output'] = result['fs_output']
        # content['args'] = args
        call.status = CallStatus.CALLING
        call.save()

        return Response(content)

class ScanCallView(APIView, LimitOffsetPagination):

    def get(self,request,format=None):

        content = {}
        content['status'] = "success"

        dial_number = request.query_params.get('number','')
        if dial_number == "":
            call = CallLog.objects.all().order_by('-id')
        else:
            call = CallLog.objects.filter(number__number=dial_number).order_by('-id')

        result = self.paginate_queryset(call, request, view=self)

        serializer = CallLogSerializer(result, many=True)

        return self.get_paginated_response(serializer.data)

def menu_target_keys(menu_id):

    cm = CallMenu.objects.get(pk=menu_id)
    current_menu_id = menu_id
    firstmenu = CallMenu.objects.filter(call__number__id=cm.call.number.id).first()
    loop_count = 1
    dtmf = ""
    while firstmenu.id != current_menu_id and loop_count < 10:
        ck = CallKey.objects.filter(next__id=current_menu_id).first()
        if ck:
            if dtmf == "":
                dtmf += '%s' % ck.keys
            else:
                dtmf += ',%s' % ck.keys
            current_menu_id = ck.menu.id
        loop_count = loop_count + 1
    return dtmf[::-1]

def make_tree(cm_id, child, key, parent_text, keys_to_reach):

    tree = None
    cm = CallMenu.objects.get(pk=cm_id)
    if cm:
        menu = {}
        menu["audio_text"] = cm.audio_text
        if cm.audio_text_debug:
            menu["audio_text_debug"] = json.loads(cm.audio_text_debug)
        else:
            menu["audio_text_debug"] = cm.audio_text_debug
        tree = TreeNode(cm.id, menu, child, key, parent_text, keys_to_reach)
        cks = CallKey.objects.filter(menu=cm.id)
        for ck in cks:
            if ck.next:
                # child = make_tree(ck.next.id, None, ck.keys)
                child = make_tree(ck.next.id, None, ck.keys, ck.audio_text, menu_target_keys(ck.next.id))
                tree.children.append(child)
            # else:
            #     child = TreeNode("", None, ck.keys)
            #     tree.children.append(child)
    return tree

class ShowCallMenu(APIView):

    def get(self, request, format=None):

        dial_number = request.query_params.get('number','')

        content = {}
        number = PhoneNumber.objects.get(number=dial_number)
        content['id'] = number.id
        content['number'] = number.number
        content['business_name'] = number.business_name
        content['retry_enabled'] = number.retry_auto
        content['attempt'] = number.attempt
        content['completed'] = number.completed

        node_start = 0
        cm = CallMenu.objects.filter(call__number__number=dial_number).first()

        tree = make_tree(cm.id, None, '', '', '')

        json_str = json.dumps(tree, indent=2)
        print(json_str)
        content["menu"] = tree
        return Response(content)

class PhonenumberView(APIView):

    def post(self,request,format=None):

        content = {}

        dial_number = request.query_params.get('number','')
        business_name = request.query_params.get('business_name','')

        number, isnew = PhoneNumber.objects.get_or_create(number=dial_number)
        if business_name:
            number.business_name = business_name
        number.save()

        serializer = PhonenumberSerializer(number)
        return Response(serializer.data)

class MakeRetryCallSubMenuView(APIView):

    def get(self,request,format=None):

        content = {}

        menu_id = request.query_params.get('id','')
        try:
            menu = CallMenu.objects.get(pk=menu_id)
        except:
            content['status'] = "fail"
            content['message'] = "menu not found"
            content['fs_output'] = ""
            return Response(content)

        if menu.completed == True:
            content['status'] = "fail"
            content['message'] = "menu is completed already."
            content['fs_output'] = ""
            return Response(content)

        caller_id = '14582037530'
        number = menu.call.number
        dial_number = number.number
        call_id = menu.call.id
        call_menu_id = menu.id
        call_uuid = str(uuid.uuid4())

        menu.call.status = CallStatus.CALLING
        menu.call.uuid = call_uuid
        menu.call.save()

        cmd = 'bgapi'
        phonenumber_info = "is_new_call=0,phoneai_number_id=%s,phoneai_call_id=%s,call_menu_id=%s" % (str(number.id),str(call_id), str(call_menu_id))
        callParams = "{%s,ignore_early_media=true,origination_caller_id_name=phoneAI,origination_caller_id_number=%s,origination_uuid=%s}" % (phonenumber_info,caller_id,call_uuid)
        args = "originate %ssofia/gateway/58e29eb4-bc1e-4c3d-bf30-25ff961b1b99/69485048*%s &lua(phoneai.lua)" %(callParams,dial_number)
        print( "%s %s" %(cmd,args) )
        result = freeswitch_execute(cmd,args)
        if result['status'] < 1:
            content['status'] = "fail"
            content['message'] = result['message']
            content['fs_output'] = ""
            return Response(content)

        content['dial_number'] = dial_number
        content['status'] = "success"
        content['call_uuid'] = call_uuid
        content['message'] = result['message']
        content['fs_output'] = result['fs_output']

        return Response(content)

class MakeCallSubMenuView(APIView):

    def get(self,request,format=None):

        content = {}

        forwarding_number = request.query_params.get('forwarding_number','')
        if forwarding_number == "":
            content['status'] = "fail"
            content['message'] = "forwarding_number is required!"
            content['fs_output'] = ""
            return Response(content)

        menu_id = request.query_params.get('id','')
        try:
            menu = CallMenu.objects.get(pk=menu_id)
        except:
            content['status'] = "fail"
            content['message'] = "menu not found"
            content['fs_output'] = ""
            return Response(content)

        # if menu.completed == True:
        #     content['status'] = "fail"
        #     content['message'] = "menu is completed already."
        #     content['fs_output'] = ""
        #     return Response(content)

        caller_id = '14582037530'
        number = menu.call.number
        dial_number = number.number
        call_id = menu.call.id
        call_menu_id = menu.id
        call_uuid = str(uuid.uuid4())

        menu.call.status = CallStatus.CALLING
        menu.call.uuid = call_uuid
        menu.call.save()

        agentcall = AgentCallLog(number=number, menu=menu,uuid=call_uuid)
        agentcall.status = CallStatus.CALLING
        agentcall.forwarding_number = forwarding_number
        agentcall.save()

        cmd = 'bgapi'
        phonenumber_info = "agentcall_id=%s,forwarding_number=%s,is_new_call=0,phoneai_number_id=%s,phoneai_call_id=%s,call_menu_id=%s" % (str(agentcall.id),forwarding_number,str(number.id),str(call_id), str(call_menu_id))
        callParams = "{%s,ignore_early_media=true,origination_caller_id_name=phoneAI,origination_caller_id_number=%s,origination_uuid=%s}" % (phonenumber_info,caller_id,call_uuid)
        args = "originate %ssofia/gateway/58e29eb4-bc1e-4c3d-bf30-25ff961b1b99/69485048*%s &lua(phoneai_go.lua)" %(callParams,dial_number)
        print( "%s %s" %(cmd,args) )
        # content["command"] = cmd
        # content["args"] = args
        # return Response(content)
        result = freeswitch_execute(cmd,args)
        if result['status'] < 1:
            content['status'] = "fail"
            content['message'] = result['message']
            content['fs_output'] = ""
            return Response(content)

        content['dial_number'] = dial_number
        content['status'] = "success"
        content['call_uuid'] = call_uuid
        content['message'] = result['message']
        content['fs_output'] = result['fs_output']

        return Response(content)

class SendSMSView(APIView):

    def post(self,request,format=None):

        # to_number = request.query_params.post('to_number','')
        # sms_text = request.query_params.post('sms_text','')

        smsdata = SMSSerializer(data=request.data)
        if smsdata.is_valid():
            sms = SMSLog(sms_to=smsdata.sms_to, sms_body=smsdata.sms_body, status=0)
            sms.save()

            result = send_sms(to_number=smsdata.sms_to,sms_text=smsdata.sms_body)
            sms.sms_result = result
            sms.save()

            content = {}
            content["status"] = "ok"
            content["result"] = str(result)

            # smsdata.save()
            return Response(smsdata.data, status=status.HTTP_201_CREATED)

        return Response(smsdata.errors, status=status.HTTP_400_BAD_REQUEST)
