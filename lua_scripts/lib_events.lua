function mydtbd_send_event(mc_params)

    local cur_epoch = os.time();
    local custom_msg = "";
    local e = freeswitch.Event("custom", "mydtbd::info");
    e:addHeader("event_type", "mydtbd");
    e:addHeader("event_timestamp", cur_epoch);
    for k,v in pairs(mc_params) do
        e:addHeader(k, v);
    end
    e:addBody(custom_msg);
    e:fire();

end
