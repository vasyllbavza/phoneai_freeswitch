
### CALL MENU API Listing 

**API to initiate calls:**

this api allow to trigger call. use your 11 digit number in number field.
it will initiate a call.

    example:
```sh
    curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" \
        https://phoneai.boomslang.io/api/makecall/?number=1XXXXXXXXXX
```

To make the call menu complete of old in-complement menu we can use an extra param for this

example:
```sh
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" \
https://phoneai.boomslang.io/api/makecall/?number=1XXXXXXXXXX&new=0
```

<br/><br/>

**To scan result of a number, we can use this api**

Request:
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" \
https://phoneai.boomslang.io/api/scan/?limit=3&offset=0&number=18009256278
```
Response:
```
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
<br/><br/>
**To get Call menu tree, we can use this api**

Request:
```
curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" \
https://phoneai.boomslang.io/api/callmenu/?number=13013019105
```
Response:
```
{
    "id": 18,
    "number": "13013019105",
    "business_name": null,
    "retry_enabled": 1,
    "attempt": 4,
    "completed": true,
    "menu": {
        "id": 179,
        "info": {
            "parent_text": "",
            "keys_to_reach": ""
        },
        "key": "",
        "audio_text": " hello welcome to d. p. software solution press one for sales press 2 for support press 3 for operator",
        "audio_text_debug": [
            {
                "transcript": "press 2 for support press 3 for operator ",
                "confidence": 0.97,
                "timestamps": [
                    [
                        "press",
                        7.8,
                        8.07
                    ],
                    [
                        "two",
                        8.07,
                        8.28
                    ],
                    [
                        "for",
                        8.28,
                        8.51
                    ],
                    [
                        "support",
                        8.51,
                        9.13
                    ],
                    [
                        "press",
                        9.8,
                        10.05
                    ],
                    [
                        "three",
                        10.05,
                        10.36
                    ],
                    [
                        "for",
                        10.36,
                        10.6
                    ],
                    [
                        "operator",
                        10.6,
                        11.3
                    ]
                ]
            }
        ],
        "children": [
            {
                "id": 180,
                "info": {
                    "parent_text": "east press one for sales ",
                    "keys_to_reach": "1"
                },
                "key": "1",
                "audio_text": " thanks for contact sales department please press 3 to voice press sms and press 5 for facts",
                "audio_text_debug": [
                    {
                        "transcript": "thanks for contact sales department please press 3 to voice press for for SMS and press 5 for facts ",
                        "confidence": 0.89,
                        "timestamps": [
                            [
                                "thanks",
                                15.11,
                                15.44
                            ],
                            [
                                "for",
                                15.44,
                                15.66
                            ],
                            [
                                "contact",
                                15.66,
                                16.31
                            ],
                            [
                                "sales",
                                16.31,
                                16.77
                            ],
                            [
                                "department",
                                16.77,
                                17.5
                            ],
                            [
                                "please",
                                18.24,
                                18.52
                            ],
                            [
                                "press",
                                18.52,
                                18.82
                            ],
                            [
                                "three",
                                18.82,
                                19.1
                            ],
                            [
                                "to",
                                19.1,
                                19.27
                            ],
                            [
                                "voice",
                                19.27,
                                19.75
                            ],
                            [
                                "press",
                                20.44,
                                20.68
                            ],
                            [
                                "for",
                                20.68,
                                21.03
                            ],
                            [
                                "for",
                                21.03,
                                21.24
                            ],
                            [
                                "SMS",
                                21.24,
                                22.06
                            ],
                            [
                                "and",
                                22.76,
                                22.94
                            ],
                            [
                                "press",
                                22.94,
                                23.25
                            ],
                            [
                                "five",
                                23.25,
                                23.63
                            ],
                            [
                                "for",
                                23.7,
                                23.84
                            ],
                            [
                                "facts",
                                23.84,
                                24.5
                            ]
                        ]
                    }
                ],
                "children": [
                    {
                        "id": 181,
                        "info": {
                            "parent_text": "press three to voice",
                            "keys_to_reach": "1,3"
                        },
                        "key": "3",
                        "audio_text": " thanks for your query",
                        "audio_text_debug": null,
                        "children": []
                    },
                    {
                        "id": 184,
                        "info": {
                            "parent_text": "press five",
                            "keys_to_reach": "1,5"
                        },
                        "key": "5",
                        "audio_text": " thanks for your query",
                        "audio_text_debug": null,
                        "children": []
                    }
                ]
            },
            {
                "id": 182,
                "info": {
                    "parent_text": "press two for support",
                    "keys_to_reach": "2"
                },
                "key": "2",
                "audio_text": " thanks for your query",
                "audio_text_debug": null,
                "children": []
            },
            {
                "id": 183,
                "info": {
                    "parent_text": "three for operator",
                    "keys_to_reach": "3"
                },
                "key": "3",
                "audio_text": " thanks for your query",
                "audio_text_debug": null,
                "children": []
            }
        ]
    }
}
```
<br/><br/>
**To send call with predefined menu, we can use this api**

Request:
```
    curl -H "Authorization: Token 9c66b4539c522dbb19f390e902e501eebbc1adcd" \
        https://phoneai.boomslang.io/api/makecall_submenu/?id=171&forwarding_number=XXXXXXXXX
```
Response:
```
{
    "dial_number": "13027410434",
    "status": "success",
    "call_uuid": "24960e50-3a98-403f-8e02-51f8f408acd4",
    "message": "",
    "fs_output": "+OK Job-UUID: 07cdc030-88cd-11ec-a1d5-a593d3cd889e\n"
}

{
    "status": "fail",
    "message": "menu is completed already.",
    "fs_output": ""
}

```
