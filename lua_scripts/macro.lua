--define the macro function
function macro(session, name, max_digits, max_timeout, param)

    tries = 1
    default_language = "en"
    default_dialect = "us"
    default_voice = "callie"
    sounds_dir = "/usr/share/freeswitch/sounds"

    if (session:ready()) then
        --create an empty table
        actions = {}
        session:flushDigits();
        --captcha
        if (name == "captcha_ivr") then
            table.insert(actions, {app="streamFile",data="phoneai/need_to_verify.mp3"});
            table.insert(actions, {app="streamFile",data="phoneai/captcha_q1.mp3"});
            table.insert(actions, {app="streamFile",data="phoneai/"..param.number1..".mp3"});
            table.insert(actions, {app="streamFile",data="phoneai/and.mp3"});
            table.insert(actions, {app="streamFile",data="phoneai/"..param.number2..".mp3"});
            table.insert(actions, {app="streamFile",data="phoneai/captcha_q2.mp3"});
        end
        --record your message at the tone press any key or stop talking to end the recording
        if (name == "record_message") then
            table.insert(actions, {app="streamFile",data="voicemail/vm-record_message.wav"});
        end
        --beep
        if (name == "record_beep") then
            table.insert(actions, {app="tone_stream",data="L=1;%(1000, 0, 640)"});
        end

        --if actions table exists then process it
        if (actions) then
            --set default values
            timeout = 100;
            dtmf_digits = "";
            --loop through the action and data
            for key, row in pairs(actions) do
                if (session:ready()) then
                    if (string.len(dtmf_digits) == 0) then
                        if (row.app == "streamFile") then
                            session:streamFile(sounds_dir.."/"..default_language.."/"..default_dialect.."/"..default_voice.."/"..row.data);
                        elseif (row.app == "tone_stream") then
                            session:streamFile("tone_stream://"..row.data);
                        elseif (row.app == "silence_stream") then
                            session:streamFile("silence_stream://"..row.data);
                        end
                        session:streamFile("silence_stream://100");
                    end --if
                end --session:ready
            end --for
            --get the remaining digits
            if (session:ready()) then
                if param == nil or type(param) ~= 'table' or param.escape_digit == nil or dtmf_digits ~= param.escape_digit then
                if (string.len(dtmf_digits) < max_digits) then
                    dtmf_digits = dtmf_digits .. session:getDigits(max_digits-string.len(dtmf_digits), "#", max_timeout);
                end
                end
            end
            --return dtmf the digits
            return dtmf_digits;
        else
            --no dtmf digits to return
            return '';
        end
    end
end