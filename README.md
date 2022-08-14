# phoneai_freeswitch
freeswitch phone service

![img](schema.png)

#### Four Section

1) lua scripts:
```
    lua_scripts/phoneai.lua
```
    after call connected, this script start speech to text conversion
    with watson backend. when number detected it send events and
    event handler caputre that and do further processing.

    when silence detect with predefined time [5second],
    it trigger silence event to start navigate.

2) API
```
api_code/api/views.py
```
3) dtmf input processing and store and initiate crawling
```
api_code/call_esl.py
```

4) admin interface to view reports
```
/api_code/api/admin.py
```

```
url: https://phoneai.boomslang.io/api/admin/
user: admin
pass: nguAO0YesMt162fnVbMwTa0tgeg
```

**cronjob**
/etc/crontab
```
* * * * * root  /root/py36ENV/bin/python /root/code/phoneai_freeswitch/api_code/call_retry.py > /var/log/call_cron.log 2>&1
```
<br/><br/>
##### API Authentication: 

Token based authentication is needed to access API resources.
we need to put token in Authorization Header during api request.

example:
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" https://phoneai.boomslang.io/api/UPDATE-ENDPOINT-HERE
```

<br/><br/>

**Call Menu API**

Click [here](api_call_menu.md) for more information

<br/><br/>

**SMS API**

To send SMS, we can use this api

Request:
```
curl --location -X POST 'https://phoneai.boomslang.io/api/sendsms/' \
-H 'Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd' \
-H 'Content-Type: application/json' \
-d '{
    "sms_to": "1786XXX86XX",
    "sms_body": "hello",
    "callback_url": "https://webhook.site/da7b7433-e75e-45c1-a81d-d274955b4531"
}'
```

Response:
```
{
    "id": 7,
    "sms_to": "1786XXX86XX",
    "sms_body": "hello",
    "callback_url": "https://webhook.site/da7b7433-e75e-45c1-a81d-d274955b4531"
    "status": 0
}
```

CallBack SMS payload:
```
{
    "from": "17866648610",
    "to": "14582037530",
    "text": "Fydyd"
}
```

<br/><br/>
##### OneUp API

API for Extension and DID phonenumber management

Click [here](api_oneup.md) for more information

<br/><br/>
**Postman collection**

[Click Here](phoneAI.postman_collection.json) for the lastest postman collection export

<br/><br/>
