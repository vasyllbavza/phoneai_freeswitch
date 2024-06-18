#!/bin/bash

git pull origin $1
supervisorctl reload

cp lua_scripts/directory.lua /usr/share/freeswitch/scripts/app/phoneai/
cp lua_scripts/inbound.lua  /usr/share/freeswitch/scripts/app/phoneai/
cp lua_scripts/macro.lua  /usr/share/freeswitch/scripts/app/phoneai/
cp lua_scripts/outbound.lua  /usr/share/freeswitch/scripts/app/phoneai/
cp lua_scripts/chat.lua  /usr/share/freeswitch/scripts/app/phoneai/
cp lua_scripts/utils.lua  /usr/share/freeswitch/scripts/app/phoneai/
cp lua_scripts/lib_events.lua  /usr/share/freeswitch/scripts/app/phoneai/
cp lua_scripts/xfer_ext.lua  /usr/share/freeswitch/scripts/app/phoneai/

source  /root/py36ENV/bin/activate

cd /root/code/phoneai_freeswitch/api_code/
python manage.py migrate
