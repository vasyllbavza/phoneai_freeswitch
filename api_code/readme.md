
docker build -t phoneai .

docker run -itd -p 8000:8000 --name phoneai -v /Users/mohammadkamruzzaman/mywork1/phoneAI/code/phoneai_freeswitch/api_code:/app --platform=linux/x86_64  phoneai

docker exec -it phoneai  bash


## supervisor configurations
cat << EOT > /etc/supervisor/conf.d/phone.conf
[program:gunicorn]
command=/root/py36ENV/bin/gunicorn phoneai_api.wsgi:application  -b 127.0.0.1:8123
directory=/root/code/phoneai_freeswitch/api_code/
#user=ubuntu
autostart=true
autorestart=true
startsecs = 5
startretries = 20
redirect_stderr=true
logfile=/var/log/gunicorn.log

[program:callesl]
command=/root/py36ENV/bin/python call_esl.py > /var/log/call_esl.log
directory=/root/code/phoneai_freeswitch/api_code/
#user=ubuntu
autostart=true
autorestart=true
startsecs = 5
startretries = 20
redirect_stderr=true
logfile=/var/log/call_esl.log

EOT