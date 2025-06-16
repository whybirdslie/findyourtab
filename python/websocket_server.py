"""
MIT License

Copyright (c) 2025 whybirdslie (FindYourTab)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

Any modifications or contributions to this software must maintain attribution to the original author (whybirdslie) and share credit for the work.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import json
import websockets
import logging
import psutil
import ctypes
from ctypes import wintypes
from websockets.exceptions import ConnectionClosed

# Windows API constants and functions for window management
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Windows API constants
SW_RESTORE = 9
SW_SHOW = 5
HWND_TOP = 0
SWP_SHOWWINDOW = 0x0040

# Define callback function type for EnumWindows
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

# Windows API function definitions
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.SetWindowPos.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, wintypes.LPDWORD]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.BringWindowToTop.argtypes = [wintypes.HWND]
user32.BringWindowToTop.restype = wintypes.BOOL

# Cache for browser processes to avoid repeated lookups
_browser_process_cache = {}
_cache_timestamp = 0

def bring_browser_to_foreground(browser_name):
    """Ultra-fast browser focusing - bypasses slow process enumeration"""
    try:
        import time
        start_time = time.time()
        print(f"[PERF] Starting ULTRA-FAST browser focus for {browser_name}")
        
        # Skip process enumeration entirely - directly find browser windows
        success = _find_and_focus_browser_window_direct(browser_name)
        
        total_time = time.time() - start_time
        if success:
            print(f"[PERF] ULTRA-FAST SUCCESS: Total={total_time:.3f}s")
        else:
            print(f"[PERF] ULTRA-FAST FAILED: Total={total_time:.3f}s")
        return success
        
    except Exception as e:
        total_time = time.time() - start_time
        print(f"[PERF] ULTRA-FAST ERROR after {total_time:.3f}s: {e}")
        return False

def _find_and_focus_browser_window_direct(browser_name):
    """Find browser window directly without process enumeration"""
    try:
        import time
        start_time = time.time()
        
        # Map browser names to window class names and titles
        browser_patterns = {
            'Chrome': {'classes': ['Chrome_WidgetWin_1'], 'title_contains': ['Google Chrome', 'Chrome']},
            'Firefox': {'classes': ['MozillaWindowClass'], 'title_contains': ['Mozilla Firefox', 'Firefox']},
            'Brave': {'classes': ['Chrome_WidgetWin_1'], 'title_contains': ['Brave']},
            'Opera': {'classes': ['Chrome_WidgetWin_1'], 'title_contains': ['Opera']},
            'Opera GX': {'classes': ['Chrome_WidgetWin_1'], 'title_contains': ['Opera GX']},
            'Edge': {'classes': ['Chrome_WidgetWin_1'], 'title_contains': ['Microsoft Edge', 'Edge']},
        }
        
        patterns = browser_patterns.get(browser_name, {'classes': [], 'title_contains': [browser_name]})
        
        # Find browser window directly
        browser_window = None
        
        def enum_windows_callback(hwnd, lParam):
            nonlocal browser_window
            if not user32.IsWindowVisible(hwnd):
                return True
                
            # Get window title
            title_length = user32.GetWindowTextLengthW(hwnd)
            if title_length == 0:
                return True
                
            title_buffer = ctypes.create_unicode_buffer(title_length + 1)
            user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
            window_title = title_buffer.value
            
            # Check if this looks like a browser window
            for title_pattern in patterns['title_contains']:
                if title_pattern.lower() in window_title.lower():
                    # Additional check: make sure it's a main window (has meaningful title)
                    if len(window_title.strip()) > 5:  # Not just "Chrome" but has page title
                        browser_window = hwnd
                        return False  # Stop enumeration
            
            return True
        
        enum_start = time.time()
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
        enum_time = time.time() - enum_start
        print(f"[PERF] Direct window search took {enum_time:.3f}s")
        
        if browser_window:
            focus_start = time.time()
            # Ultra-fast focusing
            if user32.IsIconic(browser_window):
                user32.ShowWindow(browser_window, SW_RESTORE)
            
            user32.SetForegroundWindow(browser_window)
            user32.BringWindowToTop(browser_window)
            
            focus_time = time.time() - focus_start
            total_time = time.time() - start_time
            print(f"[PERF] Direct focus: search={enum_time:.3f}s, focus={focus_time:.3f}s, total={total_time:.3f}s")
            return True
        
        total_time = time.time() - start_time
        print(f"[PERF] No browser window found after {total_time:.3f}s")
        return False
        
    except Exception as e:
        print(f"[PERF] Error in direct window search: {e}")
        return False

def _focus_browser_window_fast(pid):
    """Fast window focusing for a specific PID"""
    try:
        import time
        start_time = time.time()
        print(f"[PERF] Focusing window for PID {pid}")
        
        # Use a more efficient approach - find the main window directly
        main_window = None
        
        def enum_windows_callback(hwnd, lParam):
            nonlocal main_window
            if user32.IsWindowVisible(hwnd):
                window_pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
                if window_pid.value == pid:
                    # Check if this is likely the main browser window
                    window_text_length = user32.GetWindowTextLengthW(hwnd)
                    if window_text_length > 0:  # Has a title, likely main window
                        main_window = hwnd
                        return False  # Stop enumeration
            return True
        
        enum_start = time.time()
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
        enum_time = time.time() - enum_start
        print(f"[PERF] Window enumeration took {enum_time:.3f}s")
        
        if main_window:
            focus_start = time.time()
            # Fast window activation sequence
            if user32.IsIconic(main_window):
                user32.ShowWindow(main_window, SW_RESTORE)
            
            # Use the most direct approach for instant focusing
            user32.SetForegroundWindow(main_window)
            user32.BringWindowToTop(main_window)
            focus_time = time.time() - focus_start
            total_time = time.time() - start_time
            print(f"[PERF] Window focus: enum={enum_time:.3f}s, focus={focus_time:.3f}s, total={total_time:.3f}s")
            return True
        
        total_time = time.time() - start_time
        print(f"[PERF] No main window found after {total_time:.3f}s")
        return False
    except Exception as e:
        print(f"Error in fast window focus: {e}")
        return False

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
        print(f"Client connected. Total clients: {len(self.clients)}")
        self.logger.info(f"Client connected. Total clients: {len(self.clients)}")
        await self.send_all_tabs(websocket)

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        self.logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def send_all_tabs(self, websocket):
        print(f"Sending all tabs to client. Browser tabs available: {list(self.browser_tabs.keys())}")
        if self.browser_tabs:
            # Combine all tabs from all browsers while preserving their browser type
            all_tabs = []
            for browser_type, tabs in self.browser_tabs.items():
                # Ensure each tab has the correct browser type
                for tab in tabs:
                    tab['browser'] = browser_type
                all_tabs.extend(tabs)
            
            print(f"Sending {len(all_tabs)} tabs to client")
            await websocket.send(json.dumps({
                "type": "tabs_update",
                "tabs": all_tabs,
                "browsers": list(self.browser_tabs.keys())  # This will now include both Opera and Opera GX
            }))
        else:
            print("No browser tabs available to send")

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
            # Find which browser this tab belongs to
            tab_id = data.get("tabId")
            target_browser = None
            
            # Search through all browsers to find the tab
            for browser_name, tabs in self.browser_tabs.items():
                for tab in tabs:
                    if tab.get('id') == tab_id:
                        target_browser = browser_name
                        break
                if target_browser:
                    break
            
            # Bring the browser to foreground
            if target_browser:
                print(f"Bringing {target_browser} to foreground for tab {tab_id}")
                bring_browser_to_foreground(target_browser)
            
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
        print(f"Attempting to start WebSocket server on {host}:{port}")
        try:
            server = await websockets.serve(
                self.handler, 
                host, 
                port, 
                ping_interval=None,
                ping_timeout=None,
                logger=None  # Disable internal websockets logger
            )
            print(f"WebSocket server successfully started at ws://{host}:{port}")
            self.logger.info(f"WebSocket server started at ws://{host}:{port}")
            await server.wait_closed()
        except Exception as e:
            print(f"Failed to start WebSocket server: {e}")
            self.logger.error(f"Failed to start WebSocket server: {e}")
            raise