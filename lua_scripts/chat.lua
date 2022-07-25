-----------------
-- chat.lua
-----------------
local inspect = require "inspect"
local dbh = freeswitch.Dbh("pgsql://hostaddr=127.0.0.1 dbname=phoneai user=phoneai password='P0s@@w0123#' options='-c client_min_messages=NOTICE'")
api = freeswitch.API();
-- freeswitch.consoleLog("info", message:serialize());
local domain_name = "phoneai.boomslang.io"

local chat_from = message:getHeader("from_user");
local chat_to = message:getHeader("to_user");
local chat_host = message:getHeader("to_host");
local chat_text = message:getBody();
local sender = chat_from.."@"..chat_host;

function uriencode(vals)

    function escape (s)
        s = string.gsub(
            s,
            '([\r\n"#%%&+:;<=>?@^`{|}%\\%[%]%(%)$!~,/\'])',
            function (c)
                return '%'..string.format("%02X", string.byte(c));
            end
        );
        s = string.gsub(s, "%s", "+");
        return s;
    end

    function encode (t)
        local s = "";
        for k , v in pairs(t) do
            s = s .. "&" .. escape(k) .. "=" .. escape(v);
        end
        return string.sub(s, 2);
    end

    if type(vals) == 'table' then
        return encode(vals);
    else
        local t = {};
        for k, v in  string.gmatch(vals, ",?([^=]+)=([^,]+)") do
            t[k]=v;
        end
        return encode(t);
    end
end

function send_sms(number, sms_text, chat_from)

    headers = "append_headers 'Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd'"
    postdata = uriencode("sms_to="..number..",sms_body="..sms_text)
    sms_url = "https://phoneai.boomslang.io/api/sendsms/"
    if chat_from ~= nil then
        sms_url = sms_url.."?from_number="..chat_from
    end
    curl_response = api:execute("curl", sms_url.." "..headers.." post "..postdata)
    -- curl_response_code = api:getVariable("curl_response_code")
    -- curl_response      = session:getVariable("curl_response_data")
    -- freeswitch.consoleLog("INFO", inspect(curl_response_code))
    freeswitch.consoleLog("INFO", inspect(curl_response))
    if curl_response_code == 200 then
        return 1
    end
    return 0
end

function get_sofia_contact(agent_id)
    result = api:execute("sofia_contact", agent_id);
    if(result == "error/user_no_registered") then
        return "";
    else
        return result;
    end
end
function explode(seperator, str)
    local pos, arr = 0, {}
    if str == nil then return arr; end
    for st,sp in function() return string.find(str,seperator, pos, true) end do
        table.insert(arr, string.sub(str,pos, st-1))
        pos = sp + 1
    end
    table.insert(arr, string.sub( str, pos))
    return arr
end

function send_message(text_from, text_to, text)

    freeswitch.consoleLog("info", "chat console\n")
    
    local event = freeswitch.Event("CUSTOM", "SMS::SEND_MESSAGE");
    -- event:addHeader("proto", "sip");
    event:addHeader("dest_proto", "sip");
    event:addHeader("from", text_from.."@"..domain_name);
    -- event:addHeader("from_full", "sip:"..text_from.."@"..domain_name);
    event:addHeader("to", text_to.."@"..domain_name);
    -- event:addHeader("to_full", "sip:"..text_to.."@"..domain_name);
    -- event:addHeader("subject", "SMS-from-"..text_from);
    -- event:addHeader("type", "text/plain");
    -- event:addHeader("hint", "the hint");
    -- event:addHeader("replying", "true");
    event:addHeader("sip_profile", "internal");
    event:addBody(text);
    
    freeswitch.consoleLog("info", event:serialize());
    event:fire();

end

-- message:chat_execute("reply", "you said: " .. message:getBody());

-- chat_from = "7866648610"
-- chat_to = "1005"
-- chat_text = "hi!"
if chat_to:len() == 10 then
    chat_to = "1"..chat_to
end
if chat_to:len() == 11 then
    from_number = nil
    sql = "select fs_didnumber.phonenumber  from fs_didnumber "
    sql = sql .. " join fs_extension on fs_extension.id=fs_didnumber.extension_id "
    sql = sql .. " where fs_extension.sip_username='"..chat_from.."'"
    dbh:query(sql, function(row)
        from_number = row["phonenumber"]
    end)
    send_sms(chat_to, chat_text, from_number)
else
    -- send_message(chat_from, chat_to, chat_text);
    agent = chat_to.."@"..chat_host
    agent_url = get_sofia_contact(agent);
    if agent_url == nil or agent_url == "" then
        freeswitch.consoleLog("info", "extension is not available !!!");
    else
        exts = explode(",", agent_url);
        for k,v in pairs(exts) do
            exturl = v:gsub("sofia/", "");
            freeswitch.consoleLog("info", exturl);
            cmd = "bgapi chat sip|"..sender.."|"..exturl.."|"..chat_text;
            -- resp = api:executeString(cmd);
            resp = api:execute("chat", "sip|"..sender.."|"..exturl.."|"..chat_text.."|text/plain");
            freeswitch.consoleLog("info", resp);
        end
    end
end
