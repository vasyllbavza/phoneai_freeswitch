webhook_url = "https://webhook.site/9525bf64-a5de-46f9-b3a4-18b9a025f8d5"

api = freeswitch.API();

local xml2lua = require("xml2lua")
local handler = require("xmlhandler.tree")
local domHandler = require("xmlhandler/dom")
local myjson = require "json";
require "lib_events";

-- URL ENCOCDE DECODE Library
local char_to_hex = function(c)
    return string.format("%%%02X", string.byte(c))
  end
  
  local function urlencode(url)
    if url == nil then
      return
    end
    url = url:gsub("\n", "\r\n")
    url = url:gsub("([^%w ])", char_to_hex)
    url = url:gsub(" ", "+")
    return url
  end
  
  local hex_to_char = function(x)
    return string.char(tonumber(x, 16))
  end
  
  local urldecode = function(url)
    if url == nil then
      return
    end
    url = url:gsub("+", " ")
    url = url:gsub("%%(%x%x)", hex_to_char)
    return url
  end

-- END
dtmf_input = "";
ivr_menu_digit_len = "10";
recordfile = "/usr/share/freeswitch/scripts/recorded_audio.wav";
sound = "/usr/share/freeswitch/sounds/silence_10m.wav";
results = "";
confidenceRef = 0.01;

phoneai_call_id = session:getVariable("phoneai_call_id");
uuid = session:getVariable("uuid");
destination_number = session:getVariable("destination_number");
if destination_number == nil then destination_number = ""; end

local evtdata = {};
evtdata["action"] = "call_started";
evtdata['call_id'] = phoneai_call_id;
evtdata['call_uuid'] = uuid;
mydtbd_send_event(evtdata);

speaking_start = 0;
speech_found = "";

key_level  = 0;
key_parent = 0;
session:setVariable("key_level", key_level);
session:setVariable("key_parent", key_parent);

--ASR Stuff
-- Used in parse_xml
function parseargs_xml(s)
    local arg = {}
    string.gsub(s, "(%w+)=([\"'])(.-)%2", function (w, _, a)
                        arg[w] = a
                     end)
    return arg
end

-- Turns XML into a lua table.
function parse_xml(s)
    local stack = {};
    local top = {};
    table.insert(stack, top);
    local ni,c,label,xarg, empty;
    local i, j = 1, 1;
    while true do
        ni,j,c,label,xarg, empty = string.find(s, "<(%/?)(%w+)(.-)(%/?)>", i);
        if not ni then
            break
        end
        
        local text = string.sub(s, i, ni-1);
        if not string.find(text, "^%s*$") then
             table.insert(top, text);
        end
        
        if empty == "/" then
            table.insert(top, {label=label, xarg=parseargs_xml(xarg), empty=1});
        elseif c == "" then
            top = {label=label, xarg=parseargs_xml(xarg)};
            table.insert(stack, top);
        elseif label == "input" then
            local toclose = table.remove(stack);
            top = stack[#stack];
            if #stack < 1 then
                error("nothing to close with "..label);
            end
            if toclose.label ~= label then
                error("trying to close "..toclose.label.." with "..label);
            end
            table.insert(stack, toclose);
        else

        end
        
        i = j+1;
    end
    
    local text = string.sub(s, i);
    if not string.find(text, "^%s*$") then
      table.insert(stack[stack.n], text);
    end
    return stack;
end
-- Used to parse the XML results.
function getResults(s) 
    local xml = parse_xml(s);
    --freeswitch.consoleLog("notice", "[asr] xml:" .. json.encode(xml) .. "\n");
    local stack = {}
    local top = {}
    table.insert(stack, top)
    top = {grammar=xml[2].xarg.grammar, score=xml[3].xarg.confidence, text=xml[4][1]}
    table.insert(stack, top)
    return top;
end
function parse_xmlstr(speechStr)
    local confidenceVal = string.match(speechStr, "<interpretation .* confidence=\"(%d+)\">");
    if confidenceVal ~= nil or confidenceVal ~= "" then
        confidenceVal = tonumber(confidenceVal)
    else
        confidenceVal = 0
    end
    local speech = string.match(speechStr, "<interpretation .*>(.*)</input>");
    if speech == nil then
        speech = "";
    end
    speech = speech:lower();

    if confidenceVal >= confidenceRef then
        speechOut = speech;
        return speech
    else
          return ""
    end
end
function parse_watson_xmlstr(speechStr)
    confidenceVal = string.match(speechStr, "<interpretation .* confidence=\"(%d+.%d+)\">");
    if confidenceVal ~= nil or confidenceVal ~= "" then
        confidenceVal = tonumber(confidenceVal)
    else
        confidenceVal = 0
    end
    speech = string.match(speechStr, "<interpretation .*>(.*)</input>");
    if speech == nil then
        speech = "";
    end
    speech = speech:lower();

    if confidenceVal >= confidenceRef then
        speechOut = speech;
        return speech
    else
          return ""
    end
end
function upload_webhook(msg,keys)

    msg = urlencode(msg);
    local data = '{"apitoken":"phoneai","destination_number":"'..destination_number..'","transcription":"'..msg..'","keys":"'..keys..'"}';
    local apiparam = webhook_url.." content-type 'application/json'  ";
    apiparam = apiparam .. ' connect-timeout 1 timeout 2 ';
    apiparam = apiparam .. ' post ';
    apiparam = apiparam .. data;

    local response = api:execute("curl", apiparam);
    response = response:gsub("\\/","/");
    local cdata = myjson.decode(response);
    return cdata;

end

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
    ["zero"] = "0"
}

key_collected = "";

function key_check(speech)

    local key_collected = "";
    for k,v in pairs(results_map) do
        if speech:match(k) or speech:match(v) then
            key_collected = key_collected..v..",";
        end
    end
    return key_collected
end

function send_dtmf(number)

    local words = {}
    for w in number:gmatch("%w+") do
        table.insert(words, w) 
        freeswitch.consoleLog("ERR", w)
        for k,v in pairs(results_map) do
            if k == w then
                cmd = "uuid_send_dtmf "..uuid.." "..v;
                api:executeString(cmd);
                break;
            end
        end
    end

end
function send_dtmf_single(digit)
    cmd = "uuid_send_dtmf "..uuid.." "..digit;
    api:executeString(cmd);
end

-- This is the input callback used by dtmf or any other events on this session such as ASR.
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
            -- Return break on begin-speaking events to stop playback of the fire or tts.
            --return "break";
            speaking_start = os.time();
            freeswitch.consoleLog("ERR", "\nspeaking_start = " .. speaking_start .. "\n");
        end
        if (event == "detected-speech") then
            freeswitch.consoleLog("debug", "\n" .. obj:serialize() .. "\n");
            if (obj:getBody()) then
               -- Pause speech detection (this is on auto but pausing it just in case)
               session:execute("detect_speech", "resume");
               -- Parse the results from the event into the results table for later use.
               local xmlstr = obj:getBody();
            --    results = getResults(xmlstr);
            --    speech = parse_xmlstr(xmlstr);
               speech = parse_watson_xmlstr(xmlstr);
               speech_found = speech_found .. " "..speech;
               freeswitch.consoleLog("ERR", "\n" .. speech .. "\n");               
               freeswitch.consoleLog("ERR", "\n" .. speech_found .. "\n");
               new_key = key_check(speech);
               key_collected = key_collected..new_key;
               freeswitch.consoleLog("ERR", "\n" .. key_collected .. "\n");
               speaking_start = os.time();
               upload_webhook(speech_found,key_collected);
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

               mydtbd_send_event(evtdata);
            --    send_dtmf(speech);
            end
            -- return "break";
        end
    end
    end
end


if (session:ready()) then
    session:answer();
    
    session:execute("record_session",recordfile);
    call_start_epoch = os.time();

    session:setInputCallback("onInput");
    -- Sleep a little bit to give media time to be fully up.
    session:sleep(200);
    -- session:execute("detect_speech", "pocketsphinx pai_number undefined");
    session:execute("detect_speech", "unimrcp:watson {start-input-timers=false}builtin:speech/transcribe undefined");
    -- session:streamFile(sound);
    while session:ready() do
        session:sleep(1000);
        if speaking_start > 0 then
            wait_time = os.time() - speaking_start;
            freeswitch.consoleLog("ERR", "wait_time = " .. wait_time .."\n");
            if wait_time > 5 then
                local evtdata = {};
                evtdata["action"] = "silence_detected";
                evtdata['keys'] = key_collected;
                evtdata['call_id'] = phoneai_call_id;
                evtdata['call_uuid'] = uuid;
                evtdata["param1"] = "phoneAI";
                evtdata["param2"] = destination_number;
                evtdata["param3"] = key_collected;
                evtdata["param4"] = speech_found;
                evtdata["key_level"] = session:getVariable("key_level");
                evtdata["key_parent"] = session:getVariable("key_parent");
                mydtbd_send_event(evtdata);
                wait_time = 0;
                speaking_start = 0;
                speech_found = "";
            end
        end
    end
    -- session:execute("play_and_detect_speech",sound.." detect:unimrcp:watson {start-input-timers=false}builtin:speech/transcribe");
    local xml = session:getVariable('detect_speech_result')
    if xml ~= nil then
            speechStr = xml;
            freeswitch.consoleLog("INFO", speechStr .."\n")
    end

    local evtdata = {};
    evtdata["action"] = "call_ended";
    evtdata['call_id'] = phoneai_call_id;
    evtdata['call_uuid'] = uuid;
    mydtbd_send_event(evtdata);

end