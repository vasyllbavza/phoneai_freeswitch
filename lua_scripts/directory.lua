--
-- Created by IntelliJ IDEA.
-- User: mohammad.kamruzzaman
-- Date: 16-06-2022
-- Time: 12:58 PM
--
require "app.phoneai.settings"

local inspect = require "inspect"
local dbh = freeswitch.Dbh("pgsql://hostaddr=127.0.0.1 dbname=phoneai user=phoneai password='P0s@@w0123#' options='-c client_min_messages=NOTICE'")

assert(dbh:connected())

sql = "select fs_extension.id, fs_extension.sip_username, fs_extension.sip_password, fs_domain.domain, fs_domain.id as id_domain,"
sql = sql .." coalesce(fs_didnumber.phonenumber,'') as caller_id_number"
sql = sql .." from fs_extension join fs_users on fs_users.id=fs_extension.user_id "
sql = sql .." join fs_domain on fs_domain.id=fs_users.domain_id"
sql = sql .." left join fs_didnumber on extension_id=fs_extension.id"

local req_domain = params:getHeader("domain")
local req_key    = params:getHeader("key")
local req_user   = params:getHeader("user")
if req_domain == nil then req_domain = "" end
if req_user == nil then req_user = "" end
if req_key == nil then req_key = "" end

--get the action
action = params:getHeader("action");
purpose = params:getHeader("purpose");
profile = params:getHeader("profile");
remote_ip = params:getHeader("ip");
if remote_ip == nil then
    remote_ip = '';
end
if action == nil then
    action = ""
end
if purpose == nil then
    purpose = ""
end

--determine the correction action to perform
if (purpose == "gateways") then
elseif (action == "message-count") then
    --    debugger:msg("DEBUG","directory -" .. action );
elseif (action == "group_call") then
    --    debugger:msg("DEBUG","directory -" .. purpose );
elseif (action == "reverse-auth-lookup") then
    --    debugger:msg("DEBUG","directory -" .. purpose );
elseif (params:getHeader("Event-Calling-Function") == "switch_xml_locate_domain") then
    --    debugger:msg("DEBUG","directory -" .. purpose );
elseif (params:getHeader("Event-Calling-Function") == "populate_database") then
    --    debugger:msg("DEBUG","directory -" .. purpose );
else

--build the xml
local xml = {}
table.insert(xml, [[<?xml version="1.0" encoding="UTF-8" standalone="no"?>]]);
table.insert(xml, [[<document type="freeswitch/xml">]]);
table.insert(xml, [[	<section name="directory">]]);
table.insert(xml, [[		<domain name="]] .. req_domain .. [[" alias="true">]]);


dbh:query(sql, function(row)

    freeswitch.consoleLog("INFO", inspect(row))
    user_domain = row["domain"]
    user_domain_id = row["id_domain"]
    user_sipname = row["sip_username"]
    user_sip_id = row["id"]
    caller_id_number = row["caller_id_number"]
    if caller_id_number == nil then caller_id_number = "" end
    user_url = user_sipname.."@"..user_domain

    table.insert(xml,[[ <user id="]]..row["sip_username"]..[[" number-alias="]]..row["sip_username"]..[[">]])
    table.insert(xml,[[ <params> ]])
    table.insert(xml,[[     <param name="password" value="]]..row["sip_password"]..[["/> ]])
    table.insert(xml,[[     <param name="vm-password" value="123456"/>]])
    table.insert(xml,[[     <param name="vm-enabled" value="true"/>]])
    table.insert(xml,[[     <param name="MWI-Account" value="]]..row["sip_username"]..[[@]]..row["domain"]..[["/>]])

    table.insert(xml,[[     <param name="callback-dialplan" value="XML"/>]])
    table.insert(xml,[[     <param name="callback-context" value="]]..user_domain..[["/>]])
    table.insert(xml,[[     <param name="NDLB-force-rport" value="true"/>]])
    table.insert(xml,[[     <param name="dial-string" value="{sip_invite_domain=${domain_name},leg_timeout=30,presence_id=]]..user_url..[[}${sofia_contact(]]..user_url..[[)}"/>]])
    table.insert(xml,[[  </params>]])
    table.insert(xml,[[  <variables>]])
    table.insert(xml,[[     <variable name="phoneai_domain" value="]]..user_domain..[["/>]])
    table.insert(xml,[[     <variable name="phoneai_domain_id" value="]]..user_domain_id..[["/>]])
    table.insert(xml,[[     <variable name="phoneai_username" value="]]..user_sipname..[["/>]])
    table.insert(xml,[[     <variable name="phoneai_extension_id" value="]]..user_sip_id..[["/>]])

    table.insert(xml,[[     <variable name="domain_uuid" value="]]..user_domain..[["/>]])
    table.insert(xml,[[     <variable name="user_context" value="]]..user_domain..[["/>]])
    -- table.insert(xml,[[     <variable name="hold_music" value="]]..moh_url..[["/>]])

    table.insert(xml,[[     <variable name="number" value="]]..user_sipname..[["/>]])
    table.insert(xml,[[     <variable name="accountcode" value="]]..user_sipname..[["/>]])
    table.insert(xml,[[     <variable name="effective_caller_id_name" value="]]..user_sipname..[["/>]])
    -- table.insert(xml,[[     <variable name="effective_caller_id_number" value="]]..ext.number..[["/>]])
    if caller_id_number ~= nil then
        table.insert(xml,[[     <variable name="outbound_caller_id_name" value="]]..caller_id_number..[["/>]])
        table.insert(xml,[[     <variable name="outbound_caller_id_number" value="]]..caller_id_number..[["/>]])
    else
        table.insert(xml,[[     <variable name="outbound_caller_id_name" value="]]..DEFAULT_CALLERID..[["/>]])
        table.insert(xml,[[     <variable name="outbound_caller_id_number" value="]]..DEFAULT_CALLERID..[["/>]])
    end
    table.insert(xml,[[     <variable name="sip-force-contact" value="NDLB-connectile-dysfunction"/>]])
    table.insert(xml,[[     <variable name="sip-force-expires" value="630"/>]])

    -- table.insert(xml,[[     <variable name="call_recording" value="]]..call_recording..[["/>]])
    --
    table.insert(xml,[[  </variables>]])
    table.insert(xml,[[  </user>  ]])
end)


table.insert(xml, [[		</domain>]]);
table.insert(xml, [[	</section>]]);
table.insert(xml, [[</document>]]);


XML_STRING = table.concat(xml, "\n");

end

