--
-- Created by IntelliJ IDEA.
-- User: mohammad.kamruzzaman
-- Date: 18-06-2022
-- Time: 12:58 PM
--
require "app.phoneai.settings"
require "app.phoneai.macro"

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
    if curl_response_code == 200 then
        return 1
    end
    return 0
end

function check_cid_verified(inp_str)
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

-- session:execute("info")

callerid_verified = 0
if check_carrier(caller_id_number) == 1 then
    if check_cid_verified(sip_paid) == 1 then
        callerid_verified = 1
    end
end
session:execute("set", "caller_is_verified="..callerid_verified)
session:execute("export", "caller_is_verified="..callerid_verified)

local extension_id = 0
local sip_username = ""
local sip_domain = ""
local id_domain = 0

sql = "select fs_didnumber.phonenumber, fs_domain.id as id_domain, fs_domain.domain,fs_extension.sip_username, fs_didnumber.extension_id"
sql = sql .. " from fs_didnumber left join fs_extension on fs_extension.id=fs_didnumber.extension_id"
sql = sql .. " join fs_users on fs_extension.user_id=fs_users.id "
sql = sql .. " join fs_domain on fs_domain.id=fs_users.domain_id"
sql = sql .. " where right(fs_didnumber.phonenumber,10) = right('"..destination_number.."',10)"

freeswitch.consoleLog("INFO", sql)

dbh:query(sql, function(row)
    extension_id = tonumber(row['extension_id'])
    sip_username = row["sip_username"]
    sip_domain = row["domain"]
    id_domain = row["id_domain"]
end)

if extension_id > 0 then

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

    session:execute("set","profile=s3")
    session:execute("set","RECORD_STEREO=true");
    session:execute("set","api_on_answer=uuid_record "..call_uuid.." start "..recording_file)
    -- origination_param = "{phoneai_direction=inbound,phoneai_source_number"..caller_id_number.."}"
    session:execute("bridge", "user/"..sip_username.."@"..sip_domain)

end

session:hangup()
