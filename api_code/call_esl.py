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
                    
                    print(e.serialize())

                    sub_class = get_header(e,"Event-Subclass")

                    if sub_class == "mydtbd::info":
                        idle_count = 0

                        event_action = get_header(e,"action")
                        event_keys = get_header(e,"keys")
                        call_uuid = get_header(e,"call_uuid")
                        call_id = get_header(e,"call_id")
                        logger.info(f"{event_action} {call_id}")

                        if event_action == "call_keys":
                            try:
                                call = CallLog.objects.filter(id=call_id)
                                callkey = CallKey(call=call,keys=event_keys)
                                callkey.save()
                            except:
                                logger.error("callkey save error!!")

                        if event_action == "call_started":
                            try:
                                call = CallLog.objects.filter(id=call_id)
                                call.status = CallStatus.CALLING
                                call.save()
                            except:
                                logger.error("CallLog save error!!")

                        if event_action == "silence_detected":
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
