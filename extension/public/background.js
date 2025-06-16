/*
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
*/

console.log('Background script loaded');

let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = Infinity;
let updateTimeout = null;
let reconnectInterval = null;
let isConnecting = false;

function connectWebSocket() {
    if (isConnecting) return;
    if (ws && ws.readyState === WebSocket.OPEN) return;

    isConnecting = true;
    console.log('Attempting to connect to WebSocket server...');
    
    // Close existing connection if any
    if (ws) {
        try {
            ws.close();
        } catch (err) {
            console.log('Error closing existing connection:', err);
        }
    }

    ws = new WebSocket('ws://localhost:8765');

    ws.onopen = () => {
        console.log('Connected to WebSocket server');
        reconnectAttempts = 0;
        clearInterval(reconnectInterval);
        reconnectInterval = null;
        isConnecting = false;
        sendCurrentTabs(); // Send tabs immediately upon connection
    };

    ws.onerror = (error) => {
        console.log('WebSocket error:', error);
        isConnecting = false;
    };

    ws.onclose = () => {
        console.log('WebSocket connection closed');
        isConnecting = false;
        
        // Start reconnection attempts immediately
        if (!reconnectInterval) {
            reconnectInterval = setInterval(() => {
                reconnectAttempts++;
                console.log(`Reconnection attempt ${reconnectAttempts}`);
                connectWebSocket();
            }, 1000); // Try every second instead of every 2 seconds
        }
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'activate_tab') {
            chrome.tabs.update(data.tabId, { active: true });
            chrome.windows.update(data.windowId, { focused: true });
        }
    };
}

async function detectCurrentBrowser() {
  try {
    const extensionUrl = chrome.runtime.getURL('');
    console.log('Extension URL:', extensionUrl);
    console.log('User Agent:', navigator.userAgent);

    // Firefox detection
    if (typeof browser !== 'undefined' && browser.runtime) {
      return 'Firefox';
    }

    // Check for Opera GX and Opera
    if (navigator.userAgent.includes('OPR/')) {
      return navigator.userAgent.includes('GX') ? 'Opera GX' : 'Opera';
    }

    // Check for Edge
    if (navigator.userAgent.includes('Edg/')) {
      return 'Edge';
    }

    // Primary Brave detection using native API
    if (navigator.brave && typeof navigator.brave.isBrave === 'function') {
      const isBrave = await navigator.brave.isBrave();
      if (isBrave) {
        return 'Brave';
      }
    }

    // Extension URL based detection
    if (extensionUrl.includes('chrome-extension://')) {
      return 'Chrome';
    } else if (extensionUrl.includes('brave-extension://')) {
      return 'Brave';
    } else if (extensionUrl.includes('opera-extension://')) {
      return navigator.userAgent.includes('GX') ? 'Opera GX' : 'Opera';
    } else if (extensionUrl.includes('moz-extension://')) {
      return 'Firefox';
    }

    console.log('Browser detection details:', {
      extensionUrl,
      userAgent: navigator.userAgent
    });

    return 'Unknown';
  } catch (error) {
    console.error('Error in browser detection:', error);
    return 'Unknown';
  }
}

async function getIconDataUrl(favIconUrl) {
    if (!favIconUrl) return null;
    
    try {
        // For extension URLs or data URLs, use them directly
        if (favIconUrl.startsWith('chrome-extension://') || 
            favIconUrl.startsWith('moz-extension://') || 
            favIconUrl.startsWith('edge-extension://') ||
            favIconUrl.startsWith('data:')) {
            return favIconUrl;
        }

        // Try to fetch with no-cors mode
        const response = await fetch(favIconUrl, {
            mode: 'no-cors',
            cache: 'force-cache',
            credentials: 'omit'
        }).catch(() => null);  // Silently catch fetch errors

        // If fetch fails or response is not ok, return original URL
        if (!response) return favIconUrl;

        // Try to convert to blob
        const blob = await response.blob().catch(() => null);
        if (!blob) return favIconUrl;

        // Convert blob to data URL
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result || favIconUrl);
            reader.onerror = () => resolve(favIconUrl);  // On error, use original URL
            reader.readAsDataURL(blob);
        });
    } catch (error) {
        // Silently handle any errors and return original URL
        return favIconUrl;
    }
}

async function sendCurrentTabs() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    try {
        const tabs = await chrome.tabs.query({});
        const currentBrowser = await detectCurrentBrowser();
        
        // Process tabs without logging errors
        const formattedTabs = await Promise.all(tabs.map(async tab => ({
            id: tab.id,
            title: tab.title,
            url: tab.url,
            favIconUrl: tab.favIconUrl,  // Use original URL directly
            windowId: tab.windowId,
            browser: currentBrowser
        })));

        ws.send(JSON.stringify({
            type: 'tabs_update',
            tabs: formattedTabs,
            browser: currentBrowser
        }));
    } catch (error) {
        // Only log critical errors
        if (error.message !== 'Failed to fetch') {
            console.error('Error sending tabs:', error);
        }
    }
}

function debouncedSendTabs() {
  if (updateTimeout) {
    clearTimeout(updateTimeout);
  }
  updateTimeout = setTimeout(sendCurrentTabs, 1000);
}

// Connect to WebSocket server immediately when the background script loads
connectWebSocket();

// Try to reconnect periodically if not connected
setInterval(() => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        connectWebSocket();
    }
}, 1000);

// Update tabs every 5 seconds if connected (reduced from 10 seconds)
setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        debouncedSendTabs();
    }
}, 5000);

// Listen for tab changes
chrome.tabs.onCreated.addListener(debouncedSendTabs);
chrome.tabs.onRemoved.addListener(debouncedSendTabs);
chrome.tabs.onUpdated.addListener(debouncedSendTabs);
chrome.tabs.onMoved.addListener(debouncedSendTabs);

// Add listener for extension startup
chrome.runtime.onStartup.addListener(() => {
    console.log('Extension starting up, connecting to WebSocket...');
    connectWebSocket();
});

// Add listener for extension installation/update
chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension installed/updated, connecting to WebSocket...');
    connectWebSocket();
});