
api = freeswitch.API();

myjson = require "json";
require "app.phoneai.lib_events";
require "app.phoneai.utils";

--variables
--
caller_id = '13013019105'

dtmf_input = "";
ivr_menu_digit_len = "10";
recordfile = "/usr/share/freeswitch/scripts/recorded_audio.wav";
sound = "/usr/share/freeswitch/sounds/silence_10m.wav";
results = "";
confidenceRef = 0.01;


record_uuid = api:execute("create_uuid","");
record_base = "/var/lib/freeswitch/recordings/usermedia/";
recordfile = record_base..record_uuid..".wav";
masterfile = record_base.."master.wav";

wait_time_missed = 0;

--collect parameter that passed from api request
phoneai_number_id = session:getVariable("phoneai_number_id");
phoneai_call_id = session:getVariable("phoneai_call_id");
is_new_call = session:getVariable("is_new_call");
uuid = session:getVariable("uuid");
destination_number = session:getVariable("destination_number");
if destination_number == nil then destination_number = ""; end

call_menu_id = session:getVariable("call_menu_id");
freeswitch.consoleLog("info", "call_menu_id = " .. call_menu_id .. "\n");

forwarding_number = session:getVariable("forwarding_number");
agentcall_id = session:getVariable("agentcall_id");

--event data object
local evtdata = {};
evtdata["action"] = "go_call_started";
evtdata['number_id'] = phoneai_number_id;
evtdata['call_id'] = phoneai_call_id;
evtdata['call_uuid'] = uuid;
evtdata['call_menu_id'] = call_menu_id;
evtdata['is_new_call'] = is_new_call;
evtdata['agentcall_id'] = agentcall_id;

mydtbd_send_event(evtdata);

speaking_start = 0;
speech_found = "";

key_level  = 0;
key_parent = 0;
session:setVariable("key_level", key_level);
session:setVariable("key_parent", key_parent);

session:setVariable("key_travel", "");
session:setVariable("key_target", "");
session:setVariable("current_menu_id", "");

-- variables
menu_ready_for_input = 0;

results_map = {
    ["one"] = "1",
    ["two"] = "2",
    ["three"] = "3",
    ["four"] = "4",
    ["five"] = "5",
    ["six"] = "6",
    ["seven"] = "7",
    ["eight"] = "8",
    ["nine"] = "9",
    ["zero"] = "0",
    ["pound"] = "#"
}

key_collected = "";

key_travel = "#";
key_pos = 1;
-- functions

-- key_travel: we need to press this dtmf to reach our desired menu
-- we need to check if we are ready to press that or not
-- we will check this with key_collected channel variables
--
function dtmf_to_press(key_collected)
    if key_travel ~= nil then
        len = key_travel:len()
        if len > 0 then
            key = key_travel:sub(len,len+1)
            if key_collected:find(key) ~= nil then
                return key
            end
        end
    end
    return nil
end
-- after execute/press dtmf, we will remove that 
-- from key_travel channel variable
--
function update_key_travel()
    len = key_travel:len()
    if len > 1 then
        key_travel = key_travel:sub(1, len-1)
    else
        key_travel = ""
    end
    session:setVariable("key_travel", key_travel);
    return key_travel
end
function key_check(speech)

    local key_collected = "";
    for k,v in pairs(results_map) do
        if speech:match(k) or speech:match(v) then
            key_collected = key_collected..v..",";
        end
    end
    return key_collected
end

-- This is the input callback used by dtmf or any other events
-- on this session such as ASR.
-- we are using detect_speech to capture watson transcription data
-- and this information pass to use through this callback
--
function onInput(s, type, obj)
    freeswitch.consoleLog("info", "Callback with type " .. type .. "\n");

    if (type == "dtmf") then
        freeswitch.consoleLog("info", "DTMF Digit: " .. obj.digit .. "\n");
        if (dtmf_input ~= nil) then
              dtmf_input = dtmf_input .. obj.digit;
        else
            session:execute("detect_speech", "pause");
            dtmf_input = obj.digit;
              return "break";
        end
        if (#dtmf_input == tonumber(ivr_menu_digit_len)) then
            return "break";
        end

    else if (type == "event") then
        local event = obj:getHeader("Speech-Type");

        if (event == "begin-speaking") then
            freeswitch.consoleLog("info", "\n" .. obj:serialize() .. "\n");
            speaking_start = os.time();
            freeswitch.consoleLog("ERR", "\nspeaking_start = " .. speaking_start .. "\n");
        end

        if (event == "detected-speech") then
            freeswitch.consoleLog("debug", "\n" .. obj:serialize() .. "\n");
            if (obj:getBody()) then
                session:execute("detect_speech", "resume");
                -- Parse the results from the event into the results table for later use.
                local xmlstr = obj:getBody();
                if xmlstr ~= nil then
                    speech = parse_watson_xmlstr(xmlstr);
                    speech_found = speech_found .. " "..speech;
                    freeswitch.consoleLog("ERR", "\n" .. speech .. "\n");               
                    freeswitch.consoleLog("ERR", "\n" .. speech_found .. "\n");
                    new_key = key_check(speech);
                    key_collected = key_collected..new_key;
                    if new_key ~= "" then menu_ready_for_input = 1; end
                    freeswitch.consoleLog("ERR", "\n" .. key_collected .. "\n");
                    speaking_start = os.time();
                    --    upload_webhook(speech_found,key_collected);
                    local evtdata = {};
                    evtdata["action"] = "call_keys";
                    evtdata['keys'] = new_key;
                    evtdata['call_id'] = phoneai_call_id;
                    evtdata['call_uuid'] = uuid;
                    evtdata["param1"] = "phoneAI";
                    evtdata["param2"] = destination_number;
                    evtdata["param3"] = key_collected;
                    evtdata["param4"] = speech_found;
                    evtdata["key_level"] = key_level;
                    evtdata["key_parent"] = key_parent;
                    evtdata['is_new_call'] = is_new_call;

                    evtdata['call_menu_id'] = call_menu_id;
                    evtdata['record_uuid'] = record_uuid;

                    --initial event trigger for event handler [call_esl.py]
                    if new_key ~= nil and new_key ~= "" then
                        mydtbd_send_event(evtdata);
                    end
                end
            end
        end
    end
    end
end

-- call answer and wait for watson to send capture data
--
if (session:ready()) then
    session:answer();

    session:execute("record_session",masterfile);
    -- session:execute("record_session","shout://source:h@ck1me@phoneai.boomslang.io:8000/master");
    session:execute("record_session",recordfile);
    call_start_epoch = os.time();

    session:setInputCallback("onInput");
    session:sleep(200);
    -- session:execute("detect_speech", "pocketsphinx pai_number undefined");
    session:execute("detect_speech", "unimrcp:watson {start-input-timers=false}builtin:speech/transcribe undefined");
    -- session:streamFile(sound);
    force_hangup = 0;

    idle_start_time = os.time();
    while session:ready() and force_hangup==0 do
        session:sleep(1000);
        key_travel = session:getVariable("key_travel");
        if key_travel == nil then key_travel = ""; end
        key_target = session:getVariable("key_target");
        if key_target == nil then key_target = ""; end
        current_menu_id = session:getVariable("current_menu_id");
        if current_menu_id == nil then current_menu_id = ""; end
        freeswitch.consoleLog("ERR", "key_travel = " .. key_travel .."\n");
        freeswitch.consoleLog("ERR", "key_target = " .. key_target .."\n");
        call_menu_id = session:getVariable("call_menu_id");
        if call_menu_id == nil then call_menu_id = ""; end
        freeswitch.consoleLog("ERR", "current_menu_id = " .. current_menu_id ..", call_menu_id = " .. call_menu_id .."\n");

        local key_to_send = dtmf_to_press(key_collected);
        if key_to_send ~= nil then
            session:execute("send_dtmf",key_to_send);
            local key_rem = update_key_travel();

            --event data object
            local evtdata = {};
            evtdata["action"] = "key_pressed";
            evtdata['number_id'] = phoneai_number_id;
            evtdata['call_id'] = phoneai_call_id;
            evtdata['call_uuid'] = uuid;
            evtdata['call_menu_id'] = call_menu_id;
            evtdata['current_menu_id'] = current_menu_id;
            evtdata['keys'] = key_to_send;
            evtdata['agentcall_id'] = agentcall_id;
            mydtbd_send_event(evtdata);
            --end

            wait_time_missed = 0;
            menu_ready_for_input = 0;
            idle_start_time = os.time();
            wait_time = 0;
            speaking_start = 0;
            speech_found = "";
            key_collected = "";
            if key_rem == "" then
                -- going to transfer this calls to forwarding number
                freeswitch.consoleLog("ERR", "transfer calls to agent with forwading number = " .. forwarding_number .."\n");
                dialstring = "{ignore_early_media=true,origination_caller_id_number="..caller_id.."}"
                if forwarding_number:len() < 7 then
                    dialstring = dialstring.."user/"..forwarding_number;
                else
                    dialstring = dialstring.."sofia/gateway/58e29eb4-bc1e-4c3d-bf30-25ff961b1b99/69485048*"..forwarding_number;
                end
                freeswitch.consoleLog("ERR", "dialstring = " .. dialstring .."\n");
                session:execute("set","hangup_after_bridge=true");
                session:execute("bridge", dialstring);
                session:hangup();
            end
            goto continue
        end
        if speaking_start > 0 then
            wait_time = os.time() - speaking_start;
            freeswitch.consoleLog("ERR", "wait_time = " .. wait_time .."\n");
            if wait_time > 5 and menu_ready_for_input == 1 then
                local evtdata = {};
                evtdata["action"] = "silence_detected";
                evtdata["keys"] = key_collected;
                evtdata["call_id"] = phoneai_call_id;
                evtdata["call_uuid"] = uuid;
                evtdata["param1"] = "phoneAI";
                evtdata["param2"] = destination_number;
                evtdata["param3"] = key_collected;
                evtdata["param4"] = speech_found;
                key_level = session:getVariable("key_level");
                evtdata["key_level"] = key_level;
                key_parent = session:getVariable("key_parent");
                evtdata["key_parent"] = key_parent;
                call_menu_id = session:getVariable("call_menu_id");
                evtdata["call_menu_id"] = call_menu_id;
                evtdata["is_new_call"] = is_new_call;

                if key_collected ~= "" then
                    freeswitch.consoleLog("info", "silence_detected event triggering.\n");
                    evtdata["key_collected"] = "1";
                    evtdata["audio_text"] = speech_found;
                    evtdata["record_uuid"] = record_uuid;
                    session:execute("stop_record_session",recordfile);
                    record_uuid = api:execute("create_uuid","");
                    recordfile = record_base..record_uuid..".wav";
                    session:execute("record_session",recordfile);

                    -- send silence detected event to [call_esl.py]
                    -- which will initiate dtmf witH ESL interface
                    -- mydtbd_send_event(evtdata);
                    wait_time_missed = 0;
                    menu_ready_for_input = 0;
                    idle_start_time = os.time();
                else
                    evtdata["key_collected"] = "0";
                    evtdata["audio_text"] = speech_found;
                    -- mydtbd_send_event(evtdata);
                    freeswitch.consoleLog("ERR", "silence_detected with no key collected\n");
                    wait_time_missed = wait_time_missed + 1;
                    freeswitch.consoleLog("INFO", "wait_time_missed= "..wait_time_missed.."\n");
                    if wait_time_missed > 10 then
                        force_hangup = 1;
                        freeswitch.consoleLog("INFO", "clean up call.\n");
                    end
                end
                wait_time = 0;
                speaking_start = 0;
                speech_found = "";
                key_collected = "";
            else
                if wait_time > 30 then
                    force_hangup = 1;
                    freeswitch.consoleLog("INFO", "clean up call.\n");
                end    
            end
        else
            no_audio_wait_time = os.time() - idle_start_time;
            freeswitch.consoleLog("ERR", "no_audio_wait_time = " .. no_audio_wait_time .."\n");
            if no_audio_wait_time > 30 then
                force_hangup = 1;
                freeswitch.consoleLog("INFO", "clean up call.\n");
            end
        end
        ::continue::
    end
    local xml = session:getVariable('detect_speech_result')
    if xml ~= nil then
            speechStr = xml;
            freeswitch.consoleLog("INFO", speechStr .."\n")
    end

    local evtdata = {};
    evtdata["action"] = "go_call_ended";
    evtdata['call_id'] = phoneai_call_id;
    evtdata['call_uuid'] = uuid;
    evtdata["call_menu_id"] = call_menu_id;
    evtdata["audio_text"] = speech_found;
    evtdata["record_uuid"] = record_uuid;
    evtdata["key_level"] = key_level;
    evtdata["force_hangup"] = force_hangup
    evtdata['agentcall_id'] = agentcall_id;
    mydtbd_send_event(evtdata);
    session:hangup();
end