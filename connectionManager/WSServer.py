from connectionManager.ServerTemplate import ServerTemplate

import websockets
import asyncio

class WSServer(ServerTemplate):
    def __init__(self, host: str, port: str, loop: asyncio.AbstractEventLoop):
        self.server = websockets.serve(self.conn_handle, host=host, port=int(port), loop=loop)
        print(f"-- WSServer is running on {host}:{port}")

    def run(self):
        return self.server

    async def conn_handle(self, wsocket: websockets.WebSocketClientProtocol, path: str):
        host, port = wsocket.remote_address
        print(f'{host}:{port} websocket has connected')
        while not wsocket.closed:
            try:
                result = await asyncio.wait_for(wsocket.recv(), 
                                                timeout=5)
                print(f"From {host}:{port} recived:", result)

            except asyncio.TimeoutError:
                continue

            except (asyncio.CancelledError, websockets.ConnectionClosed):
                print(f"{host}:{port} websocket has disconnected.{wsocket.close_code}:'{wsocket.close_reason}'")

    async def sendall(self, msg):
        if (len(self.server.ws_server.websockets) > 0):
            await asyncio.wait([wsocket.send(msg) for wsocket in self.server.ws_server.websockets])