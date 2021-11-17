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
)

try:
    from freeswitchESL import ESL
except ImportError:
    ESL = None
    print("ESL")

import logging
logger = logging.getLogger('call_esl')

def signal_term_handler(signal, frame):

    print >>sys.stderr,  'got SIGTERM'
    logger.error('got SIGTERM')
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_term_handler)

def logme(level,title="",message=""):

    print("%s %s ::  %s : %s" % (datetime.datetime.now(),level,title,message))
    if level == "DEBUG":
        logger.debug("%s %s ::  %s : %s" % (datetime.datetime.now(),level,title,message))
    if level == "ERROR":
        logger.error("%s %s ::  %s : %s" % (datetime.datetime.now(),level,title,message))
    if level == "INFO":
        logger.info("%s %s ::  %s : %s" % (datetime.datetime.now(),level,title,message))

def log_debug(title,message=""):
    logme("DEBUG",title,message)

def log_error(title,message=""):
    logme("ERROR",title,message)

def log_info(title,message=""):
    logme("INFO",title,message)

def msg_inpect(msg):
    logme("INFO",msg)

def json_outp(jsondata):

    data = json.dumps(jsondata, indent=4, sort_keys=True)
    log_info(data)

def get_header(event,header_name):
    try:
        hdr = event.getHeader(header_name)
        if hdr:
            return hdr
        else:
            return ""
    except:
        return ""

def fs_send_dtmf(conn, uuid, dtmf):
    cmd = 'bgapi'
    args = f"uuid_send_dtmf {uuid} {dtmf}"
    ev = conn.api(str(cmd),str(args))
    fs_result = ''
    if ev:
        fs_result = ev.serialize()
        # log_info(fs_result)
        res = fs_result.split('\n\n',1)
        if res[1]:
            fs_result = res[1]
            log_info(fs_result)
            return True
    return False

def fs_set_var(conn, uuid, var, val):
    cmd = 'bgapi'
    args = f"uuid_setvar {uuid} {var} {val}"
    ev = conn.api(str(cmd),str(args))
    fs_result = ''
    if ev:
        fs_result = ev.serialize()
        # log_info(fs_result)
        res = fs_result.split('\n\n',1)
        if res[1]:
            fs_result = res[1]
            log_info(fs_result)
            return True
    return False

con = ESL.ESLconnection(settings.ESL_HOSTNAME, settings.ESL_PORT, settings.ESL_SECRET)
print("[x] Starting..")

if con.connected():
    log_info(" [x] FreeSWITCH is connected..")
    log_info(con)
else:
    log_error(" [x] FreeSWITCH connectivity Error!..")
    sys.exit(1)

log_debug(" [x] Starting.....OK")

try:

    con.events('plain', 'HEARTBEAT CUSTOM mydtbd::info')

    idle_count = 0
    hb_count = 0
    while 1:
        if con.connected():
            try:
                e = con.recvEventTimed(2000)
            except Exception as exp:
                log_error( exp )
                exit(0)

            if e:
                
                event_name = get_header(e,"Event-Name")
                domain_name = get_header(e,'variable_domain_uuid')
                switchname = get_header(e,'FreeSWITCH-Switchname')

                event_time = "%sZ" % datetime.datetime.utcnow().replace(microsecond=0).isoformat()
                myDate = datetime.datetime.now()

                if event_name == "HEARTBEAT":
                    event_info = get_header(e,"Event-Info")
                    up_time = get_header(e,"Up-Time")
                    # log_debug(event_name,"%s - idle_count =%s" %(event_info,str(idle_count)))
                    callinfo = {}
                    callinfo['up_time'] = up_time
                    callinfo['event_info'] = event_info
                    callinfo['switchname'] = switchname
                    callinfo['event'] = event_name
                    callinfo['message'] = event_info
                    key = "system.heartbeat.message"
                    data = json.dumps(callinfo)

                if event_name == "CUSTOM":
                    
                    # print(e.serialize())

                    sub_class = get_header(e,"Event-Subclass")

                    if sub_class == "mydtbd::info":
                        idle_count = 0

                        event_action = get_header(e,"action")
                        event_keys = get_header(e,"keys")
                        call_uuid = get_header(e,"call_uuid")
                        call_id = get_header(e,"call_id")
                        log_info(f"{event_action} {call_id}")
                        # call_id = 1
                        if event_action == "call_keys":
                            try:
                                call = CallLog.objects.get(pk=call_id)
                                if event_keys:
                                    kk = event_keys.split(",")
                                    if not kk:
                                        continue
                                    for k in kk:
                                        if k:
                                            try:
                                                callkey = CallKey(call=call,keys=k)
                                                callkey.save()
                                                log_info(f"{callkey.id} key : {k}")
                                            except:
                                                pass
                            except:
                                logger.error("callkey save error!!")

                        if event_action == "call_started":
                            try:
                                call = CallLog.objects.get(pk=call_id)
                                call.status = CallStatus.ANSWERED
                                call.save()
                                callkeys = CallKey.objects.filter(call=call)
                                if callkeys:
                                    for k in callkeys:
                                        k.delete()
                            except:
                                logger.error("CallLog save error!!")

                        if event_action == "call_ended":
                            try:
                                call = CallLog.objects.get(pk=call_id)
                                call.status = CallStatus.PROCESSED
                                call.save()
                            except:
                                logger.error("CallLog save error!!")

                        if event_action == "silence_detected":
                            print(e.serialize())
                            key_parent = get_header(e, "key_parent")
                            key_level = get_header(e, "key_level")
                            call_keys = get_header(e, "param3")
                            log_info("silence_detected")
                            ckeys = CallKey.objects.filter(call_id=call_id,processed=0,level=key_level).order_by('id')
                            if len(ckeys) > 0:
                                ckey = ckeys[0]
                                log_info( f"sending DTMF [{ckey.keys}] to {call_id}, {call_uuid}")
                                ckey.processed=1
                                ckey.save()
                                fs_send_dtmf(con, call_uuid, ckey.keys)
                                fs_set_var(con, call_uuid,"key_level", int(key_level)+1)
                                fs_set_var(con, call_uuid,"key_parent", ckey.id)
                            pass
            else:
                if idle_count < 120:
                    idle_count = idle_count + 1

                if idle_count == 120:
                    django.db.close_old_connections()
                    logger.debug("closing db connection")
                    idle_count = 222

        else:
            log_error("FreeSWITCH gone away. we are closing here")
            sys.exit(0)

except KeyboardInterrupt:

    log_error("KeyboardInterrupt..Good bye")
    con.disconnect()
    sys.exit(0)

except SystemExit:

    log_error("SystemExit..Good bye")
    con.disconnect()
    sys.exit(0)

except Exception as e:

    log_error(e)

except:

    log_error("unknown error!")
    pass
