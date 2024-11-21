from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os

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
                        background: rgba(255, 255, 255, 1);
                        height: 100vh;
                        overflow-y: auto;
                        box-sizing: border-box;
                        user-select: none;
                        -webkit-user-select: none;
                        -webkit-app-region: no-drag;
                    }
                    #container {
                        max-width: 800px;
                        margin: 0 auto;
                        height: calc(100vh - 40px);
                        overflow-y: auto;
                        -webkit-app-region: no-drag;
                    }
                    .header-container {
                        display: flex;
                        justify-content: space-between;
                        align-items: baseline;
                        margin-bottom: 20px;
                        position: sticky;
                        top: 0;
                        background: rgba(255, 255, 255, 0.95);
                        padding: 10px 0;
                        z-index: 1000;
                    }
                    .header-left {
                        display: flex;
                        align-items: baseline;
                        gap: 20px;
                    }
                    h1 {
                        margin: 0;
                        font-size: 20px;
                        color: #333;
                    }
                    .connection-status {
                        font-size: 12px;
                        padding: 4px 8px;
                        border-radius: 4px;
                        margin-left: 10px;
                    }
                    .connection-status.connected {
                        color: #4CAF50;
                        background-color: #E8F5E9;
                    }
                    .connection-status.offline {
                        color: #666;
                        background-color: #f0f0f0;
                    }
                    .browser-filters {
                        display: flex;
                        gap: 10px;
                        margin-bottom: 15px;
                    }
                    .browser-filter {
                        padding: 4px 12px;
                        border-radius: 4px;
                        border: 1px solid #ddd;
                        background: white;
                        cursor: pointer;
                        font-size: 12px;
                    }
                    .browser-filter.active {
                        background: #4CAF50;
                        color: white;
                        border-color: #4CAF50;
                    }
                    .tab-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 10px;
                        padding-bottom: 20px;
                        -webkit-app-region: no-drag;
                        pointer-events: auto !important;
                    }
                    .tab-item {
                        display: flex;
                        align-items: center;
                        gap: 10px;
                        padding: 12px;
                        background: white;
                        border-radius: 4px;
                        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                        cursor: pointer;
                        transition: background-color 0.2s ease;
                        overflow: hidden;
                        height: 20px;
                        -webkit-app-region: no-drag;
                        cursor: pointer !important;
                        pointer-events: auto !important;
                    }
                    .tab-item:hover {
                        background: #f0f0f0;
                    }
                    .favicon {
                        width: 16px;
                        height: 16px;
                        flex-shrink: 0;
                    }
                    .favicon.recolor-black {
                        filter: brightness(0) saturate(100%);
                    }
                    .tab-title {
                        flex: 1;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        font-size: 14px;
                    }
                    .browser-label {
                        font-size: 10px;
                        padding: 2px 6px;
                        border-radius: 3px;
                        background: #f0f0f0;
                        margin-left: 8px;
                    }
                </style>
            </head>
            <body>
                <div id="container">
                    <div class="header-container">
                        <div class="header-left">
                            <h1>Current Tabs</h1>
                            <div id="connectionStatus" class="connection-status offline">
                                Offline Mode
                            </div>
                        </div>
                    </div>
                    <div class="browser-filters" id="browserFilters">
                        <button class="browser-filter active" data-browser="all">All Browsers</button>
                    </div>
                    <div id="tabList" class="tab-grid"></div>
                </div>
                <script>
                    let ws = new WebSocket('ws://localhost:8765');
                    const whiteIcons = new Map();
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    let currentFilter = 'all';
                    let allTabs = [];
                    
                    function detectBrowser(tab) {
                        if (tab.url.includes('chrome-extension://')) return 'Chrome';
                        if (tab.url.includes('brave-extension://')) return 'Brave';
                        return 'Unknown';
                    }

                    function updateBrowserFilters(tabs) {
                        const browsers = new Set(['all']);
                        tabs.forEach(tab => browsers.add(detectBrowser(tab)));
                        
                        const filtersContainer = document.getElementById('browserFilters');
                        filtersContainer.innerHTML = '';
                        
                        browsers.forEach(browser => {
                            const button = document.createElement('button');
                            button.className = `browser-filter ${currentFilter === browser ? 'active' : ''}`;
                            button.textContent = browser === 'all' ? 'All Browsers' : browser;
                            button.dataset.browser = browser;
                            button.onclick = () => {
                                currentFilter = browser;
                                document.querySelectorAll('.browser-filter').forEach(btn => 
                                    btn.classList.toggle('active', btn.dataset.browser === browser)
                                );
                                updateTabList(allTabs);
                            };
                            filtersContainer.appendChild(button);
                        });
                    }

                    function isIconWhite(img) {
                        canvas.width = img.width;
                        canvas.height = img.height;
                        
                        try {
                            ctx.drawImage(img, 0, 0);
                            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                            const data = imageData.data;
                            
                            let whitePixels = 0;
                            let totalPixels = 0;
                            
                            for (let i = 0; i < data.length; i += 4) {
                                const r = data[i];
                                const g = data[i + 1];
                                const b = data[i + 2];
                                const a = data[i + 3];
                                
                                if (a > 0) {
                                    totalPixels++;
                                    if (r > 240 && g > 240 && b > 240) {
                                        whitePixels++;
                                    }
                                }
                            }
                            
                            return totalPixels > 0 && whitePixels / totalPixels > 0.9;
                        } catch (error) {
                            console.log('Error analyzing icon:', error);
                            return false;
                        }
                    }

                    function checkIfWhiteIcon(tab) {
                        if (tab.favIconUrl) {
                            const img = new Image();
                            img.crossOrigin = 'anonymous';
                            img.onload = () => {
                                const isWhite = isIconWhite(img);
                                whiteIcons.set(tab.id, isWhite);
                                updateTabList(allTabs); // Refresh the display
                            };
                            img.onerror = () => {
                                whiteIcons.set(tab.id, false);
                            };
                            img.src = tab.favIconUrl;
                        }
                    }

                    function updateTabList(tabs) {
                        allTabs = tabs;
                        const filteredTabs = currentFilter === 'all' 
                            ? tabs 
                            : tabs.filter(tab => detectBrowser(tab) === currentFilter);
                        
                        const tabList = document.getElementById('tabList');
                        tabList.innerHTML = '';
                        
                        updateBrowserFilters(tabs);
                        
                        filteredTabs.forEach(tab => {
                            const tabElement = document.createElement('div');
                            tabElement.className = 'tab-item';
                            tabElement.onclick = () => {
                                ws.send(JSON.stringify({
                                    type: 'activate_tab',
                                    tabId: tab.id,
                                    windowId: tab.windowId
                                }));
                            };
                            
                            const browser = detectBrowser(tab);
                            const isWhite = whiteIcons.get(tab.id);
                            
                            tabElement.innerHTML = `
                                <img src="${tab.favIconUrl || '/static/fallback.svg'}" 
                                     class="favicon ${isWhite ? 'recolor-black' : ''}" 
                                     onerror="this.src='/static/fallback.svg'">
                                <span class="tab-title">${tab.title}</span>
                                <span class="browser-label">${browser}</span>
                            `;
                            
                            tabList.appendChild(tabElement);
                            
                            if (!whiteIcons.has(tab.id)) {
                                checkIfWhiteIcon(tab);
                            }
                        });
                    }

                    ws.onopen = function() {
                        connectionStatus.textContent = 'Connected';
                        connectionStatus.classList.remove('offline');
                        connectionStatus.classList.add('connected');
                    };

                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        if (data.type === 'tabs_update') {
                            updateTabList(data.tabs);
                        }
                    };

                    ws.onclose = function() {
                        console.log('WebSocket connection closed');
                        connectionStatus.textContent = 'Offline Mode';
                        connectionStatus.classList.remove('connected');
                        connectionStatus.classList.add('offline');
                        setTimeout(() => {
                            ws = new WebSocket('ws://localhost:8765');
                        }, 1000);
                    };
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html_content.encode())
        elif self.path == '/static/fallback.svg':
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            
            with open('static/fallback.svg', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

def start_http_server():
    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    server = HTTPServer(('localhost', 8000), ExtensionHandler)
    server.serve_forever()

def run_http_server():
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start() 