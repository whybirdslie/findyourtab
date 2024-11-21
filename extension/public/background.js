console.log('Background script loaded');

let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

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

async function sendCurrentTabs() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;

  try {
    const tabs = await chrome.tabs.query({});
    const formattedTabs = tabs.map(tab => ({
      id: tab.id,
      title: tab.title,
      url: tab.url,
      favIconUrl: tab.favIconUrl,
      windowId: tab.windowId
    }));

    ws.send(JSON.stringify({
      type: 'tabs_update',
      tabs: formattedTabs
    }));
  } catch (error) {
    console.error('Error sending tabs:', error);
  }
}

// Connect to WebSocket server
connectWebSocket();

// Update tabs periodically
setInterval(sendCurrentTabs, 5000);

// Listen for tab changes
chrome.tabs.onCreated.addListener(sendCurrentTabs);
chrome.tabs.onRemoved.addListener(sendCurrentTabs);
chrome.tabs.onUpdated.addListener(sendCurrentTabs);
chrome.tabs.onMoved.addListener(sendCurrentTabs);