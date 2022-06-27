local destination_number = session:getVariable("destination_number")
local caller_id_number = session:getVariable("caller_id_number")
local call_uuid = session:getVariable("uuid")

session:execute("info")