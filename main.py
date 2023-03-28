from discord.gateway import MyGateway
from discord.user import User

token = 'MTA4Mzk1OTIwMDMzNTU0NDM2MA.GxjAj-.80DDZQw4a_dY7JuFK4n38KOBxAIwZE1FX2Fd9U'

config = {
    'discord': {
        "TOKEN": token,
        "server": "1085213703881900102",
        "channel": "1085213704330686586",
        "app": "936929561302675456"
    }
}


class GatewayTest:
    def __init__(self) -> None:
        self.gateway = MyGateway(token)
        self.user = User(config)
        self.user.identify()

        self.session = None

        @self.gateway.listener("READY")
        def _on_ready(event):
            self.on_ready(event)

        @self.gateway.listener("SESSIONS_REPLACE")
        def _sessions_replace(event):
            self.on_ready(event)

        @self.gateway.listener("MESSAGE_CREATE")
        def _discord_message_create(event):
            print(event['d']['content'])

    def on_ready(self, event):
        self.session = event['d']['session_id']
        print('Gateway session:', self.session)

    def test_run(self):
        self.gateway.ws.run_forever()

if __name__ == "__main__":
    gateway = GatewayTest()
    gateway.test_run()