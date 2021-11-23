--[[
    watson send xml string with transcribe information
    we need to parse it to get transcribed text

    todo: we only collect text. 
    but we do not have any idea about context.
    we may need to add some AI assistant logics
]]
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

function upload_webhook(msg,keys)

    webhook_url = "https://webhook.site/9525bf64-a5de-46f9-b3a4-18b9a025f8d5"

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

-- depreciated code
--


-- Used to parse the XML results.
-- function getResults(s) 
--     local xml = parse_xml(s);
--     --freeswitch.consoleLog("notice", "[asr] xml:" .. json.encode(xml) .. "\n");
--     local stack = {}
--     local top = {}
--     table.insert(stack, top)
--     top = {grammar=xml[2].xarg.grammar, score=xml[3].xarg.confidence, text=xml[4][1]}
--     table.insert(stack, top)
--     return top;
-- end
-- function parse_xmlstr(speechStr)
--     local confidenceVal = string.match(speechStr, "<interpretation .* confidence=\"(%d+)\">");
--     if confidenceVal ~= nil or confidenceVal ~= "" then
--         confidenceVal = tonumber(confidenceVal)
--     else
--         confidenceVal = 0
--     end
--     local speech = string.match(speechStr, "<interpretation .*>(.*)</input>");
--     if speech == nil then
--         speech = "";
--     end
--     speech = speech:lower();

--     if confidenceVal >= confidenceRef then
--         speechOut = speech;
--         return speech
--     else
--           return ""
--     end
-- end

--ASR Stuff
-- Used in parse_xml
-- function parseargs_xml(s)
--     local arg = {}
--     string.gsub(s, "(%w+)=([\"'])(.-)%2", function (w, _, a)
--                         arg[w] = a
--                      end)
--     return arg
-- end

-- Turns XML into a lua table.
-- function parse_xml(s)
--     local stack = {};
--     local top = {};
--     table.insert(stack, top);
--     local ni,c,label,xarg, empty;
--     local i, j = 1, 1;
--     while true do
--         ni,j,c,label,xarg, empty = string.find(s, "<(%/?)(%w+)(.-)(%/?)>", i);
--         if not ni then
--             break
--         end
        
--         local text = string.sub(s, i, ni-1);
--         if not string.find(text, "^%s*$") then
--              table.insert(top, text);
--         end
        
--         if empty == "/" then
--             table.insert(top, {label=label, xarg=parseargs_xml(xarg), empty=1});
--         elseif c == "" then
--             top = {label=label, xarg=parseargs_xml(xarg)};
--             table.insert(stack, top);
--         elseif label == "input" then
--             local toclose = table.remove(stack);
--             top = stack[#stack];
--             if #stack < 1 then
--                 error("nothing to close with "..label);
--             end
--             if toclose.label ~= label then
--                 error("trying to close "..toclose.label.." with "..label);
--             end
--             table.insert(stack, toclose);
--         else

--         end
        
--         i = j+1;
--     end
    
--     local text = string.sub(s, i);
--     if not string.find(text, "^%s*$") then
--       table.insert(stack[stack.n], text);
--     end
--     return stack;
-- end
