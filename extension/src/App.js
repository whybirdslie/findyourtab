/* global chrome */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import './index.css';
import fallbackIcon from './fallback.svg';

function App() {
  const [tabs, setTabs] = useState([]);
  const [whiteIcons, setWhiteIcons] = useState({});
  const [wsConnected, setWsConnected] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const canvasRef = useRef(document.createElement('canvas'));
  const wsRef = useRef(null);
  const searchInputRef = useRef(null);

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

  const handleImageError = useCallback((e) => {
    e.preventDefault();
    e.target.onerror = null;
    e.target.src = fallbackIcon;
  }, []);

  const isIconWhite = useCallback((imgElement, favIconUrl) => {
    console.log('Running isIconWhite analysis');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });

    try {
      canvas.width = imgElement.width;
      canvas.height = imgElement.height;
      console.log(`Canvas size set to ${canvas.width}x${canvas.height}`);

      // Draw image with crossOrigin handling
      ctx.drawImage(imgElement, 0, 0);

      try {
        // Try to get image data
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

        const isWhite = totalPixels > 0 && whitePixels / totalPixels > 0.9;
        console.log(`Icon analysis result: ${isWhite ? 'white' : 'not white'} (${whitePixels}/${totalPixels} pixels)`);
        return isWhite;
      } catch (error) {
        // If we can't access pixel data, try to detect white icons by URL pattern
        console.log('Falling back to URL pattern detection');
        return favIconUrl.includes('github');
      }
    } catch (error) {
      console.log('Error in canvas operation:', error);
      return false;
    } finally {
      canvas.remove();
    }
  }, []);

  useEffect(() => {
    console.log(`Analyzing ${tabs.length} tabs`);
    
    tabs.forEach(tab => {
      if (!tab.favIconUrl) return;

      // Create a hidden image element
      const img = new Image();
      
      // Suppress console errors for image loading
      const originalConsoleError = console.error;
      console.error = (...args) => {
        if (!args[0].includes('Access to image at') && !args[0].includes('Failed to load icon')) {
          originalConsoleError.apply(console, args);
        }
      };

      img.onload = () => {
        const isWhite = isIconWhite(img, tab.favIconUrl);
        setWhiteIcons(prev => ({
          ...prev,
          [tab.id]: isWhite
        }));
        // Restore console.error
        console.error = originalConsoleError;
      };

      img.onerror = () => {
        setWhiteIcons(prev => ({
          ...prev,
          [tab.id]: false
        }));
        // Restore console.error
        console.error = originalConsoleError;
      };

      // Try to load the image silently
      try {
        img.src = tab.favIconUrl;
      } catch (error) {
        // Silently handle any errors
        setWhiteIcons(prev => ({
          ...prev,
          [tab.id]: false
        }));
      }
    });

    // Cleanup: restore console.error
    return () => {
      console.error = console.error;
    };
  }, [tabs, isIconWhite]);

  const filteredTabs = tabs.filter(tab => 
    tab.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === '/') {
        e.preventDefault();
        searchInputRef.current?.focus();
      } else if (e.key === 'Enter' && searchInputRef.current === document.activeElement) {
        // Activate first visible tab on Enter
        if (filteredTabs.length > 0) {
          handleTabClick(filteredTabs[0].id);
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [filteredTabs]);

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

      <div className="search-container">
        <input
          type="text"
          ref={searchInputRef}
          className="search-input"
          placeholder="Search tabs... (Press 'Tab ⭾' to focus)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          autoFocus
        />
      </div>

      <div className="tab-grid">
        {filteredTabs.map((tab) => {
          const isWhite = whiteIcons[tab.id];
          console.log(`Rendering ${tab.title} - isWhite: ${isWhite}`);
          
          return (
            <div
              key={tab.id}
              className="tab-item"
              onClick={() => handleTabClick(tab.id)}
            >
              <img
                src={tab.favIconUrl || fallbackIcon}
                alt=""
                className={`favicon ${isWhite ? 'recolor-black' : ''}`}
                onError={handleImageError}
                loading="lazy"
              />
              <span className="tab-title">
                {highlightMatchingText(tab.title, searchQuery)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function highlightMatchingText(text, query) {
  if (!query) return text;
  
  const parts = text.split(new RegExp(`(${query})`, 'gi'));
  return parts.map((part, i) => 
    part.toLowerCase() === query.toLowerCase() ? 
      <span key={i} className="highlight">{part}</span> : 
      part
  );
}

export default App;