import uuid

from django.shortcuts import render
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    CallLog,
    CallStatus,
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

        call_uuid = str(uuid.uuid4())

        call = CallLog(number=dial_number,status=CallStatus.PENDING)
        call.uuid = call_uuid
        call.save()
        call_id = call.id

        cmd = 'bgapi'
        callParams = "{phoneai_call_id=%s,ignore_early_media=true,origination_caller_id_name=phoneAI,origination_caller_id_number=%s,origination_uuid=%s}" % (str(call_id),caller_id,call_uuid)
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

        return Response(content)

