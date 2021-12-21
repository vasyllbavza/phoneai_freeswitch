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
    filename='call_esl.log',
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
            logger.info(fs_result)
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
            logger.info(fs_result)
            return True
    return False

con = ESL.ESLconnection(settings.ESL_HOSTNAME, settings.ESL_PORT, settings.ESL_SECRET)
print("[x] Starting..")

if con.connected():
    logger.info(" [x] FreeSWITCH is connected..")
    logger.info(con)
else:
    logger.error(" [x] FreeSWITCH connectivity Error!..")
    sys.exit(1)

logger.info(" [x] Starting.....OK")

try:

    con.events('plain', 'HEARTBEAT CUSTOM mydtbd::info')

    idle_count = 0
    hb_count = 0
    while 1:
        if con.connected():
            try:
                e = con.recvEventTimed(2000)
            except Exception:
                logger.exception( "Exception occured" )
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
                        number_id = get_header(e,"number_id")
                        call_id = get_header(e,"call_id")
                        is_new_call = get_header(e,"is_new_call")

                        logger.info(f"{event_action} {call_id}")
                        # debug
                        # call_id = 1
                        # if event_action == "call_keys":
                        #     try:
                        #         call = CallLog.objects.get(pk=call_id)
                        #         if event_keys:
                        #             kk = event_keys.split(",")
                        #             if not kk:
                        #                 continue
                        #             for k in kk:
                        #                 if k:
                        #                     try:
                        #                         if is_new_call == "1":
                        #                             callkey = CallKey(call=call,keys=k)
                        #                             callkey.save()
                        #                         else:
                        #                             try:
                        #                                 callkey = CallKey.objects.get(call=call,keys=k)
                        #                             except:
                        #                                 callkey = CallKey(call=call,keys=k)
                        #                                 callkey.save()
                        #                         logger.info(f"{callkey.id} key : {k}")
                        #                     except:
                        #                         pass
                        #     except:
                        #         logger.error("callkey save error!!")

                        if event_action == "call_started":
                            try:
                                number = PhoneNumber.objects.get(pk=number_id)
                                number.attempt = number.attempt + 1
                                number.save()

                                call = CallLog.objects.get(pk=call_id)
                                call.status = CallStatus.ANSWERED
                                call.save()
                                # callkeys = CallKey.objects.filter(call=call)
                                # if callkeys:
                                #     for k in callkeys:
                                #         if is_new_call == "1":
                                #             k.delete()
                            except:
                                logger.exception("CallLog save error!!")

                        if event_action == "call_ended":
                            try:
                                call = CallLog.objects.get(pk=call_id)
                                call.status = CallStatus.PROCESSED
                                call.save()
                            except:
                                logger.error("CallLog save error!!")

                        if event_action == "silence_detected":
                            # print(e.serialize())
                            try:
                                key_parent = get_header(e, "key_parent")
                                key_level = get_header(e, "key_level")
                                call_keys = get_header(e, "param3")
                                call_menu_id = get_header(e, "call_menu_id")
                                record_uuid = get_header(e, "record_uuid")
                                record_uuid = "%s.wav" % record_uuid
                                audio_text = get_header(e, "audio_text")

                                callmenu = CallMenu(call_id=call_id, audio_file = record_uuid, audio_text = audio_text)
                                callmenu.save()
                                try:
                                    if event_keys:
                                        kk = event_keys.split(",")
                                        for k in kk:
                                            if k:
                                                try:
                                                    callkey = CallKey.objects.get(menu=callmenu,keys=k)
                                                except:
                                                    callkey = CallKey(menu=callmenu,keys=k)
                                                    callkey.save()
                                            logger.info(f"{callkey.id} key : {k}")
                                except Exception:
                                    logger.exception("callkey save error!!")

                                if key_parent:
                                    try:
                                        ck = CallKey.objects.get(pk=key_parent)
                                        ck.next = callmenu
                                        ck.save()
                                    except Exception:
                                        logger.exception("next menu save error")

                                logger.info("silence_detected")
                                ckeys = CallKey.objects.filter(menu=callmenu,processed=0).order_by('id')
                                if len(ckeys) > 0:
                                    ckey = ckeys[0]
                                    logger.info( f"sending DTMF [{ckey.keys}] to {call_id}, {call_uuid}")
                                    ckey.processed=1
                                    ckey.save()
                                    fs_send_dtmf(con, call_uuid, ckey.keys)
                                    fs_set_var(con, call_uuid,"key_level", int(key_level)+1)
                                    fs_set_var(con, call_uuid,"key_parent", ckey.id)
                            except Exception:
                                logger.exception("silence_detected: error!!!")
            else:
                if idle_count < 120:
                    idle_count = idle_count + 1

                if idle_count == 120:
                    django.db.close_old_connections()
                    logger.debug("closing db connection")
                    idle_count = 222

        else:
            logger.error("FreeSWITCH gone away. we are closing here")
            sys.exit(0)

except KeyboardInterrupt:

    logger.error("KeyboardInterrupt..Good bye")
    con.disconnect()
    sys.exit(0)

except SystemExit:

    logger.error("SystemExit..Good bye")
    con.disconnect()
    sys.exit(0)

except Exception:

    logger.exception("error found!!")
