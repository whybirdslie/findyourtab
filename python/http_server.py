from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

class ExtensionHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/popup.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>FindYourTab</title>
                <style>
                    body {
                        margin: 0;
                        padding: 20px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: rgba(255, 255, 255, 0.95);
                    }
                    .tab-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 10px;
                        margin-top: 10px;
                    }
                    .tab-item {
                        display: flex;
                        align-items: center;
                        gap: 10px;
                        padding: 8px;
                        background: white;
                        border-radius: 4px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                        cursor: pointer;
                    }
                    .tab-item:hover {
                        background: #f0f0f0;
                    }
                    .favicon {
                        width: 16px;
                        height: 16px;
                    }
                    h1 {
                        margin-top: 0;
                        margin-bottom: 20px;
                        color: #333;
                    }
                </style>
            </head>
            <body>
                <h1>Current Tabs</h1>
                <div id="tabList" class="tab-grid"></div>
                <script>
                    let ws = new WebSocket('ws://localhost:8765');
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        if (data.type === 'tabs_update') {
                            updateTabList(data.tabs);
                        }
                    };

                    ws.onclose = function() {
                        console.log('WebSocket connection closed');
                        setTimeout(() => {
                            ws = new WebSocket('ws://localhost:8765');
                        }, 1000);
                    };

                    function updateTabList(tabs) {
                        const tabList = document.getElementById('tabList');
                        tabList.innerHTML = '';
                        
                        tabs.forEach(tab => {
                            const tabElement = document.createElement('div');
                            tabElement.className = 'tab-item';
                            tabElement.onclick = () => {
                                ws.send(JSON.stringify({
                                    type: 'activate_tab',
                                    tabId: tab.id,
                                    windowId: tab.windowId
                                }));
                            };
                            
                            tabElement.innerHTML = `
                                <img src="${tab.favIconUrl || 'fallback.png'}" 
                                     class="favicon" 
                                     onerror="this.src='fallback.png'">
                                <span>${tab.title}</span>
                            `;
                            tabList.appendChild(tabElement);
                        });
                    }
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html_content.encode())

def start_http_server():
    server = HTTPServer(('localhost', 8000), ExtensionHandler)
    server.serve_forever()

def run_http_server():
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start() 