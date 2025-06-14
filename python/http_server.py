from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os
import sys
import urllib.parse
import urllib.request
import base64
from pathlib import Path

class ExtensionHandler(SimpleHTTPRequestHandler):
    favicon_cache = {}
    
    def get_static_file_path(self, filename):
        """Get the correct path for static files in both development and executable environments"""
        import sys
        import os
        
        if getattr(sys, 'frozen', False):
            # Running as executable - PyInstaller bundles files in sys._MEIPASS
            base_path = sys._MEIPASS
        else:
            # Running as script - use current directory
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(base_path, 'static', filename)
    
    def do_GET(self):
        if self.path.startswith('/proxy-favicon?url='):
            try:
                # Extract the original favicon URL
                favicon_url = self.path.split('url=')[1]
                favicon_url = urllib.parse.unquote(favicon_url)
                
                # Check cache first
                if favicon_url in self.favicon_cache:
                    cached_data = self.favicon_cache[favicon_url]
                    self.send_response(200)
                    self.send_header('Content-type', cached_data['content_type'])
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(base64.b64decode(cached_data['data']))
                    return
                
                # Create headers with a fake user agent
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # Make the request to get the favicon
                req = urllib.request.Request(favicon_url, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as response:
                    content_type = response.headers.get('Content-type', 'image/x-icon')
                    icon_data = response.read()
                    
                    # Cache the favicon
                    self.favicon_cache[favicon_url] = {
                        'content_type': content_type,
                        'data': base64.b64encode(icon_data).decode('utf-8')
                    }
                    
                    # Send response
                    self.send_response(200)
                    self.send_header('Content-type', content_type)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(icon_data)
                    
            except Exception as e:
                print(f"Error proxying favicon: {e}")
                self.send_error(404)
                
        elif self.path == '/popup.html':
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
                        max-width: 100%;
                        margin: 0 auto;
                        height: calc(100vh - 40px);
                        overflow-y: auto;
                        -webkit-app-region: no-drag;
                        padding-right: 8px;
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
                        font-size: 24px;
                        color: #333;
                        align-self: center;
                    }
                    .connection-status {
                        font-size: 12px;
                        padding: 4px 8px;
                        border-radius: 4px;
                        margin-left: 10px;
                        align-self: center;
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
                        object-fit: contain;
                        transition: none;
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
                    .browser-section {
                        margin-bottom: 20px;
                    }
                    .browser-header {
                        font-size: 16px;
                        color: #666;
                        margin: 10px 0;
                        padding-bottom: 5px;
                        border-bottom: 1px solid #eee;
                    }
                    .search-container {
                        position: sticky;
                        top: 0;
                        background: white;
                        padding: 10px 0;
                        margin-bottom: 15px;
                        z-index: 1000;
                        width: 100%;
                        min-width: 200px;
                        margin-left: 0;
                        margin-right: auto;
                    }
                    
                    .search-input {
                        width: 100%;
                        padding: 8px 12px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 14px;
                        outline: none;
                        transition: border-color 0.2s;
                        box-sizing: border-box;
                    }
                    
                    .search-input:focus {
                        border-color: #4CAF50;
                    }
                    
                    .tab-item.hidden {
                        display: none;
                    }
                    
                    .highlight {
                        background-color: #fff3cd;
                        padding: 2px;
                        border-radius: 2px;
                    }
                    /* Style the scrollbar track */
                    #container::-webkit-scrollbar {
                        width: 8px;  // Width of the scrollbar
                    }

                    /* Style the scrollbar thumb */
                    #container::-webkit-scrollbar-thumb {
                        background: #c1c1c1;
                        border-radius: 4px;
                    }

                    /* Style the scrollbar track on hover */
                    #container::-webkit-scrollbar-track {
                        background: #f1f1f1;
                    }

                    /* When scrollbar is present, adjust the padding */
                    @media (overflow-y: scroll) {
                        #container {
                            padding-right: 16px;  // More padding when scrollbar appears
                        }
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
                    
                    <div class="search-container">
                        <input type="text" 
                               class="search-input" 
                               id="searchInput" 
                               placeholder="Search tabs..."
                               autofocus>
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
                    let availableBrowsers = new Set(['all']);
                    
                    function detectBrowser(tab) {
                        if (tab.url.includes('chrome-extension://')) return 'Chrome';
                        if (tab.url.includes('brave-extension://')) return 'Brave';
                        return 'Unknown';
                    }

                    function updateBrowserFilters(browsers) {
                        const filtersContainer = document.getElementById('browserFilters');
                        filtersContainer.innerHTML = '';
                        
                        // Add 'All Browsers' filter
                        const allButton = document.createElement('button');
                        allButton.className = `browser-filter ${currentFilter === 'all' ? 'active' : ''}`;
                        allButton.textContent = 'All Browsers';
                        allButton.dataset.browser = 'all';
                        allButton.onclick = () => {
                            currentFilter = 'all';
                            document.querySelectorAll('.browser-filter').forEach(btn => 
                                btn.classList.toggle('active', btn.dataset.browser === 'all')
                            );
                            updateTabList(allTabs);
                        };
                        filtersContainer.appendChild(allButton);
                        
                        // Add browser-specific filters
                        browsers.forEach(browser => {
                            if (browser !== 'all') {
                                const button = document.createElement('button');
                                button.className = `browser-filter ${currentFilter === browser ? 'active' : ''}`;
                                button.textContent = browser;
                                button.dataset.browser = browser;
                                button.onclick = () => {
                                    currentFilter = browser;
                                    document.querySelectorAll('.browser-filter').forEach(btn => 
                                        btn.classList.toggle('active', btn.dataset.browser === browser)
                                    );
                                    updateTabList(allTabs);
                                };
                                filtersContainer.appendChild(button);
                            }
                        });
                    }

                    function isIconWhite(img) {
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        
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
                                    if (r > 245 && g > 245 && b > 245) {
                                        whitePixels++;
                                    }
                                }
                            }
                            
                            return totalPixels > 0 && whitePixels / totalPixels > 0.9;
                        } catch (error) {
                            console.log('Error analyzing icon:', error);
                            return false;
                        } finally {
                            canvas.remove();
                        }
                    }

                    function checkIfWhiteIcon(tab) {
                        if (!tab.favIconUrl) return;
                        
                        // Create a proxy URL for the favicon through our server
                        const proxyUrl = `/proxy-favicon?url=${encodeURIComponent(tab.favIconUrl)}`;
                        
                        const img = new Image();
                        img.onload = () => {
                            const isWhite = isIconWhite(img);
                            whiteIcons.set(tab.id, isWhite);
                            updateTabList(allTabs);
                        };
                        img.onerror = () => {
                            whiteIcons.set(tab.id, false);
                        };
                        img.src = proxyUrl;
                    }

                    function updateTabList(tabs) {
                        allTabs = tabs;
                        let filteredTabs;
                        
                        if (currentFilter === 'all') {
                            // For 'all' view, combine all tabs and sort by browser and title
                            filteredTabs = tabs.sort((a, b) => {
                                // First sort by browser
                                const browserCompare = a.browser.localeCompare(b.browser);
                                if (browserCompare !== 0) return browserCompare;
                                // Then by title within each browser
                                return a.title.localeCompare(b.title);
                            });
                        } else {
                            // For specific browser view, filter and sort by title
                            filteredTabs = tabs
                                .filter(tab => tab.browser === currentFilter)
                                .sort((a, b) => a.title.localeCompare(b.title));
                        }
                        
                        const tabList = document.getElementById('tabList');
                        tabList.innerHTML = '';
                        
                        if (currentFilter === 'all') {
                            // Group tabs by browser
                            const browserGroups = {};
                            filteredTabs.forEach(tab => {
                                if (!browserGroups[tab.browser]) {
                                    browserGroups[tab.browser] = [];
                                }
                                browserGroups[tab.browser].push(tab);
                            });
                            
                            // Create sections for each browser
                            Object.entries(browserGroups).forEach(([browser, browserTabs]) => {
                                const browserSection = document.createElement('div');
                                browserSection.className = 'browser-section';
                                
                                const browserHeader = document.createElement('div');
                                browserHeader.className = 'browser-header';
                                browserHeader.textContent = browser;
                                browserSection.appendChild(browserHeader);
                                
                                const tabsContainer = document.createElement('div');
                                tabsContainer.className = 'browser-tabs';
                                
                                browserTabs.forEach(tab => {
                                    const tabElement = createTabElement(tab);
                                    tabsContainer.appendChild(tabElement);
                                });
                                
                                browserSection.appendChild(tabsContainer);
                                tabList.appendChild(browserSection);
                            });
                        } else {
                            // Regular tab list for specific browser view
                            filteredTabs.forEach(tab => {
                                const tabElement = createTabElement(tab);
                                tabList.appendChild(tabElement);
                            });
                        }
                    }
                    
                    function createTabElement(tab) {
                        const tabElement = document.createElement('div');
                        tabElement.className = 'tab-item';
                        tabElement.onclick = () => {
                            ws.send(JSON.stringify({
                                type: 'activate_tab',
                                tabId: tab.id,
                                windowId: tab.windowId
                            }));
                        };
                        
                        // Create image element with explicit size
                        const imgElement = document.createElement('img');
                        imgElement.width = 16;
                        imgElement.height = 16;
                        
                        if (tab.favIconUrl) {
                            // Use our proxy for external URLs
                            const proxyUrl = `/proxy-favicon?url=${encodeURIComponent(tab.favIconUrl)}`;
                            imgElement.src = proxyUrl;
                            
                            // Analyze the icon
                            const testImg = new Image();
                            testImg.onload = () => {
                                const isWhite = isIconWhite(testImg);
                                if (isWhite) {
                                    imgElement.classList.add('recolor-black');
                                }
                            };
                            testImg.src = proxyUrl;
                        } else {
                            imgElement.src = '/static/fallback.svg';
                        }
                        
                        imgElement.className = 'favicon';
                        imgElement.onerror = function() {
                            this.src = '/static/fallback.svg';
                        };
                        
                        const titleSpan = document.createElement('span');
                        titleSpan.className = 'tab-title';
                        titleSpan.textContent = tab.title;
                        
                        const browserLabel = document.createElement('span');
                        browserLabel.className = 'browser-label';
                        browserLabel.textContent = tab.browser;
                        
                        tabElement.appendChild(imgElement);
                        tabElement.appendChild(titleSpan);
                        tabElement.appendChild(browserLabel);
                        
                        return tabElement;
                    }

                    // Add styles for browser sections
                    const style = document.createElement('style');
                    style.textContent = `
                        .browser-section {
                            margin-bottom: 20px;
                        }
                        .browser-header {
                            font-size: 14px;
                            color: #666;
                            padding: 8px;
                            background: #f5f5f5;
                            border-radius: 4px;
                            margin-bottom: 10px;
                        }
                        .browser-tabs {
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                            gap: 10px;
                        }
                    `;
                    document.head.appendChild(style);

                    ws.onopen = function() {
                        connectionStatus.textContent = 'Connected';
                        connectionStatus.classList.remove('offline');
                        connectionStatus.classList.add('connected');
                    };

                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        if (data.type === 'tabs_update') {
                            updateBrowserFilters(data.browsers || ['all']);
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

                    const searchInput = document.getElementById('searchInput');
                    
                    function highlightText(text, searchTerm) {
                        if (!searchTerm) return text;
                        const regex = new RegExp(`(${searchTerm})`, 'gi');
                        return text.replace(regex, '<span class="highlight">$1</span>');
                    }
                    
                    function filterTabs() {
                        const searchTerm = searchInput.value.toLowerCase();
                        const tabElements = document.querySelectorAll('.tab-item');
                        
                        tabElements.forEach(tabElement => {
                            const title = tabElement.querySelector('.tab-title').textContent.toLowerCase();
                            const matches = title.includes(searchTerm);
                            
                            if (matches) {
                                tabElement.classList.remove('hidden');
                                // Highlight matching text
                                const titleElement = tabElement.querySelector('.tab-title');
                                titleElement.innerHTML = highlightText(titleElement.textContent, searchTerm);
                            } else {
                                tabElement.classList.add('hidden');
                            }
                        });
                    }
                    
                    searchInput.addEventListener('input', filterTabs);
                    searchInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            const visibleTabs = document.querySelectorAll('.tab-item:not(.hidden)');
                            if (visibleTabs.length > 0) {
                                visibleTabs[0].click();
                            }
                        }
                    });
                    
                    const originalUpdateTabList = updateTabList;
                    updateTabList = function(tabs) {
                        originalUpdateTabList(tabs);
                        filterTabs();
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
            
            # Get the correct path for both development and executable
            fallback_path = self.get_static_file_path('fallback.svg')
            with open(fallback_path, 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            
            # Get the correct path for both development and executable
            favicon_path = self.get_static_file_path('favicon.ico')
            with open(favicon_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

def start_http_server():
    # Ensure static directory exists (for development mode)
    if not getattr(sys, 'frozen', False):
        os.makedirs('static', exist_ok=True)
    
    server = HTTPServer(('localhost', 8000), ExtensionHandler)
    server.serve_forever()

def run_http_server():
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start() 