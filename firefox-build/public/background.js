console.log('Background script loaded');

let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
let updateTimeout = null;

function connectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) return;

  console.log('Attempting to connect to WebSocket server...');
  ws = new WebSocket('ws://localhost:8765');

  ws.onopen = () => {
    console.log('Connected to WebSocket server');
    reconnectAttempts = 0;
    sendCurrentTabs();
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket connection closed');
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      setTimeout(connectWebSocket, 1000 * reconnectAttempts);
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

async function sendCurrentTabs() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;

  try {
    const tabs = await chrome.tabs.query({});
    const currentBrowser = await detectCurrentBrowser();
    console.log('Detected browser:', currentBrowser); // Debug log
    
    const formattedTabs = tabs.map(tab => ({
      id: tab.id,
      title: tab.title,
      url: tab.url,
      favIconUrl: tab.favIconUrl,
      windowId: tab.windowId,
      browser: currentBrowser
    }));

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

// Update tabs every 10 seconds
setInterval(debouncedSendTabs, 10000);

// Listen for tab changes
chrome.tabs.onCreated.addListener(debouncedSendTabs);
chrome.tabs.onRemoved.addListener(debouncedSendTabs);
chrome.tabs.onUpdated.addListener(debouncedSendTabs);
chrome.tabs.onMoved.addListener(debouncedSendTabs);