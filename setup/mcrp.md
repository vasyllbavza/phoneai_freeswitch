## ubuntu/debian package
```
apt-get update
apt-get install gnupg2

echo "deb [arch=amd64] https://unimrcp.org/repo/apt/ bionic main" > /etc/apt/sources.list.d/unimrcp.list

nano /etc/apt/auth.conf.d/unimrcp.conf
```
machine unimrcp.org
login romonzamanbd
password Test!1234
```

wget -O - https://unimrcp.org/keys/unimrcp-gpg-key.public | sudo apt-key add -
apt-get update

apt-get install unimrcp-client
apt-get install unimrcp-server
apt-get install unimrcp-demo-plugins

systemctl status unimrcp.service
systemctl enable unimrcp.service

apt-get install unimrcp-watson-sr
apt-get install umc-addons


cd ~
/opt/unimrcp/bin/unilicnodegen
# send this generated file to provider for license generation for us



##### File Directory

root@mrcp:/opt/unimrcp# ls
bin  conf  data  lib  log  plugin  record  var

root@mrcp:/opt/unimrcp# ls bin/
asrclient  umc  unilicnodegen  unimrcpclient  unimrcpserver

root@mrcp:/opt/unimrcp# ls conf/
client-profiles  logfile.xml  umc-scenarios    umswatsonsr.xml.orig  unimrcpclient.xml  unimrcpserver.xml
dirlayout.xml    logger.xml   umswatsonsr.xml  umswatsonsr.xml.save  unimrcpclient.xsd  unimrcpserver.xsd

root@mrcp:/opt/unimrcp# ls data/
bookhotel.pcm  demo-16kHz.pcm  grammar.mixed  johnsmith-16kHz.pcm  one-8kHz.pcm             speak.txt            speechgenderid.txt    umswatsonsr_124ca579-ce36-489d-ac94-037b8af2a8bc.lic
bookroom.pcm   demo-8kHz.pcm   grammar.srgs   johnsmith-8kHz.pcm   params_default.txt       speak.xml            speechlanguageid.txt  umswatsonsr_51f2b701-771f-47f3-962c-9cd9ff6d3fb9.lic
callsteve.pcm  dial5.pcm       grammar.xml    makereservation.pcm  result-verification.xml  speechcontext.xml    speechtelephony.txt   watsonsr.credentials
command.jsgf   grammar.jsgf    jgrammar.list  one-16kHz.pcm        result.xml               speechemotionid.txt  speechtranscribe.txt  whatstheweatherlike.pcm

root@mrcp:/opt/unimrcp# ls lib/
libapr-1.so.0          libasrclient.so.0      libevent_core-2.1.so.6       libevent_openssl-2.1.so.6       libsofia-sip-ua.so.0       libunimrcpserver.so.0
libapr-1.so.0.5.2      libasrclient.so.0.7.0  libevent_core-2.1.so.6.0.2   libevent_openssl-2.1.so.6.0.2   libsofia-sip-ua.so.0.6.0   libunimrcpserver.so.0.7.0
libaprutil-1.so.0      libevent-2.1.so.6      libevent_extra-2.1.so.6      libevent_pthreads-2.1.so.6      libunimrcpclient.so.0
libaprutil-1.so.0.5.4  libevent-2.1.so.6.0.2  libevent_extra-2.1.so.6.0.2  libevent_pthreads-2.1.so.6.0.2  libunimrcpclient.so.0.7.0

root@mrcp:/opt/unimrcp# ls log/
unimrcpserver_2020.10.22_19.37.18.359662.log  unimrcpserver_current.log

root@mrcp:/opt/unimrcp# ls record/
rdr_0026ab70d5b3417f-1.json  rdr_30a975755f514c33-1.json  rdr_612a832e2d27417b-1.json  rdr_8c3c11bda80d4f54-1.json   rdr_b1c975bb12eb43d3-1.json   rdr_dc0afd14daf1448e-1.json

root@mrcp:/opt/unimrcp# ls var
status  synth-8kHz-4c8b77c89cf4432e.pcm


### configuration : server

/opt/unimrcp/conf/unimrcpserver.xml
```xml
    <!-- Factory of plugins (MRCP engines) -->
    <plugin-factory>
      <engine id="Demo-Synth-1" name="demosynth" enable="true"/>
      <engine id="Demo-Recog-1" name="demorecog" enable="false"/>
      <engine id="Demo-Verifier-1" name="demoverifier" enable="true"/>
      <engine id="Recorder-1" name="mrcprecorder" enable="true"/>
      <engine id="Watson-SR-1" name="umswatsonsr" enable="true"/>
```

/opt/unimrcp/conf/umswatsonsr.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<umswatsonsr license-file="umswatsonsr_*.lic" credentials-file="watsonsr.credentials">

   <license-server
      enable="false"
      server-address="127.0.0.1"
      certificate-file="unilic_client_*.crt"
      ca-file="unilic_ca.crt"
   />

   <ws-streaming-recognition
      language="en-US"
      language-customization-id=""
      acoustic-customization-id=""
      base-model-version=""
      grammar-name=""
      single-utterance="false"
      max-alternatives="1"
      alternatives-below-threshold="false"
      confidence-format="auto"
      smart-formatting="true"
      word-confidence="false"
      timestamps="false"
      speaker-labels="false"
      redaction="false"
      processing-metrics="false"
      audio-metrics="false"
      end-of-phrase-silence-time="1"
      start-of-input="service-originated"
      skip-unsupported-grammars="true"
      transcription-grammar="transcribe"
      auth-validation-period="0"
      inter-result-timeout="2000"
   />

   <speech-contexts>
      <speech-context id="boolean" language="en-US" speech-complete="true" scope="strict" enable="false">
         <phrase tag="true">yes</phrase>
         <phrase tag="true">sure</phrase>
         <phrase tag="true">correct</phrase>
         <phrase tag="false">no</phrase>
         <phrase tag="false">not sure</phrase>
         <phrase tag="false">incorrect</phrase>
      </speech-context>
   </speech-contexts>

   <speech-dtmf-input-detector
      vad-mode="2"
      speech-start-timeout="300"
      speech-complete-timeout="1000"
      speech-incomplete-timeout="15000"
      noinput-timeout="5000"
      input-timeout="30000"
      dtmf-interdigit-timeout="5000"
      dtmf-term-timeout="10000"
      dtmf-term-char=""
      speech-leading-silence="300"
      speech-trailing-silence="300"
      speech-output-period="200"
   />

   <utterance-manager
      save-waveforms="false"
      purge-existing="false"
      max-file-age="60"
      max-file-count="100"
      waveform-base-uri="http://localhost/utterances/"
      waveform-folder=""
      use-logging-tag="false"
   />

   <rdr-manager
      save-records="true"
      purge-existing="false"
      max-file-age="0"
      max-file-count="100"
      record-folder="/opt/unimrcp/record/"
      file-prefix="rdr_"
      use-logging-tag="false"
   />

   <monitoring-agent refresh-period="60">
      <usage-change-handler>
         <log-usage enable="true" priority="NOTICE"/>
         <update-usage enable="false" status-file="umswatsonsr-usage.status"/>
         <dump-channels enable="false" status-file="umswatsonsr-channels.status"/>
      </usage-change-handler>

      <usage-refresh-handler>
         <log-usage enable="false" priority="NOTICE"/>
         <update-usage enable="false" status-file="umswatsonsr-usage.status"/>
         <dump-channels enable="false" status-file="umswatsonsr-channels.status"/>
      </usage-refresh-handler>
   </monitoring-agent>

</umswatsonsr>

```

/opt/unimrcp/data/watsonsr.credentials
```json
{
  "apikey": "9CnAWKPkTMRPXdIiMN6Ux-MtDTBfnsE74Fmjx5USPVib",
  "iam_apikey_de  scription": "Auto-generated for key 48aeaa6b-e93e-4f27-9787-ce61197b8445",
  "iam_apikey_name": "Auto-generated service credentials",
  "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Manager",
  "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/ca5b50d4b638439d8b8491db6062eb8b::serviceid:ServiceId-26f6a42e-58a4-40a8-a6d5-4f9dfc6cf23b",
  "url": "https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/20f792a3-0551-4067-ac67-910475a3e02f"
}
```

copy licensence to /opt/unimrcp/data/

cd /opt/unimrcp/bin
sudo ./unimrcpserver

tail -f /opt/unimrcp/log/unimrcpserver_current.log

#### FreSWITCH configuration
apt-get install freeswitch-mod-unimrcp
make mod_mrcp-install

/etc/freeswitch/autoload_configs/unimrcp.conf.xml
```xml
<configuration name="unimrcp.conf" description="UniMRCP Client">
  <settings>
    <!-- UniMRCP profile to use for TTS -->
    <param name="default-tts-profile" value="voxeo-prophecy8.0-mrcp1"/>
    <!-- UniMRCP profile to use for ASR -->
    <param name="default-asr-profile" value="watson"/>
    <!-- UniMRCP logging level to appear in freeswitch.log.  Options are:
         EMERGENCY|ALERT|CRITICAL|ERROR|WARNING|NOTICE|INFO|DEBUG -->
    <param name="log-level" value="DEBUG"/>
    <!-- Enable events for profile creation, open, and close -->
    <param name="enable-profile-events" value="false"/>

    <param name="max-connection-count" value="100"/>
    <param name="offer-new-connection" value="1"/>
    <param name="request-timeout" value="3000"/>
  </settings>

  <profiles>
    <X-PRE-PROCESS cmd="include" data="../mrcp_profiles/*.xml"/>
  </profiles>

</configuration>
```

nano /etc/freeswitch/mrcp_profiles/watson.xml
```xml
<include>
<profile name="watson" version="2">
  <param name="client-ip" value="162.0.220.158"/>
  <param name="client-port" value="16090"/>
  <param name="server-ip" value="162.0.220.158"/>
  <param name="server-port" value="8060"/>
  <!--param name="force-destination" value="1"/-->
  <param name="sip-transport" value="udp"/>
  <!--param name="ua-name" value="lawhq"/-->
  <!--param name="sdp-origin" value="lawhq"/-->
  <!--param name="rtp-ext-ip" value="auto"/-->
  <param name="rtp-ip" value="auto"/>
  <param name="rtp-port-min" value="14000"/>
  <param name="rtp-port-max" value="15000"/>
  <!-- enable/disable rtcp support -->
  <param name="rtcp" value="0"/>
  <!-- rtcp bye policies (rtcp must be enabled first)
    0 - disable rtcp bye
    1 - send rtcp bye at the end of session
    2 - send rtcp bye also at the end of each talkspurt (input)
  -->
  <param name="rtcp-bye" value="2"/>
  <!-- rtcp transmission interval in msec (set 0 to disable) -->
  <param name="rtcp-tx-interval" value="5000"/>
  <!-- period (timeout) to check for new rtcp messages in msec (set 0 to disable) -->
  <param name="rtcp-rx-resolution" value="1000"/>
  <!--param name="playout-delay" value="50"/>
  <param name="max-playout-delay" value="200"/>
  <param name="ptime" value="20"/-->
  <param name="codecs" value="PCMU PCMA L16/96/8000"/>

  <!-- Add any default MRCP params for SPEAK requests here -->
  <synthparams>
  </synthparams>

  <!-- Add any default MRCP params for RECOGNIZE requests here -->
  <recogparams>
    <!--param name="start-input-timers" value="false"/-->
  </recogparams>

</profile>
</include>
```