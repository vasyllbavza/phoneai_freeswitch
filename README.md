# phoneai_freeswitch
freeswitch phone service

Four Section

1) lua scripts:
```
    lua_scripts/phoneai.lua
```
    after call connected, this script start speech to text conversion
    with watson backend. when number detected it send events and
    event handler caputre that and do further processing.

    when silence detect with predefined time [5second],
    it trigger silence event to start navigate.

2) api to initiate calls:
```
    api_code/api/views.py
```
    this api allow to trigger call. use your 11 digit number in number field.
    it will initiate a call.

    example:
```
    curl -H "Authorization: Token afd8b1c1d09600bc31ac222174ed308256a34ce1" \
        https://phoneai.boomslang.io/api/makecall/?number=1XXXXXXXXXX
```

3) dtmf input processing and store and initiate crawling
    api_code/call_esl.py

4) admin interface to view reports
    /api_code/api/admin.py
```
    url: https://phoneai.boomslang.io/api/admin/
    user: admin
    pass: nguAO0YesMt162fnVbMwTa0tgeg
```