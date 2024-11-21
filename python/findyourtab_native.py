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
                    width=600,
                    height=400,
                    resizable=True,
                    frameless=True,
                    transparent=True,
                    on_top=True
                )
                self.is_visible = True
            else:
                print("Showing existing window", file=sys.stderr)
                self.window.show()
                self.is_visible = True
        except Exception as e:
            print(f"Error showing window: {e}", file=sys.stderr)

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

    # Create initial window (hidden)
    tab_finder.show_window()

    # Start webview
    print("Starting webview...", file=sys.stderr)
    webview.start(debug=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting FindYourTab", file=sys.stderr)
        sys.exit(0)