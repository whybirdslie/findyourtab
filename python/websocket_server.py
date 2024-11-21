import asyncio
import json
import websockets

class TabWebSocketServer:
    def __init__(self):
        self.clients = set()
        self.current_tabs = []

    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")
        if self.current_tabs:
            await websocket.send(json.dumps({
                "type": "tabs_update",
                "tabs": self.current_tabs
            }))

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def broadcast_tabs(self, tabs):
        self.current_tabs = tabs
        message = json.dumps({
            "type": "tabs_update",
            "tabs": tabs
        })
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.ConnectionClosed:
                pass

    async def handle_message(self, websocket, message):
        data = json.loads(message)
        if data["type"] == "tabs_update":
            await self.broadcast_tabs(data["tabs"])
        elif data["type"] == "activate_tab":
            # Broadcast tab activation request to all clients
            for client in self.clients:
                if client != websocket:  # Don't send back to sender
                    try:
                        await client.send(message)
                    except websockets.ConnectionClosed:
                        pass

    async def handler(self, websocket):
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def start_server(self, host="localhost", port=8765):
        async with websockets.serve(self.handler, host, port):
            print(f"WebSocket server started at ws://{host}:{port}")
            await asyncio.Future()  # run forever