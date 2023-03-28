from typing import Union, List
import websocket
import json
import ujson
import random
import time
import threading

class MyGateway:
    def __init__(self, token) -> None:
        self.heartbeat_interval = 41.25
        self.handlers: List[dict] = []
        self.open: bool = False
        self.ready = False
        self.heart = False
        
        self.token = token
        self.session = None
        self.seq = None

        self.test = True

        # websocket.enableTrace(True)
        
        self.ws = websocket.WebSocketApp(
            "wss://gateway.discord.gg/?v=9&encoding=json",
            on_message = self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        self.ws.on_open = self.on_open

    @property
    def isReady(self):
        return self.ready
    
    def on_message(self, ws, message):
        message = json.loads(message)

        msg_code = message.get('t')
        msg_data = message.get('d')
        op_code = message.get('op')
        self.seq = message["s"]

        # print(op_code)
        
        
        # Gateway Opcodes
        # code, name, client action, description
        
        # 0	Dispatch, Receive,              An event was dispatched.
        # 1	Heartbeat, Send/Receive,	    Fired periodically by the client to keep the connection alive.
        # 2	Identify, Send,                 Starts a new session during the initial handshake.
        # 3	Presence Update, Send,          Update the client's presence.
        # 4	Voice State, Update,	        Send Used to join/leave or move between voice channels.
        # 6	Resume, Send,                   Resume a previous session that was disconnected.
        # 7	Reconnect,	Receive,	        You should attempt to reconnect and resume immediately.
        # 8	Request Guild Members, Send,    Request information about offline guild members in a large guild.
        # 9	Invalid Session, Receive,	    The session has been invalidated. You should reconnect and identify/resume accordingly.
        # 10 Hello, Receive,	            Sent immediately after connecting, contains the heartbeat_interval to use.
        # 11 Heartbeat ACK,	Receive,	    Sent in response to receiving a heartbeat to acknowledge that it has been received.

        if op_code != 11:
            # print("\nMESSAGE:", message)
            pass

        if op_code == 1:
            self.heartbeat()

        # reconnect
        elif op_code == 7:
            self.reconnect()

        # restart
        elif op_code == 9:
            self.reconnect()

        # heartbeat
        if op_code == 10:
            self.heart = False
            self.heartbeat_interval = message['d']['heartbeat_interval'] / 1000
            print('init heartbeat, interval =', str(self.heartbeat_interval))
            threading.Thread(target=self.heartbeat_old, daemon=True).start()

        elif op_code == 11:
            # Ответный опкод на heartbeat
            pass

        # events
        elif op_code == 0:

            if msg_code == "READY" or  msg_code == "SESSIONS_REPLACE":
                self.ready = True

                self.session = msg_data['session_id']
                print('Gateway session:', str(self.session))

            for handler in self.handlers:
                if msg_code in handler["events"]:
                    handler["callback"](message)
                elif "ALL" in handler["events"]:
                    handler["callback"](message)
        
    def on_error(self, ws, error):
        print("ERROR", str(error))
    
    def on_close(self, ws, code, _):
        print('socket closed')
        self.reconnect()


    def on_open(self, message):
        if self.session is None:
            self.identify()
            print("Discord gateway ready.")
        else:
            reconnect = {
                "op": 6,
                "d": {
                "token": self.token,
                "session_id": self.session,
                "seq": self.seq
                }
            }
            
            # self.identify()
            self.send_json(reconnect)
            
            
            print("Reconnecting...")
            
            
        

    def send_json(self, data: dict) -> None:
        try:
            self.ws.send(ujson.dumps(data))
        except:
            pass

    def identify(self) -> None:
        self.send_json({
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "os": "Windows",
                    "os_version": "10",
                    "browser": "Windows",
                    "device": "NT 10"
                }
            }
        })

    def heartbeat_old(self):
        jitter = random.random()
        time.sleep(self.heartbeat_interval*jitter)
        self.heart = True

        while True:
            if self.heart is False:
                print('Hearbeat stoped')
                break

            heart = {
                "op": 1,
                "d": self.seq
            }

            self.send_json(heart)
            time.sleep(self.heartbeat_interval*jitter)

    def heartbeat(self):
        heart = {
                "op": 1,
                "d": self.seq
            }

        self.send_json(heart)

    def reconnect(self):
        """
        Должен быть отправлен при получении Opcode 7
        7 Reconnect, Receive, You should attempt to reconnect and resume immediately.
        """
        self.heart = False

        self.ws.close()
        self.ws = websocket.WebSocketApp(
            "wss://gateway.discord.gg/?v=9&encoding=json",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        self.ws.on_open = self.on_open
        print('SEND GATEWAY RECONNECT')
        self.ws.run_forever()

        
    def listener(self, events: Union[str, list]) -> dict:
        if isinstance(events, str):
            events = [events]

        def decorator(callback):
            self.handlers.append({"callback": callback, "events": events})

        return decorator