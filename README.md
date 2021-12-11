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

    To make the call menu complete of old in-complement menu we can use an extra param for this
    example:
```
    curl -H "Authorization: Token afd8b1c1d09600bc31ac222174ed308256a34ce1" \
        https://phoneai.boomslang.io/api/makecall/?number=1XXXXXXXXXX&new=0
```

    To scan result of a number, we can use this api

    example:
```
    curl -H "Authorization: Token afd8b1c1d09600bc31ac222174ed308256a34ce1" \
        https://phoneai.boomslang.io/api/scan/?limit=10&offset=0&number=18009256278

    Response:
        {
            "count": 7,
            "next": "https://phoneai.boomslang.io/api/scan/?limit=3&number=18009256278&offset=3",
            "previous": null,
            "results": [
                {
                    "id": 52,
                    "number": "18009256278",
                    "status": "Processed",
                    "attempt": 2,
                    "created_at": "2021-12-10T11:14:23.481349Z",
                    "updated_at": "2021-12-10T11:40:03.225748Z"
                },
                {
                    "id": 51,
                    "number": "18009256278",
                    "status": "Calling",
                    "attempt": 1,
                    "created_at": "2021-12-10T11:13:43.234798Z",
                    "updated_at": "2021-12-10T11:13:43.239514Z"
                },
                {
                    "id": 50,
                    "number": "18009256278",
                    "status": "Calling",
                    "attempt": 1,
                    "created_at": "2021-12-10T11:11:17.509273Z",
                    "updated_at": "2021-12-10T11:11:17.512518Z"
                }
            ]
        }
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