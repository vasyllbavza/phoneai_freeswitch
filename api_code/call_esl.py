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
from tasks import process_menu_audio

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
    logger.info(args)
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

def isNumber(str):
    from word2number import w2n
    try:
        return w2n.word_to_num(str)
    except:
        return False

def findKeys(audio_text):
    from urllib.parse import unquote
    audio_text = unquote(audio_text)
    audio_text = audio_text.strip()
    ret = [isNumber(s) for s in audio_text.split() if isNumber(s)]
    return ret

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

    con.events('plain', 'HEARTBEAT TALK NOTALK DETECTED_SPEECH CUSTOM mydtbd::info')

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
                # logger.debug(f"{event_name} {event_time}")
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

                if event_name == "DETECTED_SPEECH":
                    print(e.serialize())
                if event_name == "TALK":
                    print(e.serialize())
                if event_name == "NOTALK":
                    print(e.serialize())

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
                        call_menu_id = get_header(e, "call_menu_id")
                        is_new_call = get_header(e,"is_new_call")
                        logger.info(f"{event_action} {call_id}")
                        # debug
                        # call_id = 1
                        # number_id = 4
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
                            # print(e.serialize())
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
                                if call_menu_id:
                                    if call_menu_id == "0":
                                        menu = CallMenu(call=call)
                                        menu.save()
                                        fs_set_var(con, call_uuid,"call_menu_id", menu.id)
                                        logger.info(f"new menu started.")
                                        fs_set_var(con, call_uuid,"current_menu_id", menu.id)
                                    else:
                                        dtmf = ""
                                        cm = CallMenu.objects.get(pk=call_menu_id)
                                        firstmenu = CallMenu.objects.filter(call__number__id=cm.call.number.id).first()
                                        fs_set_var(con, call_uuid,"current_menu_id", firstmenu.id)
                                        loop_count = 1
                                        while firstmenu.id != call_menu_id and loop_count < 10:
                                            ck = CallKey.objects.filter(next__id=call_menu_id).first()
                                            if ck:
                                                if dtmf == "":
                                                    dtmf += '%s' % ck.keys
                                                else:
                                                    dtmf += '%s' % ck.keys
                                                call_menu_id = ck.menu.id
                                            loop_count = loop_count + 1

                                        fs_set_var(con, call_uuid,"key_travel", dtmf)
                                        dtmf = ""
                                        ck_next = CallKey.objects.filter(next__isnull=True,menu=cm).first()
                                        if ck_next:
                                            dtmf = ck_next.keys
                                        fs_set_var(con, call_uuid,"key_target", dtmf)

                                        # cm_new = CallMenu(call_id=call_id, audio_file = "", audio_text = "")
                                        # cm_new.save()
                                        # ck_next.next = cm_new
                                        # ck_next.save()
                                        # fs_set_var(con, call_uuid,"call_menu_id", cm_new.id)
                                        # logger.info(f"new menu [{cm_new.id}] started. ")
                                        # logger.info(f"sending dtmf {dtmf}")
                                        # fs_send_dtmf(con, call_uuid, dtmf)

                            except:
                                logger.exception("CallLog save error!!")

                        if event_action == "go_call_started":
                            try:
                                number = PhoneNumber.objects.get(pk=number_id)
                                call = CallLog.objects.get(pk=call_id)
                                if call_menu_id:
                                    dtmf = ""
                                    cm = CallMenu.objects.get(pk=call_menu_id)
                                    firstmenu = CallMenu.objects.filter(call__number__id=cm.call.number.id).first()
                                    fs_set_var(con, call_uuid,"current_menu_id", firstmenu.id)
                                    loop_count = 1
                                    while firstmenu.id != call_menu_id and loop_count < 10:
                                        ck = CallKey.objects.filter(next__id=call_menu_id).first()
                                        if ck:
                                            if dtmf == "":
                                                dtmf += '%s' % ck.keys
                                            else:
                                                dtmf += '%s' % ck.keys
                                            call_menu_id = ck.menu.id
                                        loop_count = loop_count + 1

                                    fs_set_var(con, call_uuid,"key_travel", dtmf)
                                    dtmf = ""
                                    ck_next = CallKey.objects.filter(next__isnull=True,menu=cm).first()
                                    if ck_next:
                                        dtmf = ck_next.keys
                                    fs_set_var(con, call_uuid,"key_target", dtmf)
                            except:
                                logger.exception("CallLog save error!!")

                        if event_action == "key_pressed":
                            call_menu_id = get_header(e, "call_menu_id")
                            current_menu_id = get_header(e, "current_menu_id")
                            # event_keys, call_uuid
                            try:
                                ck = CallKey.objects.get(menu__id=current_menu_id, keys=event_keys)
                                if ck.next:
                                    current_menu_id = ck.next.id
                                else:
                                    menu = CallMenu(call_id=call_id)
                                    menu.save()
                                    current_menu_id = menu.id
                            except:
                                pass
                            fs_set_var(con, call_uuid,"current_menu_id", current_menu_id)

                        if event_action == "call_ended":
                            print(e.serialize())
                            record_uuid = get_header(e, "record_uuid")
                            record_uuid = "%s.wav" % record_uuid
                            audio_text = get_header(e, "audio_text")

                            force_hangup = get_header(e, "force_hangup")

                            logger.info( f"{record_uuid} {audio_text}" )

                            if audio_text != "":
                                if call_menu_id and call_menu_id != "" and call_menu_id != "0":
                                    callmenu = CallMenu.objects.get(pk=call_menu_id)
                                    callmenu.audio_file = record_uuid
                                    callmenu.audio_text = audio_text
                                    callmenu.save()
                                else:
                                    callmenu = CallMenu(call_id=call_id, audio_file = record_uuid, audio_text = audio_text)
                                    callmenu.save()
                                if force_hangup and force_hangup == "1":
                                    callmenu.completed = True
                                    callmenu.save()
                                else:
                                    try:
                                        if audio_text and audio_text != "":
                                            kk = findKeys(audio_text)
                                            if len(kk) == 0:
                                                callmenu.completed = True
                                                callmenu.save()
                                    except:
                                        pass
                            try:
                                call = CallLog.objects.get(pk=call_id)
                                call.status = CallStatus.PROCESSED
                                call.save()

                                # if force_hangup and force_hangup == "1":
                                #     call.number.completed = True
                                #     call.number.save()

                                # find if number have completed all menu/submenu
                                pending_menu = CallMenu.objects.filter(call=call, completed=False).first()
                                if pending_menu:
                                    logger.info("need to crawl more")
                                else:
                                    call.number.completed = True
                                    call.number.save()

                            except:
                                logger.error("CallLog save error!!")


                        if event_action == "silence_detected":
                            # print(e.serialize())
                            try:
                                key_parent = get_header(e, "key_parent")
                                key_level = get_header(e, "key_level")
                                call_keys = get_header(e, "param3")
                                record_uuid = get_header(e, "record_uuid")
                                record_uuid = "%s.wav" % record_uuid
                                audio_text = get_header(e, "audio_text")
                                key_collected = get_header(e, "key_collected")
                                if call_menu_id:
                                    callmenu = CallMenu.objects.get(pk=call_menu_id)
                                    callmenu.audio_file = record_uuid
                                    callmenu.audio_text = audio_text
                                    callmenu.save()
                                else:
                                    callmenu = CallMenu(call_id=call_id, audio_file = record_uuid, audio_text = audio_text)
                                    callmenu.save()
                                try:
                                    if event_keys:
                                        # kk = event_keys.split(",")
                                        kk = findKeys(audio_text)
                                        for k in kk:
                                            if k:
                                                try:
                                                    callkey = CallKey.objects.get(menu=callmenu,keys=k)
                                                except:
                                                    callkey = CallKey(menu=callmenu,keys=k)
                                                    callkey.save()
                                            logger.info(f"{callkey.id} key : {k}")
                                        vm_data = {}
                                        vm_data["RecordingFile"] = "/var/lib/freeswitch/recordings/usermedia/%s" % record_uuid
                                        vm_data["menu_id"] = callmenu.id
                                        process_menu_audio.delay(vm_data)
                                except Exception:
                                    logger.exception("callkey save error!!")

                                # if key_parent and key_parent != "0":
                                #     try:
                                #         ck = CallKey.objects.get(pk=key_parent)
                                #         ck.next = callmenu
                                #         ck.save()
                                #     except Exception:
                                #         logger.exception("next menu save error")
                                # else:
                                #     logger.info("key_parent is missing")

                                logger.info("silence_detected")
                                if key_collected == "0":
                                    logger.info("no key collected. wait for next")
                                    continue

                                ckeys = CallKey.objects.filter(menu=callmenu,next__isnull=True).order_by('id')
                                if len(ckeys) > 0:
                                    ckey = ckeys[0]
                                    logger.info( f"sending DTMF [{ckey.keys}] to {call_id}, {call_uuid}")
                                    ckey.processed=1
                                    ckey.save()

                                    menu = CallMenu(call_id=call_id)
                                    menu.save()
                                    call_menu_id = menu.id

                                    ckey.next = menu
                                    ckey.save()

                                    if len(ckeys) == 1:
                                        callmenu.completed = True
                                        callmenu.save()

                                    fs_set_var(con, call_uuid, "call_menu_id", call_menu_id)

                                    fs_send_dtmf(con, call_uuid, ckey.keys)
                                    fs_set_var(con, call_uuid, "key_level", int(key_level)+1)
                                    fs_set_var(con, call_uuid, "key_parent", ckey.id)
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
