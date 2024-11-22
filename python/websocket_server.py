import asyncio
import json
import websockets

class TabWebSocketServer:
    def __init__(self):
        self.clients = set()
        self.browser_tabs = {}  # Store tabs for each browser

    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")
        await self.send_all_tabs(websocket)

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def send_all_tabs(self, websocket):
        if self.browser_tabs:
            # Combine all tabs from all browsers
            all_tabs = []
            for tabs in self.browser_tabs.values():
                all_tabs.extend(tabs)  # browser_tabs now stores lists directly
            
            await websocket.send(json.dumps({
                "type": "tabs_update",
                "tabs": all_tabs,
                "browsers": list(self.browser_tabs.keys())
            }))

    def update_tab_state(self, tabs, browser):
        # Store tabs directly as a list
        self.browser_tabs[browser] = tabs

    async def broadcast_current_state(self):
        # Combine all tabs from all browsers
        all_tabs = []
        for tabs in self.browser_tabs.values():
            all_tabs.extend(tabs)

        message = json.dumps({
            "type": "tabs_update",
            "tabs": all_tabs,
            "browsers": list(self.browser_tabs.keys())
        })

        # Send to all clients
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.ConnectionClosed:
                pass

    async def handle_message(self, websocket, message):
        data = json.loads(message)
        if data["type"] == "tabs_update":
            tabs = data["tabs"]
            browser = data["browser"]
            
            # Additional browser detection from URLs
            for tab in tabs:
                if tab['browser'] == 'Unknown':
                    if 'chrome-extension://' in tab.get('url', ''):
                        tab['browser'] = 'Chrome'
                    elif 'brave-extension://' in tab.get('url', ''):
                        tab['browser'] = 'Brave'
            
            # Update browser tabs
            self.update_tab_state(tabs, browser)
            
            # Broadcast updated state
            await self.broadcast_current_state()
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