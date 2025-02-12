--
-- Created by IntelliJ IDEA.
-- User: mohammad.kamruzzaman
-- Date: 18-06-2022
-- Time: 12:58 PM
--
require "app.phoneai.settings"
require "app.phoneai.macro"
require "app.phoneai.lib_events"
require "app.phoneai.utils"

local myjson = require "json"
local inspect = require "inspect"
local dbh = freeswitch.Dbh("pgsql://hostaddr=127.0.0.1 dbname=phoneai user=phoneai password='P0s@@w0123#' options='-c client_min_messages=NOTICE'")

--set default values
min_digits = 1;
max_digits = 8;
max_tries = 3;
max_timeouts = 3;
digit_timeout = 3000;
stream_seek = false;


assert(dbh:connected())

function check_carrier(number)
    session:execute("curl", "https://phoneai.boomslang.io/api/number/lookup/?number="..number:sub(-11))
    curl_response_code = session:getVariable("curl_response_code")
    curl_response      = session:getVariable("curl_response_data")
    freeswitch.consoleLog("INFO", inspect(curl_response_code))
    freeswitch.consoleLog("INFO", inspect(curl_response))
    if curl_response ~= nil then
        session:execute("set", "number_lookup="..curl_response)
    end
    if curl_response_code == 200 then
        return 1
    end
    return 0
end

function check_number(number, stir_shaken_verified)
    local check_url = "https://phoneai.boomslang.io/api/number/check/?number="..number:sub(-11)
    check_url = check_url .. "&stir_shaken="..stir_shaken_verified
    session:execute("curl", check_url)
    curl_response_code = session:getVariable("curl_response_code")
    curl_response      = session:getVariable("curl_response_data")
    freeswitch.consoleLog("INFO", inspect(curl_response_code))
    -- freeswitch.consoleLog("INFO", inspect(curl_response))
    if curl_response ~= nil then
        session:execute("set", "number_check="..curl_response)
    end
    if tonumber(curl_response_code) == 200 then
        local cdata = myjson.decode(curl_response);
        freeswitch.consoleLog("INFO", inspect(cdata))
        return cdata
    end
    return nil
end

function check_stir_shaken_verified(inp_str)
    result = string.find(inp_str, "verstat=TN%-Validation%-Passed")
    if result ~= nil then
        return 1
    end
    return 0
end
--define on_dtmf call back function
function on_dtmf(s, type, obj, arg)
    if (type == "dtmf") then
        freeswitch.consoleLog("debug", "[voicemail] dtmf digit: " .. obj['digit'] .. ", duration: " .. obj['duration'] .. "\n");
        if (obj['digit'] == "#") then
            return 0;
        else
            dtmf_digits = dtmf_digits .. obj['digit'];
            if (stream_seek == true) then
                if (dtmf_digits == "4") then
                    dtmf_digits = "";
                    return("seek:-12000");
                end
                if (dtmf_digits == "6") then
                    dtmf_digits = "";
                    return("seek:12000");
                end
            end
            if (string.len(dtmf_digits) >= max_digits) then
                return 0;
            end
        end
    end
    return 0;
end

local destination_number = session:getVariable("destination_number")
local caller_id_number = session:getVariable("caller_id_number")
local call_uuid = session:getVariable("uuid")
local force_captcha = session:getVariable("force_captcha")

-- track internal callmenu transfer call
--
if caller_id_number == DEFAULT_CALLERID then
    force_captcha = "true"
end

--[[
variable_sip_P-Asserted-Identity: [+17866648610;verstat=TN-Validation-Passed]
variable_sip_name_params: [verstat=TN-Validation-Passed]
variable_sip_h_P-Attestation-Indicator: [A]
]]
local sip_paid = session:getVariable("sip_P-Asserted-Identity")
freeswitch.consoleLog("ERR", inspect(sip_paid))
local sip_pai = session:getVariable("sip_h_P-Attestation-Indicator")
freeswitch.consoleLog("ERR", inspect(sip_pai))

callerid_verified = 0
caller_in_contact = 0
local stir_shaken_verified = check_stir_shaken_verified(sip_paid)

-- session:execute("info")
-- number check: carrier / spam check / others
local check_response = check_number(caller_id_number, stir_shaken_verified)
if check_response ~= nil then
    -- process response data
    if check_response['status'] == "success" then
        callerid_verified = 1
        caller_in_contact = tonumber(check_response['caller_in_contact'])
    end
end

session:execute("set", "caller_is_verified="..stir_shaken_verified)
session:execute("export", "caller_is_verified="..stir_shaken_verified)

local extension_id = 0
local sip_username = ""
local sip_domain = ""
local id_domain = 0
local extension_cellphone = ""
local transcription = 0
local conference_id = 0
local conference_pin = ""
-- This is the input callback used by dtmf or any other events
-- on this session such as ASR.
-- we are using detect_speech to capture watson transcription data
-- and this information pass to use through this callback
--
function onInput(s, type, obj)
    freeswitch.consoleLog("info", "Callback with type " .. type .. "\n");
    if (type == "dtmf") then
        freeswitch.consoleLog("info", "DTMF Digit: " .. obj.digit .. "\n");
    else if (type == "event") then
        local event = obj:getHeader("Speech-Type");
        if (event == "begin-speaking") then
            freeswitch.consoleLog("info", "\n" .. obj:serialize() .. "\n");
        end
        if (event == "detected-speech") then
            freeswitch.consoleLog("debug", "\n" .. obj:serialize() .. "\n");
            if (obj:getBody()) then
                session:execute("detect_speech", "resume");
                -- Parse the results from the event into the results table for later use.
                local xmlstr = obj:getBody();
                if xmlstr ~= nil then
                    speech = parse_watson_xmlstr(xmlstr);
                    if speech ~= "" then
                        freeswitch.consoleLog("err", "\n" .. speech .. "\n");
                        local evtdata = {};
                        evtdata["action"] = "transcription_speech";
                        evtdata['call_uuid'] = call_uuid;
                        evtdata['extension_id'] = extension_id;
                        evtdata['sip_username'] = sip_username;
                        evtdata['speech'] = speech;
                        mydtbd_send_event(evtdata);
                    end
                end
            end
        end
    end
    end
end

sql = "select fs_didnumber.phonenumber, fs_domain.id as id_domain, fs_domain.domain,fs_extension.sip_username"
sql = sql .. " , fs_didnumber.extension_id, fs_extension.cellphone, fs_extension.transcription "
sql = sql .. " , conference_room.pin as conference_pin, conference_room.id as conference_id "
sql = sql .. " from fs_didnumber left join fs_extension on fs_extension.id=fs_didnumber.extension_id"
sql = sql .. " join fs_users on fs_extension.user_id=fs_users.id "
sql = sql .. " join fs_domain on fs_domain.id=fs_users.domain_id"
sql = sql .. " left join conference_room on (conference_room.didnumber_id=fs_didnumber.id and conference_room.active=true)"
sql = sql .. " where right(fs_didnumber.phonenumber,10) = right('"..destination_number.."',10)"

freeswitch.consoleLog("INFO", sql)

dbh:query(sql, function(row)
    extension_id = tonumber(row['extension_id'])
    sip_username = row["sip_username"]
    sip_domain = row["domain"]
    id_domain = row["id_domain"]
    extension_cellphone = row["cellphone"]
    transcription = row["transcription"]
    if transcription ~= nil and transcription ~= "" and tonumber(transcription) ~= nil then
        transcription = tonumber(transcription)
    end
    if row["conference_pin"] ~= nil and row["conference_pin"] ~= "" then
        conference_pin = row["conference_pin"]
    end
    if row["conference_id"] ~= nil and tonumber(row["conference_id"]) ~= nil then
        conference_id = tonumber(row["conference_id"])
    end
end)

if extension_id > 0 then

    -- caller_in_contact = 0
    -- sql = "select phonebooks.name,contacts.phonenumber,fs_extension.sip_username  from contacts "
    -- sql = sql .. " join phonebooks on contacts.phonebook_id=phonebooks.id"
    -- sql = sql .. " join fs_extension on phonebooks.extension_id=fs_extension.id"
    -- sql = sql .. " where right(contacts.phonenumber,10) = right('"..caller_id_number.."',10)"
    -- dbh:query(sql, function(row)
    --     caller_in_contact = 1
    -- end)
    session:execute("set", "caller_in_contact="..caller_in_contact)
    session:execute("export", "caller_in_contact="..caller_in_contact)

    if force_captcha ~= nil or (caller_in_contact == 0 and callerid_verified == 0) then

        session:answer()
        session:execute("sleep", "1000")
        --set the callback function
        if (session:ready()) then
            session:setVariable("playback_terminators", "#")
            session:setInputCallback("on_dtmf", "")
        end

        -- captcha ivr
        dtmf_digits = '';
        math.randomseed(os.time())
        param = {}
        param.number1 = math.random(1, 5)
        param.number2 = math.random(1, 4)
        captcha_response = macro(session, "captcha_ivr", 1, 5000, param)
        freeswitch.consoleLog("INFO", captcha_response)
        if captcha_response ~= nil and captcha_response ~= "" and tonumber(captcha_response) ~= nil then
            if tonumber(captcha_response) ~= (param.number1 + param.number2) then
                session:hangup();
            else
                session:execute("set", "captcha_verified=1")
                local phonebook_id = 0;
                sql = "select phonebooks.id from phonebooks join fs_extension on phonebooks.extension_id=fs_extension.id"
                sql = sql .. " where phonebooks.extension_id="..extension_id;
                freeswitch.consoleLog("INFO", sql)
                dbh:query(sql, function(row)
                    phonebook_id = tonumber(row['id'])
                end)
                sql = "insert into contacts(phonenumber,active,source, phonebook_id) "
                sql = sql .. " values('"..caller_id_number.."', '1', 'captcha',"..phonebook_id..")"
                freeswitch.consoleLog("INFO", sql)
                local result = dbh:query(sql)
                freeswitch.consoleLog("INFO", inspect(result))
            end
        else
            session:hangup();
        end

    end

    session:setVariable("phoneai_direction", "inbound")
    session:execute("export", "phoneai_direction=inbound")
    session:setVariable("phoneai_destination", destination_number)
    session:setVariable("phoneai_source_number", caller_id_number)

    session:setVariable("phoneai_domain_id", id_domain)
    session:setVariable("phoneai_domain", sip_domain)
    session:setVariable("phoneai_extension_id", extension_id)
    session:setVariable("phoneai_username", sip_username)
    session:execute("export", "phoneai_domain_id="..id_domain)
    session:execute("export", "phoneai_domain="..sip_domain)
    session:execute("export", "phoneai_extension_id="..extension_id)
    session:execute("export", "phoneai_username="..sip_username)

    local recording_file = CALL_RECORDING_PATH.."domain_"..id_domain.."/"..extension_id.."_"..call_uuid..".mp3"
    local recording_url = "domain_"..id_domain.."/"..extension_id.."_"..call_uuid..".mp3"

    session:setVariable("phoneai_record_file",recording_url);
    session:execute("set","recording_follow_transfer=true");
    session:execute("export","RECORD_STEREO=true");
    session:execute("export","RECORD_APPEND=true");

    if extension_cellphone ~= nil then
        if caller_id_number:sub(-10) == extension_cellphone:sub(-10) then

            if conference_id > 0 then --conference call
                session:execute("conference", "conf_"..conference_id.."@default")
                session:hangup();
            end

            local bridge_number = ""
            local bridge_id = 0
            sql = "select id, didnumber, target_number from fs_bridge_call where right(didnumber,10)=right('"..destination_number.."', 10) "
            sql = sql .. " and current_timestamp < expired_at "
            sql = sql .. " and active=true "
            sql = sql .. " order by created_at desc  limit 1"
            dbh:query(sql, function(row)
                bridge_id = row["id"]
                bridge_number = row["target_number"]
            end)
            if bridge_number == "" then
                -- Call B type
                -- incoming call on your original number
                extension_cellphone = ""
                session:answer();
                session:execute("record_session", recording_file)
                session:execute("bind_digit_action", "my_digits,3,exec:lua,app/phoneai/xfer_ext.lua ${uuid} "..extension_id.." "..sip_username)
                if transcription == 1 then
                    session:setVariable("transcribed", "1")
                    session:setVariable("call_transcription", "1")
                    freeswitch.consoleLog("ERR", "transcription started")
                    session:setInputCallback("onInput", "")
                    session:execute("detect_speech", "unimrcp:watson {start-input-timers=false,smart_formatting=true,timestamps=true}builtin:speech/transcribe undefined");
                    local evtdata = {};
                    evtdata["action"] = "transcription_start";
                    evtdata['call_uuid'] = call_uuid;
                    evtdata['extension_id'] = extension_id;
                    evtdata['sip_username'] = sip_username;
                    mydtbd_send_event(evtdata);
                end
                local digits = session:getDigits(10, "#", 20000, 5000);
                session:consoleLog("info", "Got dtmf: ".. digits .."\n");
                if digits ~= nil and digits ~= "" and digits:len() == 10 then
                    extension_cellphone = "1"..digits
                    callerid_verified = 1
                end
                if extension_cellphone == "" then
                    while(session:ready()) do
                        session:sleep(500);
                    end
                    session:hangup();
                    return false;
                end
            else
                -- Call C type
                -- Outbound call
                callerid_verified = 1
                extension_cellphone = bridge_number
                sql = "update fs_bridge_call set active=false where id="..bridge_id
                local ret = dbh:query(sql)
                freeswitch.consoleLog("debug", inspect(ret))
            end
        end
    end

    if force_captcha ~= nil or callerid_verified == 0 then
        -- captcha IVR
        caller_in_contact = 0
        sql = "select phonebooks.name,contacts.phonenumber,fs_extension.sip_username  from contacts "
        sql = sql .. " join phonebooks on contacts.phonebook_id=phonebooks.id"
        sql = sql .. " join fs_extension on phonebooks.extension_id=fs_extension.id"
        sql = sql .. " where right(contacts.phonenumber,10) = right('"..caller_id_number.."',10)"
        dbh:query(sql, function(row)
            caller_in_contact = 1
        end)
        session:execute("set", "caller_in_contact="..caller_in_contact)
        session:execute("export", "caller_in_contact="..caller_in_contact)

        if force_captcha ~= nil or caller_in_contact == 0 then

            session:answer()
            session:execute("sleep", "1000")
            --set the callback function
            if (session:ready()) then
                session:setVariable("playback_terminators", "#")
                session:setInputCallback("on_dtmf", "")
            end

            -- captcha ivr
            dtmf_digits = '';
            math.randomseed(os.time())
            param = {}
            param.number1 = math.random(1, 5)
            param.number2 = math.random(1, 4)
            captcha_response = macro(session, "captcha_ivr", 1, 5000, param)
            freeswitch.consoleLog("INFO", captcha_response)
            if captcha_response ~= nil and captcha_response ~= "" and tonumber(captcha_response) ~= nil then
                if tonumber(captcha_response) ~= (param.number1 + param.number2) then
                    session:hangup();
                else
                    local phonebook_id = 0;
                    sql = "select phonebooks.id from phonebooks join fs_extension on phonebooks.extension_id=fs_extension.id"
                    sql = sql .. " where phonebooks.extension_id="..extension_id;
                    freeswitch.consoleLog("INFO", sql)
                    dbh:query(sql, function(row)
                        phonebook_id = tonumber(row['id'])
                    end)
                    sql = "insert into contacts(phonenumber,active,source, phonebook_id) "
                    sql = sql .. " values('"..caller_id_number.."', '1', 'captcha',"..phonebook_id..")"
                    freeswitch.consoleLog("INFO", sql)
                    local result = dbh:query(sql)
                    freeswitch.consoleLog("INFO", inspect(result))
                end
            else
                session:hangup();
            end

        end
    end
    session:execute("set","profile=s3")
    session:execute("set","RECORD_STEREO=true");
    session:execute("set","api_on_answer=uuid_record "..call_uuid.." start "..recording_file)

    if conference_id > 0 then --conference call
        session:execute("conference", "conf_"..conference_id.."@default+"..conference_pin)
        session:hangup();
    end
    -- origination_param = "{phoneai_direction=inbound,phoneai_source_number"..caller_id_number.."}"
    if session:ready() then
        if extension_cellphone ~= "" then
            session:execute("set", "effective_caller_id_name=${outbound_caller_id_name}")
            session:execute("set", "effective_caller_id_number=${outbound_caller_id_number}")
            session:execute("set", "hangup_after_bridge=true")
            session:execute("set", "ignore_display_updates=true")
            session:execute("bridge", "sofia/gateway/58e29eb4-bc1e-4c3d-bf30-25ff961b1b99/69485048*"..extension_cellphone)
        else
            session:execute("bridge", "user/"..sip_username.."@"..sip_domain)
        end
    end
end

session:hangup()
