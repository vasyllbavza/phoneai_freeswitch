import logging
from celery import Celery
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator, IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
from ibm_watson import SpeechToTextV1

from os.path import join, dirname
import json
import datetime
from word2number import w2n

import settings

app = Celery('tasks', backend=None)
app.conf.broker_url = settings.REDIS_BROKER

logging.basicConfig(filename='/var/log/transcribe.log', level=logging.INFO)
logger = logging.getLogger()

from api.models import (
    PhoneNumber,
    CallLog,
    CallMenu,
    CallKey,
    CallStatus
)

@app.task
def add(x, y):
    return x + y


def log(msg, level="INFO"):

    dt = "%sZ" % datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    print("%s voicemail: %s : %s" % (dt, level, msg))
    logger.info("%s :: %s"%(dt,msg))

def isNumber(str):    
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

class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def set_data(self, vm_data):
        self.vm_data = vm_data
        self.menu_data = []

    def on_data(self, data):

        log(json.dumps(data))
        for result in data["results"]:
            if result['final']:
                # print(result['alternatives'])
                for parts in result['alternatives']:
                    # print(parts)
                    keys = findKeys(parts['transcript'])
                    if len(keys) > 1:
                        # print(parts['timestamps'])
                        speech = ''
                        speech_stop  = 0
                        for part in parts['timestamps']:
                            # print(part)
                            if speech_stop == 0:
                                speech = part[0]
                                speech_stop = part[2]
                            else:
                                if part[1] > speech_stop:
                                    print(speech)
                                    ck = findKeys(speech)
                                    if len(ck) == 1:
                                        submenu_info = {}
                                        submenu_info['key'] = ck[0]
                                        submenu_info['text'] = speech
                                        self.menu_data.append(submenu_info)
                                    speech = ''
                                    speech_stop = 0
                                else:
                                    speech = "%s %s" %(speech,part[0])
                                    speech_stop = part[2]
                        print(speech)
                        if len(speech) > 0:
                            ck = findKeys(speech)
                            if len(ck) == 1:
                                submenu_info = {}
                                submenu_info['key'] = ck[0]
                                submenu_info['text'] = speech
                                self.menu_data.append(submenu_info)

                    else:
                        print(parts['transcript'])
                        if len(keys) == 1:
                            submenu_info = {}
                            submenu_info['key'] = keys[0]
                            submenu_info['text'] = parts['transcript']
                            self.menu_data.append(submenu_info)
        log(json.dumps(self.menu_data))
        for mdata in self.menu_data:
            key = CallKey.objects.filter(menu_id=self.vm_data["menu_id"], keys=mdata["key"]).first()
            if key:
                ck = CallKey.objects.get(pk=key.id)
                ck.audio_text = mdata["text"]
                ck.save()

    def on_error(self, error):
        log('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        log('Inactivity timeout: {}'.format(error))

    def on_transcription(self, transcript):
        log("transcript:")
        log(transcript)

    def on_connected(self):
        log('Connection was successful')

    def on_listening(self):
        log('Service is listening')

    def on_hypothesis(self, hypothesis):
        log(hypothesis)


@ app.task
def process_menu_audio(vm_data):

    vm_file = vm_data["RecordingFile"]
    log(vm_data)

    try:
        authenticator = IAMAuthenticator(settings.ibm_apikey)
        speech_to_text = SpeechToTextV1(
            authenticator=authenticator
        )

        url = "%s/v1/recognize?model=en-US_NarrowbandModel&smart_formatting=true&timestamps=true" % settings.ibm_url
        speech_to_text.set_service_url(url)

        # speech_to_text.set_disable_ssl_verification(True)

        myRecognizeCallback = MyRecognizeCallback()
        myRecognizeCallback.set_data(vm_data)

        with open(vm_file,
                    'rb') as audio_file:
            audio_source = AudioSource(audio_file)
            result = speech_to_text.recognize_using_websocket(
                audio=audio_source,
                recognize_callback=myRecognizeCallback,
                content_type='audio/wav',
                model='en-US_BroadbandModel',
                timestamps=True,
                smart_formatting=True,
                max_alternatives=1)
            log("finished transcription")
    except ApiException as ex:
        log("Method failed with status code % s: % s" %
            (str(ex.code), ex.message))
