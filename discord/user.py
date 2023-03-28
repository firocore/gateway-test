from typing import Union, List
import random
import requests
import random

class User(object):
    def __init__(self, config) -> None:
        self.discord_token = config['discord']['TOKEN']
        self.discord_server = config['discord']['server']
        self.discord_channel = config['discord']['channel']
        self.discord_application = config['discord']['app']

        self.info: Union[dict, None] = None
        self.api: int = 9

        self.session: requests.Session = requests.Session()
    
    def gen_nonce(self) -> str:
        return ''.join([str(random.randint(0, 9)) for i in range(19)])
    
    def request(self, method, query, options):
        headers = {
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9003 Chrome/91.0.4472.164 Electron/13.4.0 Safari/537.36",
            "authorization": self.discord_token
        }

        post = self.session.request(
            method=method,
            url=f"https://discord.com/api/v9/{query}",
            headers=headers,
            json=options
        )

        return post

    def send_message(self, message: str):
        return self.request(
            "POST",
            f"channels/{self.discord_channel}/messages", 
            {"content": message, "nonce": self.gen_nonce(), "tts":False, "flags":0}
            )
    

    def send_interaction(self, session, promt):

        payload_json = {
            "type":2,"application_id": str(self.discord_application), "guild_id": str(self.discord_server), "channel_id": str(self.discord_channel),"session_id": session,"data":{"version":"1077969938624553050","id":"938956540159881230","name":"imagine","type":1,"options":[{"type":3,"name":"prompt","value":str(promt)}],"application_command":{"id":"938956540159881230","application_id":"936929561302675456","version":"1077969938624553050","default_permission":True,"default_member_permissions":None,"type":1,"nsfw":False,"name":"imagine","description":"Create images with Midjourney","dm_permission":True,"options":[{"type":3,"name":"prompt","description":"The prompt to imagine","required":True}]},"attachments":[]},"nonce": self.gen_nonce()}

        headers = {
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9003 Chrome/91.0.4472.164 Electron/13.4.0 Safari/537.36",
            "authorization": self.discord_token
        }

        post = self.session.request(
            method="POST",
            url=f"https://discord.com/api/v9/interactions",
            headers=headers,
            json=payload_json
            )

        return post
    
    def send_button_interaction(self, session, message_id, custom_id):
        payload_json = {
            "type":3,
            "nonce": self.gen_nonce(),
            "guild_id": str(self.discord_server),
            "channel_id": str(self.discord_channel),
            "message_flags":0,
            "message_id": str(message_id),
            "application_id": str(self.discord_application),
            "session_id":session,
            "data": {
                "component_type":2,
                "custom_id": str(custom_id)
                }
            }          

        headers = {
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9003 Chrome/91.0.4472.164 Electron/13.4.0 Safari/537.36",
            "authorization": self.discord_token
        }

        post = self.session.request(
            method="POST",
            url="https://discord.com/api/v9/interactions",
            headers=headers,
            json=payload_json)
        
        return post


    def fetch_dms(self, ready_event) -> list:
        dms = ready_event["d"]["private_channels"]

        index = []
        for dm in dms:
            msg = dm["last_message_id"]

            if msg:
                index.append(int(msg))

        index = sorted(index)
        sort_dms = []

        for i in index:
            for dm in dms:
                msg = dm["last_message_id"]

                if msg and int(msg) == i:
                    sort_dms.append(dm)

        return sort_dms

    def identify(self) -> bool:
        headers = {
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9003 Chrome/91.0.4472.164 Electron/13.4.0 Safari/537.36",
            "authorization": self.discord_token
        }

        post = self.session.request(
            method="GET",
            url=f"https://discord.com/api/v{self.api}/users/@me",
            headers=headers
        )

        if post.status_code == 401:
            return False

        self.info = post.json()
        self.session.headers.update(headers)

        return True