import imp
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator, IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
from ibm_watson import SpeechToTextV1
import json
import os
from utils import findKeys
from phoneai_api import settings

def log(msg):
    print(msg)

class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):

        # print(json.dumps(data, indent=2))
        # print(json.dumps(data["results"]))
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
                                    speech = ''
                                    speech_stop = 0
                                else:
                                    speech = "%s %s" %(speech,part[0])
                                    speech_stop = part[2]
                        print(speech)
                    else:
                        print(parts['transcript'])

    def on_error(self, error):
        log('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        log('Inactivity timeout: {}'.format(error))

    # def on_transcription(self, transcript):
    #     log("transcript:")
    #     log(transcript)

    def on_connected(self):
        log('Connection was successful')

    def on_listening(self):
        log('Service is listening')

    def on_hypothesis(self, hypothesis):
        log(hypothesis)

def test_process():
    vm_file = "/var/lib/freeswitch/recordings/usermedia/3cd3ff62-874a-11ec-97f3-a593d3cd889e.wav"

    try:
        authenticator = IAMAuthenticator(settings.ibm_apikey)
        speech_to_text = SpeechToTextV1(
            authenticator=authenticator
        )

        url = "%s/v1/recognize?model=en-US_NarrowbandModel&smart_formatting=true&timestamps=true" % settings.ibm_url
        speech_to_text.set_service_url(url)

        # speech_to_text.set_disable_ssl_verification(True)

        myRecognizeCallback = MyRecognizeCallback()

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


# test_process()
from worker.tasks import process_menu_audio

data = {}
data['RecordingFile'] = '/var/lib/freeswitch/recordings/usermedia/3cd3ff62-874a-11ec-97f3-a593d3cd889e.wav'

process_menu_audio.delay(data)
