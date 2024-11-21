/* global chrome */

import React, { useState, useEffect, useRef } from 'react';
import './index.css';
import fallbackIcon from './fallback.svg';  // Adjust the path as needed

function App() {
  const [tabs, setTabs] = useState([]);
  const [whiteIcons, setWhiteIcons] = useState({});
  const canvasRef = useRef(document.createElement('canvas'));

  useEffect(() => {
    if (chrome && chrome.tabs) {
      chrome.tabs.query({}, (result) => {
        setTabs(result);
      });
    }
  }, []);

  const isIconWhite = (imgElement) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = imgElement.width;
    canvas.height = imgElement.height;
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
  };

  useEffect(() => {
    tabs.forEach(tab => {
      if (tab.favIconUrl) {
        const img = new Image();
        img.crossOrigin = 'Anonymous';
        img.onload = () => {
          setWhiteIcons(prev => ({
            ...prev,
            [tab.id]: isIconWhite(img)
          }));
        };
        img.src = tab.favIconUrl;
      }
    });
  }, [tabs]);

  const handleTabClick = (tabId) => {
    if (chrome && chrome.tabs) {
      chrome.tabs.update(tabId, { active: true });
      chrome.windows.update(tabs.find(tab => tab.id === tabId).windowId, { focused: true });
    }
  };

  return (
    <div className="App">
      <h1>Current Tabs</h1>
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
            />
            <span>{tab.title}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;