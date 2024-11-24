/* global chrome */

import React, { useState, useEffect, useRef } from 'react';
import './index.css';
import fallbackIcon from './fallback.svg';

function App() {
  const [tabs, setTabs] = useState([]);
  const [whiteIcons, setWhiteIcons] = useState({});
  const [wsConnected, setWsConnected] = useState(false);
  const canvasRef = useRef(document.createElement('canvas'));
  const wsRef = useRef(null);

  const detectBrowser = (url) => {
    if (url.includes('chrome-extension://')) return 'Chrome';
    if (url.includes('brave-extension://')) return 'Brave';
    if (url.includes('opera-extension://')) {
      // Check for Opera GX specific features
      if (window.navigator.userAgent.includes('GX')) {
        return 'Opera GX';
      }
      return 'Opera';
    }
    
    // Fallback detection based on user agent
    const userAgent = window.navigator.userAgent;
    if (userAgent.includes('OPR/')) {
      return userAgent.includes('GX') ? 'Opera GX' : 'Opera';
    }
    
    return window.navigator.userAgent.includes('Chrome') ? 'Chrome' : 'Unknown';
  };

  const getCurrentBrowser = () => {
    // Detect current browser based on the extension URL
    const currentUrl = window.location.href;
    return detectBrowser(currentUrl);
  };

  const fetchTabsDirectly = async () => {
    try {
      const chromeTabs = await chrome.tabs.query({});
      const currentBrowser = getCurrentBrowser();
      
      const formattedTabs = chromeTabs
        .map(tab => ({
          id: tab.id,
          title: tab.title,
          url: tab.url,
          favIconUrl: tab.favIconUrl,
          windowId: tab.windowId,
          browser: currentBrowser
        }));
      
      setTabs(formattedTabs);
    } catch (error) {
      console.error('Error fetching tabs directly:', error);
    }
  };

  const handleTabClick = async (tabId) => {
    const tab = tabs.find(t => t.id === tabId);
    if (!tab) return;

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // If WebSocket is connected, send through WebSocket
      wsRef.current.send(JSON.stringify({
        type: 'activate_tab',
        tabId: tab.id,
        windowId: tab.windowId
      }));
    } else {
      // Fallback to direct Chrome API
      try {
        await chrome.tabs.update(tabId, { active: true });
        await chrome.windows.update(tab.windowId, { focused: true });
      } catch (error) {
        console.error('Error activating tab:', error);
      }
    }
  };

  const handleWebSocketMessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'tabs_update') {
      const currentBrowser = getCurrentBrowser();
      // Only update tabs if they're from the same browser
      if (data.browser === currentBrowser) {
        setTabs(data.tabs);
      }
    }
  };

  const connectWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    console.log('Connecting to WebSocket from popup...');
    wsRef.current = new WebSocket('ws://localhost:8765');

    wsRef.current.onopen = () => {
      console.log('Popup connected to WebSocket server');
      setWsConnected(true);
    };

    wsRef.current.onmessage = handleWebSocketMessage;

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error in popup:', error);
      setWsConnected(false);
      fetchTabsDirectly();
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket connection closed in popup');
      setWsConnected(false);
      fetchTabsDirectly();
      setTimeout(connectWebSocket, 1000);
    };
  };

  useEffect(() => {
    // Initial tab fetch using Chrome API
    fetchTabsDirectly();

    // Set up tab update listeners
    const updateTabs = () => fetchTabsDirectly();
    chrome.tabs.onCreated.addListener(updateTabs);
    chrome.tabs.onRemoved.addListener(updateTabs);
    chrome.tabs.onUpdated.addListener(updateTabs);
    chrome.tabs.onMoved.addListener(updateTabs);

    // Try to connect to WebSocket
    connectWebSocket();

    // Cleanup
    return () => {
      chrome.tabs.onCreated.removeListener(updateTabs);
      chrome.tabs.onRemoved.removeListener(updateTabs);
      chrome.tabs.onUpdated.removeListener(updateTabs);
      chrome.tabs.onMoved.removeListener(updateTabs);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleImageError = (e) => {
    e.target.onerror = null;
    e.target.src = fallbackIcon;
  };

  const isIconWhite = (imgElement) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    canvas.width = imgElement.width;
    canvas.height = imgElement.height;

    try {
      ctx.drawImage(imgElement, 0, 0);
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
  };

  useEffect(() => {
    tabs.forEach(tab => {
      if (tab.favIconUrl) {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
          setWhiteIcons(prev => ({
            ...prev,
            [tab.id]: isIconWhite(img)
          }));
        };
        img.onerror = () => {
          setWhiteIcons(prev => ({
            ...prev,
            [tab.id]: false
          }));
        };
        img.src = tab.favIconUrl;
      }
    });
  }, [tabs]);

  return (
    <div className="App">
      <div className="header-container">
        <div className="header-left">
          <h1>Current Tabs</h1>
          <div className={`connection-status ${wsConnected ? 'connected' : 'offline'}`}>
            {wsConnected ? 'Connected' : 'Offline Mode'}
          </div>
        </div>
      </div>
      <div className="tab-grid">
        {tabs.map((tab) => (
          <div
            key={tab.id}
            className="tab-item"
            onClick={() => handleTabClick(tab.id)}
          >
            <img
              src={tab.favIconUrl || fallbackIcon}
              alt="Favicon"
              className={`favicon ${whiteIcons[tab.id] ? 'recolor-black' : ''}`}
              onError={handleImageError}
            />
            <span>{tab.title}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;