### OneUp API

<br/><br/>
#### List all extensions

Request: [ GET ]
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" https://phoneai.boomslang.io/api/extensions/
```

<br/>
Response:

```json
[
    {
        "id": 11,
        "user_id": 1,
        "cellphone": "",
        "transcription": 0,
        "sip_username": "1001",
        "sip_password": "p@ass123456",
        "updated_at": "2022-07-02T03:11:36.347291Z",
        "domain": "phoneai.boomslang.io"
    },
    {
        "id": 13,
        "user_id": 1,
        "cellphone": "",
        "transcription": 0,
        "sip_username": "1003",
        "sip_password": "p@ass123456",
        "updated_at": "2022-07-02T03:11:47.570922Z",
        "domain": "phoneai.boomslang.io"
    },
]
```

<br/><br/>

##### GET extension information

Request: [ GET ]
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" https://phoneai.boomslang.io/api/extensions/1
```

Response:
```json
{
    "id": 11,
    "user_id": 1,
    "cellphone": "",
    "transcription": 0,
    "sip_username": "1001",
    "sip_password": "p@ass123456",
    "updated_at": "2022-07-02T03:11:36.347291Z",
    "domain": "phoneai.boomslang.io"
}
```
<br/>
##### DELETE extension information

Request: [ DELETE ]
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" https://phoneai.boomslang.io/api/extensions/1/
```
<br/>
##### Create etensions
Request: [ POST ]
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" https://phoneai.boomslang.io/api/extensions/
```

payload
```
{
    "sip_username": "1003",
    "sip_password": "123456",
    "cellphone": "",
}
```
<br/>
##### LIST DID phonenumber
Request: [ GET ]
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" https://phoneai.boomslang.io/api/did_numbers/
```

Response:
```json
    [
        {
            "id": 1,
            "provider": 1,
            "phonenumber": "13013019105",
            "domain": "phoneai.boomslang.io",
            "extension": null,
            "created_at": "2022-06-12T07:35:50.947110Z"
        },
        {
            "id": 2,
            "provider": 1,
            "phonenumber": "17862062698",
            "domain": "phoneai.boomslang.io",
            "extension": 1,
            "created_at": "2022-06-15T03:59:05.370107Z"
        }
    ]
```

<br/>
##### Search puchasable phoenenumber from Flowroute

Request: [ GET ]
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" https://phoneai.boomslang.io/api/did_numbers/search/?npa=786&limit=4
```
params
```
npa: area code to search for
limit: that will list available number
```
Response:
```json
{
    "data": [
        {
            "number": "17862062699",
            "monthly_cost": 0.5
        },
        {
            "number": "17862062701",
            "monthly_cost": 0.5
        },
        {
            "number": "17862062704",
            "monthly_cost": 0.5
        },
        {
            "number": "17862062782",
            "monthly_cost": 0.5
        }
    ]
}
```
<br/>
##### Complete Buy puchasable phoenenumber and Assigned to extension

Request: [ POST ]
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" https://phoneai.boomslang.io/api/did_numbers/
```

payload
```
{
    "phonenumber": "17862062698",
    "extension": 1
}
```

Response:
```
201 Created.
```

<br/>
##### List CDR - Call Detail Records

Request: [ GET ]
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" https://phoneai.boomslang.io/api/cdrs/
```

Filter:
```
- did_number: OneUp number
- extension_number: Extension Sip username
```
Search:
```
- id
- created_at
```
Ordering:
```
- created_at
```

Response:
```json
[
    {
        "id": 2374,
        "domain": "phoneai.boomslang.io",
        "call_direction": "inbound",
        "call_uuid": "d5e28714-1be2-11ed-8b63-9dde3cd1ca46",
        "didnumber": 5,
        "call_from": "7866648610",
        "call_to": "7862062784",
        "extension": 14,
        "is_verified": true,
        "in_contact": true,
        "bill_duration": 10,
        "recording": "/api/media/domain_1/14_d5e28714-1be2-11ed-8b63-9dde3cd1ca46.mp3",
        "transcription_text": "[{'transcript': 'hello hello ', 'confidence': 0.91, 'timestamps': [['hello', 3.65, 3.94], ['hello', 3.94, 4.38]]}, {'transcript': 'hello hello ', 'confidence': 0.92, 'timestamps': [['hello', 6.39, 6.68], ['hello', 6.68, 7.09]]}]",
        "hangup_cause": "NORMAL_CLEARING",
        "started_at": "2022-08-14T08:07:38Z",
        "created_at": "2022-08-14T15:07:49.135713Z"
    },
    {
        "id": 2373,
        "domain": "phoneai.boomslang.io",
        "call_direction": "inbound",
        "call_uuid": "b035071c-1be2-11ed-8b36-9dde3cd1ca46",
        "didnumber": 5,
        "call_from": "7866648610",
        "call_to": "7862062784",
        "extension": 14,
        "is_verified": true,
        "in_contact": true,
        "bill_duration": 8,
        "recording": "/api/media/domain_1/14_b035071c-1be2-11ed-8b36-9dde3cd1ca46.mp3",
        "transcription_text": null,
        "hangup_cause": "NORMAL_CLEARING",
        "started_at": "2022-08-14T08:06:35Z",
        "created_at": "2022-08-14T15:06:43.892484Z"
    },
]

```

