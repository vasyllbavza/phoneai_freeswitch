
-- action = argv[1];
-- key = argv[2];

-- api = freeswitch.API();

-- require "lib_events";

-- local evtdata = {};
-- evtdata["action"] = "silence_detected";
-- evtdata['keys'] = "1";
-- evtdata['call_id'] = "1";
-- evtdata['call_uuid'] = "cf1411a9-8a45-4231-b5c7-559ec03d3639";
-- evtdata["param1"] = "phoneAI";
-- evtdata["param2"] = "17866648610";
-- evtdata["param3"] = "1,2,3,";
-- evtdata["param4"] = "";
-- evtdata["key_level"] = 0;
-- evtdata["key_parent"] = 0;

-- if action == "call_started" then
--     evtdata["action"] = action
-- end
-- if action == "call_keys" then
--     evtdata["action"] = action
--     evtdata['keys'] = key;
-- end
-- if action == "silence_detected" then
--     evtdata["action"] = action
-- end

-- mydtbd_send_event(evtdata);


-- # luarun test.lua call_started
-- # luarun test.lua call_keys '1,2,3,'
-- # luarun test.lua silence_detected


sip_paid = "+17866648610;verstat=TN-Validation-Passed"
-- sip_paid = "+17866648610;verstat=TN-Validation-Failed"
-- sip_paid = "+17866648610;verstat=No-TN-Validation"

function check_cid_verified(inp_str)
    result = string.find(inp_str, "verstat=TN%-Validation%-Passed")
    if result ~= nil then
        return 1
    end
    return 0
end

if check_cid_verified(sip_paid) == 1 then
    print("verified")
else
    print("NOT verified")
end


math.randomseed(os.time())
fist_number = math.random(1, 5)
print(fist_number)
-- second_number = math.random(fist_number+1, 9)
second_number = math.random(1, 4)
print(second_number)

print(fist_number+second_number)


phone = "17866648610"
print(phone:len())

print(phone)
print(phone:sub(-10))


function check_carrier(number) then
    session:execute("curl", "https://phoneai.boomslang.io/api/number/lookup/?number="..number)
    curl_response_code = session:getVariable("curl_response_code")
    curl_response      = session:getVariable("curl_response_data")

    if curl_response_code == 200 then
        return 1
    end
    return 0
end

local ret = check_carrier("14033098527")
freeswitch.consoleLog("INFO", ret)
