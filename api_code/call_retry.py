import os
import sys
import signal
import datetime
import json
import django.db
import urllib

from django.core.handlers.wsgi import WSGIHandler
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phoneai_api.settings")
application = get_wsgi_application()

from django.conf import settings

from api.models import (
    CallLog,
    CallKey,
    CallStatus,
    CallMenu,
    PhoneNumber,
)

try:
    from freeswitchESL import ESL
except ImportError:
    ESL = None
    print("ESL")

import logging

logging.basicConfig(
    filename='call_retry.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-6s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

def signal_term_handler(signal, frame):

    print >>sys.stderr,  'got SIGTERM'
    logger.error('got SIGTERM')
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_term_handler)

def json_outp(jsondata):

    data = json.dumps(jsondata, indent=4, sort_keys=True)
    logger.info(data)

def get_header(event,header_name):
    try:
        hdr = event.getHeader(header_name)
        if hdr:
            return hdr
        else:
            return ""
    except:
        return ""

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

def get_phonenumber_for_retry():
    import uuid
    # caller_id = request.query_params.get('caller_id','14582037530')
    caller_id = '14582037530'
    numbers = PhoneNumber.objects.filter(completed=False, retry_auto=True)
    for number in numbers:
        call_menu_id = 0
        call_uuid = str(uuid.uuid4())
        call = CallLog.objects.filter(number=number, status=CallStatus.PROCESSED).order_by('-id').first()
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
                continue

        cmd = 'bgapi'
        phonenumber_info = "is_new_call=0,phoneai_number_id=%s,phoneai_call_id=%s,call_menu_id=%s" % (str(number.id),str(call_id), str(call_menu_id))
        callParams = "{%s,ignore_early_media=true,origination_caller_id_name=phoneAI,origination_caller_id_number=%s,origination_uuid=%s}" % (phonenumber_info,caller_id,call_uuid)
        args = "originate %ssofia/gateway/58e29eb4-bc1e-4c3d-bf30-25ff961b1b99/69485048*%s &lua(phoneai.lua)" %(callParams,number.number)
        print( "%s %s" %(cmd,args) )
        result = freeswitch_execute(cmd,args)
        if result['status'] < 1:
            logger.error("error: %s" % result['message'])
            continue

        call.status = CallStatus.CALLING
        call.save()


get_phonenumber_for_retry()
