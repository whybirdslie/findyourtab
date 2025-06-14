console.log('Background script loaded');

let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = Infinity;
let updateTimeout = null;
let reconnectInterval = null;

function connectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) return;

  console.log('Attempting to connect to WebSocket server...');
  ws = new WebSocket('ws://localhost:8765');

  ws.onopen = () => {
    console.log('Connected to WebSocket server');
    reconnectAttempts = 0;
    clearInterval(reconnectInterval);
    reconnectInterval = null;
    sendCurrentTabs();
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket connection closed');
    if (!reconnectInterval) {
      reconnectInterval = setInterval(() => {
        reconnectAttempts++;
        console.log(`Reconnection attempt ${reconnectAttempts}`);
        connectWebSocket();
      }, 2000);
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
        const response = await fetch(favIconUrl);
        const blob = await response.blob();
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.readAsDataURL(blob);
        });
    } catch (error) {
        console.log('Error converting icon to data URL:', error);
        return null;
    }
}

async function sendCurrentTabs() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    try {
        const tabs = await chrome.tabs.query({});
        const currentBrowser = await detectCurrentBrowser();
        console.log('Detected browser:', currentBrowser);
        
        // Get icon data URLs
        const formattedTabs = await Promise.all(tabs.map(async tab => ({
            id: tab.id,
            title: tab.title,
            url: tab.url,
            favIconUrl: await getIconDataUrl(tab.favIconUrl) || tab.favIconUrl,
            windowId: tab.windowId,
            browser: currentBrowser
        })));

        ws.send(JSON.stringify({
            type: 'tabs_update',
            tabs: formattedTabs,
            browser: currentBrowser
        }));
    } catch (error) {
        console.error('Error sending tabs:', error);
    }
}

function debouncedSendTabs() {
  if (updateTimeout) {
    clearTimeout(updateTimeout);
  }
  updateTimeout = setTimeout(sendCurrentTabs, 1000);
}

// Connect to WebSocket server
connectWebSocket();

// Update tabs every 10 seconds if connected
setInterval(() => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    debouncedSendTabs();
  }
}, 10000);

// Listen for tab changes
chrome.tabs.onCreated.addListener(debouncedSendTabs);
chrome.tabs.onRemoved.addListener(debouncedSendTabs);
chrome.tabs.onUpdated.addListener(debouncedSendTabs);
chrome.tabs.onMoved.addListener(debouncedSendTabs);