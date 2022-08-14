
require "app.phoneai.settings"
require "app.phoneai.macro"
require "app.phoneai.lib_events"
require "app.phoneai.utils"
local inspect = require "inspect"

--Init debug and fs_env
local debug_mode = false
local fs_env = true

freeswitch.consoleLog("INFO",inspect(argv))
session:execute("info")
call_uuid = argv[1]
extension_id = argv[2]
sip_username = argv[3]

-- api = freeswitch.API()
local evtdata = {}

local call_transcription = session:getVariable("call_transcription")
local last_matching_digits = session:getVariable("last_matching_digits")
freeswitch.consoleLog("INFO",inspect(call_transcription))
if call_transcription == nil then
    freeswitch.consoleLog("ERR", "transcription started")
    session:setVariable("call_transcription", "1")
    session:setInputCallback("onInput", "")
    session:execute("detect_speech", "unimrcp:watson {start-input-timers=false,smart_formatting=true,timestamps=true}builtin:speech/transcribe undefined");
    evtdata["action"] = "transcription_start"
    evtdata['call_uuid'] = call_uuid
    evtdata['extension_id'] = extension_id
    evtdata['sip_username'] = sip_username
    mydtbd_send_event(evtdata);    
else
    session:execute("detect_speech", "stop")
    session:execute("unset", "call_transcription")
    freeswitch.consoleLog("ERR", "transcription stopped")
    evtdata["action"] = "transcription_stop"
    evtdata['call_uuid'] = call_uuid;
    evtdata['extension_id'] = extension_id;
    evtdata['sip_username'] = sip_username;
    mydtbd_send_event(evtdata);    
end

