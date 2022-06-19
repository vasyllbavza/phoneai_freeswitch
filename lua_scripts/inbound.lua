--
-- Created by IntelliJ IDEA.
-- User: mohammad.kamruzzaman
-- Date: 18-06-2022
-- Time: 12:58 PM
--
require "app.phoneai.settings"

local inspect = require "inspect"
local dbh = freeswitch.Dbh("pgsql://hostaddr=127.0.0.1 dbname=phoneai user=phoneai password='P0s@@w0123#' options='-c client_min_messages=NOTICE'")

assert(dbh:connected())

local destination_number = session:getVariable("destination_number")
local caller_id_number = session:getVariable("caller_id_number")
local call_uuid = session:getVariable("uuid")

local extension_id = 0
local sip_username = ""
local sip_domain = ""
local id_domain = 0

sql = "select fs_didnumber.phonenumber, fs_domain.id as id_domain, fs_domain.domain,fs_extension.sip_username, fs_didnumber.extension_id"
sql = sql .. " from fs_didnumber left join fs_extension on fs_extension.id=fs_didnumber.extension_id"
sql = sql .. " join fs_users on fs_extension.user_id=fs_users.id "
sql = sql .. " join fs_domain on fs_domain.id=fs_users.domain_id"
sql = sql .. " where left(fs_didnumber.phonenumber,11) = left('"..destination_number.."',11)"

freeswitch.consoleLog("INFO", sql)

dbh:query(sql, function(row)
    extension_id = tonumber(row['extension_id'])
    sip_username = row["sip_username"]
    sip_domain = row["domain"]
    id_domain = row["id_domain"]
end)

if extension_id > 0 then

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
