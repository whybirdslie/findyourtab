import asyncio
import json
import websockets
import logging
from websockets.exceptions import ConnectionClosed

class TabWebSocketServer:
    def __init__(self):
        self.clients = set()
        self.browser_tabs = {}
        # Configure logging
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger('WebSocketServer')
        # Suppress websockets server logger
        logging.getLogger('websockets.server').setLevel(logging.ERROR)

    async def register(self, websocket):
        self.clients.add(websocket)
        self.logger.info(f"Client connected. Total clients: {len(self.clients)}")
        await self.send_all_tabs(websocket)

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        self.logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def send_all_tabs(self, websocket):
        if self.browser_tabs:
            # Combine all tabs from all browsers while preserving their browser type
            all_tabs = []
            for browser_type, tabs in self.browser_tabs.items():
                # Ensure each tab has the correct browser type
                for tab in tabs:
                    tab['browser'] = browser_type
                all_tabs.extend(tabs)
            
            await websocket.send(json.dumps({
                "type": "tabs_update",
                "tabs": all_tabs,
                "browsers": list(self.browser_tabs.keys())  # This will now include both Opera and Opera GX
            }))

    def update_tab_state(self, tabs, browser):
        # Store tabs directly as a list
        self.browser_tabs[browser] = tabs

    async def broadcast_current_state(self):
        # Combine all tabs from all browsers while preserving their browser type
        all_tabs = []
        for browser_type, tabs in self.browser_tabs.items():
            # Ensure each tab has the correct browser type
            for tab in tabs:
                tab['browser'] = browser_type
            all_tabs.extend(tabs)

        message = json.dumps({
            "type": "tabs_update",
            "tabs": all_tabs,
            "browsers": list(self.browser_tabs.keys())  # This will now include both Opera and Opera GX
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
            
            print(f"Received tabs update from browser: {browser}")  # Debug print
            print(f"Number of tabs received: {len(tabs)}")  # Debug print
            print(f"Sample tab browsers: {[tab['browser'] for tab in tabs[:3]]}")  # Debug print
            
            # Additional browser detection from URLs and user agent info
            for tab in tabs:
                # Set the browser type from the extension's detection
                tab['browser'] = browser
                
                # Only update Unknown tabs
                if tab['browser'] == 'Unknown':
                    if 'chrome-extension://' in tab.get('url', ''):
                        tab['browser'] = 'Chrome'
                    elif 'brave-extension://' in tab.get('url', ''):
                        tab['browser'] = 'Brave'
                    elif 'opera-extension://' in tab.get('url', ''):
                        tab['browser'] = browser
            
            # Store tabs under their specific browser
            if browser not in self.browser_tabs:
                self.browser_tabs[browser] = []
            
            # Update the tabs for this specific browser
            self.browser_tabs[browser] = tabs
            
            print(f"Current browsers in storage: {list(self.browser_tabs.keys())}")  # Debug print
            print(f"Tabs per browser: {[(b, len(t)) for b, t in self.browser_tabs.items()]}")  # Debug print
            
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
        try:
            await self.register(websocket)
            async for message in websocket:
                try:
                    await self.handle_message(websocket, message)
                except Exception as e:
                    self.logger.debug(f"Error handling message: {e}")
        except ConnectionClosed:
            pass  # Silently handle normal connection closes
        except EOFError:
            pass  # Silently handle EOF errors during handshake
        except Exception as e:
            if "connection closed while reading HTTP request line" not in str(e):
                self.logger.warning(f"Unexpected error in handler: {e}")
        finally:
            try:
                await self.unregister(websocket)
            except Exception:
                pass

    async def start_server(self, host="localhost", port=8765):
        while True:  # Keep trying to start the server
            try:
                async with websockets.serve(
                    self.handler, 
                    host, 
                    port, 
                    ping_interval=None,
                    ping_timeout=None,
                    logger=None  # Disable internal websockets logger
                ) as server:
                    self.logger.info(f"WebSocket server started at ws://{host}:{port}")
                    await asyncio.Future()  # run forever
            except Exception as e:
                self.logger.error(f"Server error, restarting: {e}")
                await asyncio.sleep(1)  # Wait before retrying