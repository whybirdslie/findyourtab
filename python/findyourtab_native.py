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

#!/usr/bin/env python3

import sys
import json
import asyncio
import webview
import keyboard
import threading
from websocket_server import TabWebSocketServer
from http_server import run_http_server

class TabFinder:
    def __init__(self):
        self.window = None
        self.is_visible = False
        self.webview_started = False
        print("TabFinder initialized", file=sys.stderr)
        
    def toggle_window(self):
        print("Toggling window visibility", file=sys.stderr)
        if self.is_visible:
            self.hide_window()
        else:
            self.show_window()

    def show_window(self):
        print("Attempting to show window", file=sys.stderr)
        try:
            if not self.window:
                print("Creating new webview window", file=sys.stderr)
                self.window = webview.create_window(
                    'FindYourTab',
                    'http://localhost:8000/popup.html',
                    width=800,
                    height=600,
                    resizable=True,
                    frameless=False,
                    transparent=False,
                    on_top=True,
                    min_size=(400, 300)
                )
                if self.window:
                    print("Window created successfully", file=sys.stderr)
                    self.is_visible = True
                    return True
                else:
                    print("Failed to create window", file=sys.stderr)
                    return False
            else:
                print("Showing existing window", file=sys.stderr)
                self.window.show()
                self.is_visible = True
                return True
        except Exception as e:
            print(f"Error showing window: {e}", file=sys.stderr)
            return False

    def hide_window(self):
        if self.window:
            self.window.hide()
            self.is_visible = False

def run_websocket(ws_server):
    print("Starting websocket server...", file=sys.stderr)
    asyncio.run(ws_server.start_server())

def main():
    # Start HTTP server
    print("Starting HTTP server...", file=sys.stderr)
    run_http_server()

    # Create instances
    tab_finder = TabFinder()
    ws_server = TabWebSocketServer()

    # Start WebSocket server in a separate thread
    ws_thread = threading.Thread(target=run_websocket, args=(ws_server,))
    ws_thread.daemon = True
    ws_thread.start()

    # Register hotkey
    print("Registering hotkey...", file=sys.stderr)
    keyboard.add_hotkey('ctrl+alt+f', tab_finder.toggle_window)

    # Create initial window (hidden) and ensure it's created before starting
    if tab_finder.show_window():
        # Start webview only if window creation was successful
        print("Starting webview...", file=sys.stderr)
        webview.start(debug=False)
    else:
        print("Failed to create window, exiting...", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting FindYourTab", file=sys.stderr)
        sys.exit(0)