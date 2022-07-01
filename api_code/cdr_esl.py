import os
import sys
import signal
import datetime
import json
import django.db
import urllib
import logging
import xmltodict
import pickle

from django.core.handlers.wsgi import WSGIHandler
from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phoneai_api.settings")
application = get_wsgi_application()


try:
    from freeswitchESL import ESL
except ImportError:
    ESL = None
    print("ESL")


logging.basicConfig(
    filename='cdr_esl.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-6s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

cdr_type_xml = False


def signal_term_handler(signal, frame):

    print >>sys.stderr, 'got SIGTERM'
    logger.error('got SIGTERM')
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_term_handler)


def json_outp(jsondata):

    data = json.dumps(jsondata, indent=4, sort_keys=True)
    logger.info(data)


def get_header(event, header_name):
    try:
        hdr = event.getHeader(header_name)
        if hdr:
            return hdr
        else:
            return ""
    except:
        return ""


def get_cdr_variable(file, var, type):
    result = ""
    try:
        result = urllib.unquote(file['cdr']['variables'][var])
    except:
        if type == 'string':
            result = ""
        elif type == 'float':
            result = 0.00
        elif type == 'int':
            result = 0
        else:
            result = type

    return result


def get_event_variable(event, var, type):
    result = ""
    try:
        result = get_header(event, "variable_%s" % var)
        if type == 'string':
            return result 
        elif type == 'float':
            return float(result)
        elif type == 'int':
            return int(result)
        else:
            return result

    except:
        if type == 'string':
            result = ""
        elif type == 'float':
            result = 0.00
        elif type == 'int':
            result = 0
        else:
            result = type

    return result


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


def save_cdr_local(cdrdata):
    from sipuser.models import FsCDR, Domain, Extension, FsDidNumber
    logger.info("Saving CDR..")
    # cdr = pickle.loads(cdrdata)
    # log_error(cdr)
    cdrlog = FsCDR(call_uuid=cdrdata['call_uuid'])
    cdrlog.domain_name = cdrdata['domain']
    try:
        domain = Domain.objects.get(pk=cdrdata['domain_id'])
        cdrlog.domain = domain
    except:
        pass
    cdrlog.bill_duration = cdrdata["bill_duration"]
    cdrlog.call_direction = cdrdata["call_direction"]
    cdrlog.started_at = cdrdata["started_at"]
    cdrlog.call_from = cdrdata["call_from"]
    cdrlog.call_to = cdrdata["call_to"]
    try:
        cdrlog.extension = Extension.objects.get(pk=cdrdata["phoneai_extension_id"])
    except:
        pass
    if cdrlog.call_direction == "inbound":
        try:
            cdrlog.didnumber = FsDidNumber.objects.get(phonenumber=cdrdata["phoneai_destination"])
        except:
            pass
    cdrlog.recording_file = cdrdata["phoneai_record_file"]
    cdrlog.hangup_cause = cdrdata["hangup_cause"]

    cdrlog.is_verified = cdrdata["caller_is_verified"]
    cdrlog.in_contact = cdrdata["caller_in_contact"]

    # cdrlog.read_codec = cdr['read_codec']
    # cdrlog.write_codec = cdr['write_codec']
    # if cdr['mango_record_seconds'] > 0:
    #     cdrlog.mango_record_file = cdr['mango_record_file']

    cdrlog.save()
    logger.info("Saving CDR.. DONE.")


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

    con.events('plain', 'HEARTBEAT CHANNEL_HANGUP_COMPLETE')

    idle_count = 0
    hb_count = 0
    while 1:
        if con.connected():
            try:
                e = con.recvEventTimed(2000)
            except Exception:
                logger.exception("Exception occured")
                exit(0)

            if e:
                event_name = get_header(e, "Event-Name")
                domain_name = get_header(e, "variable_domain_uuid")
                switchname = get_header(e, "FreeSWITCH-Switchname")

                event_time = "%sZ" % datetime.datetime.utcnow().replace(microsecond=0).isoformat()
                myDate = datetime.datetime.now()
                if event_name == "HEARTBEAT":
                    event_info = get_header(e, "Event-Info")
                    up_time = get_header(e, "Up-Time")
                    callinfo = {}
                    callinfo['up_time'] = up_time
                    callinfo['event_info'] = event_info
                    callinfo['switchname'] = switchname
                    callinfo['event'] = event_name
                    callinfo['message'] = event_info
                    key = "system.heartbeat.message"
                    data = json.dumps(callinfo)

                if event_name == "CHANNEL_HANGUP_COMPLETE":
                    print(e.serialize())
                    cdrBody = e.getBody()
                    cdr = {}

                    # fields
                    # variable_direction: inbound,
                    # variable_sip_from_user: c3e8f51b-6920-41d1-8d40-0a64be348445
                    # variable_sip_from_host: d0c20d13-e5b4-4649-821e-9ab8ec94b141
                    # variable_sip_auth_username: c3e8f51b-6920-41d1-8d40-0a64be348445
                    # variable_sip_auth_realm: d0c20d13-e5b4-4649-821e-9ab8ec94b141
                    # variable_domain_name: d0c20d13-e5b4-4649-821e-9ab8ec94b141
                    # variable_process_cdr: false
                    # variable_fs_server: dev2a.mangovoice.com
                    # variable_voicemail_action: check
                    # variable_voicemail_id: c3e8f51b-6920-41d1-8d40-0a64be348445
                    # variable_voicemail_profile: default
                    # variable_voicemail_domain: d0c20d13-e5b4-4649-821e-9ab8ec94b141
                    # variable_timezone: Asia/Dhaka
                    # variable_duration: 2
                    # variable_billsec: 2

                    # fields
                    # uuid,sip_from_user,sip_from_host,sip_network_ip
                    # sip_number_alias,sip_auth_username,sip_auth_realm,number_alias,domain_uuid,extension_uuid,user_context
                    # effective_caller_id_name,effective_caller_id_number,user_name,domain_name

                    # firstheader = e.serialize()
                    # data = dict(cdr=e.getBody())
                    # obj = xmltodict.parse(data['cdr'])
                    # cdr['call_uuid'] = get_cdr_variable(obj, "uuid", "string")

                    # cdr['domain'] = get_cdr_variable(obj, "phoneai_domain", "string")
                    # cdr['domain_id'] = get_cdr_variable(obj, "phoneai_domain_id", "string")
                    # cdr['username'] = get_cdr_variable(obj, "phoneai_username", "string")
                    # cdr['phoneai_record_file'] = get_cdr_variable(obj, "phoneai_record_file", "string")
                    # cdr['phoneai_extension_id'] = get_cdr_variable(obj, "phoneai_extension_id", "string")

                    # cdr['call_direction'] = get_cdr_variable(obj, "phoneai_direction", "string")
                    # cdr['phoneai_destination'] = get_cdr_variable(obj, "phoneai_destination", "string")
                    # cdr['phoneai_source_number'] = get_cdr_variable(obj, "phoneai_source_number", "string")

                    # cdr['bill_duration'] = get_cdr_variable(obj, "duration", "string")
                    # cdr['started_at'] = get_cdr_variable(obj, "start_stamp", "string")

                    # cdr['call_from'] = get_cdr_variable(obj, "caller_destination", "string")
                    # cdr['call_to'] = get_cdr_variable(obj, "caller_id_number", "string")

                    # cdr['leg'] = 'A'

                    # cdr['read_codec'] = get_cdr_variable(obj, "read_codec", "string")
                    # cdr['write_codec'] = get_cdr_variable(obj, "write_codec", "string")

                    cdr['call_uuid'] = get_event_variable(e, "uuid", "string")

                    cdr['domain'] = get_event_variable(e, "phoneai_domain", "string")
                    cdr['domain_id'] = get_event_variable(e, "phoneai_domain_id", "string")
                    cdr['username'] = get_event_variable(e, "phoneai_username", "string")
                    cdr['phoneai_record_file'] = get_event_variable(e, "phoneai_record_file", "string")
                    cdr['phoneai_extension_id'] = get_event_variable(e, "phoneai_extension_id", "string")

                    cdr['call_direction'] = get_event_variable(e, "phoneai_direction", "string")
                    if cdr['call_direction'] == "":
                        cdr['call_direction'] = "outbound"
                    cdr['phoneai_destination'] = get_event_variable(e, "phoneai_destination", "string")
                    cdr['phoneai_source_number'] = get_event_variable(e, "phoneai_source_number", "string")

                    cdr['bill_duration'] = get_event_variable(e, "duration", "string")
                    cdr['started_at'] = get_event_variable(e, "start_stamp", "string")

                    cdr['call_to'] = get_event_variable(e, "caller_destination", "string")
                    cdr['call_from'] = get_event_variable(e, "caller_id_number", "string")

                    cdr['caller_is_verified'] = get_event_variable(e, "caller_is_verified", "int")
                    cdr['caller_in_contact'] = get_event_variable(e, "caller_in_contact", "int")

                    cdr['leg'] = 'A'
                    try:
                        other_type = get_header(e, "Other-Type")
                        if other_type == "originator":
                            cdr['leg'] = 'B'
                    except:
                        pass
                    cdr['read_codec'] = get_event_variable(e, "read_codec", "string")
                    cdr['write_codec'] = get_event_variable(e, "write_codec", "string")

                    try:
                        cdr['hangup_cause'] = e.getHeader("variable_hangup_cause")
                    except:
                        cdr['hangup_cause'] = ""

                    try:
                        cdr['bill_duration'] = e.getHeader("variable_billsec")
                    except:
                        pass

                    try:
                        cdr['call_origin'] = e.getHeader("variable_call_origin")
                        if e.getHeader("variable_call_origin") == "did":
                            call_type = "inbound"
                            cdr['call_direction'] = "inbound"
                    except:
                        cdr['call_direction'] = e.getHeader("variable_call_direction")

                    try:
                        number_lookup = get_event_variable(e, "number_lookup", "string")
                        number_data = json.loads(number_lookup)
                        cdr['caller_type'] = number_data['type']
                        cdr['caller_carrier'] = number_data['carrier']
                    except:
                        pass
                    try:
                        if cdr['leg'] == 'A':
                            print(cdr)
                            save_cdr_local(cdr)
                    except Exception as err:
                        logger.error(err)

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
