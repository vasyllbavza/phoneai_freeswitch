import json
from flowroutenumbersandmessaging.flowroutenumbersandmessaging_client import FlowroutenumbersandmessagingClient
import requests

class TreeNode(dict):

    def __init__(self, id, menu, children=None, key = None, parent_text = None, keys_to_reach = None):
        super().__init__()
        self.__dict__ = self
        self.id = id
        self.info = {
            "parent_text": parent_text,
            "keys_to_reach": keys_to_reach
        }
        self.key = key
        self.audio_text = menu["audio_text"]
        self.audio_text_debug = menu["audio_text_debug"]
        self.children = list(children) if children is not None else []

    def insert(self, obj):
        self.child.append(obj)


    @staticmethod
    def from_dict(dict_):
        """ Recursively (re)construct TreeNode-based tree from dictionary. """
        node = TreeNode(dict_['name'], dict_['key'], dict_['children'])
#        node.children = [TreeNode.from_dict(child) for child in node.children]
        node.children = list(map(TreeNode.from_dict, node.children))
        return node

def send_sms(to_number, sms_text):

    basic_auth_user_name = "06b93c4e"
    basic_auth_password = "947410ae2da44b59867c564cbbc7c0c3"
    mobile_number = "17866648610"
    from_number = "14582037530"

    client = FlowroutenumbersandmessagingClient(basic_auth_user_name, basic_auth_password)
    messages_controller = client.messages
    req = {
        "data": {
            "type": "message",
            "attributes": {
                "to": to_number,
                "from": from_number,
                "body": ""
            }
        }
    }
    req["data"]["attributes"]["body"] = str(sms_text)
    request_body = json.dumps(req)
    print(request_body)
    result = messages_controller.send_a_message(request_body)
    return result

def post_webhook(url, data):

    try:
        str = json.dumps(data)
        datajson = json.loads(str)
        try:
            response = requests.post(url, json=datajson)
            if response.ok:
                print("webhook[%s] sent. response = %s" %(url, response.content))
            else:
                print("webhook sent failed !!!!!")
            print("webhook submit -> done")
        except:
            pass

    except Exception:
        print("Exception: webhook sent failed !!!!!")
        pass

    return True
