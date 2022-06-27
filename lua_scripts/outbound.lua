require "app.phoneai.settings"
local inspect = require "inspect"

local sip_authorized = session:getVariable("sip_authorized")
local destination_number = session:getVariable("caller_destination")
local caller_id_number = session:getVariable("caller_id_number")
local call_uuid = session:getVariable("uuid")

local domain_name = session:getVariable("phoneai_domain")
local domain_id = session:getVariable("phoneai_domain_id")
local sip_username = session:getVariable("phoneai_username")
local extension_id = session:getVariable("phoneai_extension_id")

session:execute("info")

local dbh = freeswitch.Dbh(PGSQL_DSN)

local phonebook_id = 0;

sql = "select phonebooks.id from phonebooks join fs_extension on phonebooks.extension_id=fs_extension.id"
sql = sql .. " where phonebooks.extension_id="..extension_id;

freeswitch.consoleLog("INFO", sql)
dbh:query(sql, function(row)
    phonebook_id = tonumber(row['id'])
end)

sql = "insert into contacts(phonenumber,active,source, phonebook_id) "
sql = sql .. " values('"..destination_number.."', '1', 'outbound',"..phonebook_id..")"

freeswitch.consoleLog("INFO", sql)

local result = dbh:query(sql)
freeswitch.consoleLog("INFO", inspect(result))
