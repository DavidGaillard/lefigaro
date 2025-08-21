// Bypass Paywalls Clean - Popup Script

document.addEventListener('DOMContentLoaded', async () => {
  await initializePopup();
  setupEventListeners();
});

async function initializePopup() {
  // Get current tab
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const currentTab = tabs[0];
  
  if (currentTab) {
    updateCurrentSiteInfo(currentTab.url);
  }
  
  // Load extension status
  const data = await chrome.storage.local.get(['enabled', 'stats', 'lastUpdate']);
  
  // Update toggle
  const toggleSwitch = document.getElementById('toggleSwitch');
  if (data.enabled !== false) {
    toggleSwitch.classList.add('active');
  } else {
    toggleSwitch.classList.remove('active');
  }
  
  // Update stats
  updateStats(data.stats || { today: 0, total: 0 });
  
  // Update last update time
  if (data.lastUpdate) {
    const lastUpdateEl = document.getElementById('lastUpdate');
    lastUpdateEl.textContent = formatDate(new Date(data.lastUpdate));
  }
}

function updateCurrentSiteInfo(url) {
  try {
    const urlObj = new URL(url);
    const domain = urlObj.hostname.replace(/^www\./, '');
    
    document.getElementById('currentSite').textContent = domain;
    
    // Check if site is supported
    const supportedSites = ['lefigaro.fr'];
    const isSupported = supportedSites.includes(domain);
    
    const supportStatus = document.getElementById('supportStatus');
    if (isSupported) {
      supportStatus.textContent = 'Supporté ✓';
      supportStatus.className = 'supported';
    } else {
      supportStatus.textContent = 'Non supporté';
      supportStatus.className = 'not-supported';
    }
  } catch (e) {
    document.getElementById('currentSite').textContent = 'Page non web';
    document.getElementById('supportStatus').textContent = 'N/A';
  }
}

function updateStats(stats) {
  document.getElementById('todayCount').textContent = stats.today || 0;
  document.getElementById('totalCount').textContent = stats.total || 0;
}

function setupEventListeners() {
  // Toggle switch
  document.getElementById('toggleSwitch').addEventListener('click', async () => {
    const toggleSwitch = document.getElementById('toggleSwitch');
    const isActive = toggleSwitch.classList.contains('active');
    
    if (isActive) {
      toggleSwitch.classList.remove('active');
      await chrome.storage.local.set({ enabled: false });
    } else {
      toggleSwitch.classList.add('active');
      await chrome.storage.local.set({ enabled: true });
    }
  });
  
  // Clear cookies button
  document.getElementById('clearCookiesBtn').addEventListener('click', async () => {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentTab = tabs[0];
    
    if (currentTab) {
      // Send message to background script to clear cookies
      chrome.runtime.sendMessage({
        action: 'clearCookies',
        url: currentTab.url
      }, (response) => {
        if (response && response.success) {
          showNotification('Cookies supprimés avec succès!');
          updateStats({ today: 1, total: 1 }); // Increment stats
        }
      });
    }
  });
  
  // Refresh button
  document.getElementById('refreshBtn').addEventListener('click', async () => {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentTab = tabs[0];
    
    if (currentTab) {
      chrome.tabs.reload(currentTab.id);
      window.close();
    }
  });
  
  // Archive button
  document.getElementById('archiveBtn').addEventListener('click', async () => {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentTab = tabs[0];
    
    if (currentTab) {
      const archiveUrl = `https://archive.is/newest/${encodeURIComponent(currentTab.url)}`;
      chrome.tabs.create({ url: archiveUrl });
      window.close();
    }
  });
  
  // Update button
  document.getElementById('updateBtn').addEventListener('click', async () => {
    try {
      // Call backend to update rules
      const response = await fetch('http://localhost:8001/api/update-rules', {
        method: 'POST'
      });
      
      if (response.ok) {
        await chrome.storage.local.set({ lastUpdate: Date.now() });
        showNotification('Règles mises à jour avec succès!');
        
        // Update display
        const lastUpdateEl = document.getElementById('lastUpdate');
        lastUpdateEl.textContent = formatDate(new Date());
      } else {
        showNotification('Erreur lors de la mise à jour');
      }
    } catch (error) {
      console.error('Update error:', error);
      showNotification('Erreur de connexion au serveur');
    }
  });
}

function showNotification(message) {
  // Create notification element
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(76,175,80,0.9);
    color: white;
    padding: 10px 15px;
    border-radius: 4px;
    font-size: 12px;
    z-index: 10000;
    animation: slideIn 0.3s ease-out;
  `;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // Remove after 3 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 3000);
}

function formatDate(date) {
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'À l\'instant';
  if (diffMins < 60) return `Il y a ${diffMins} min`;
  if (diffHours < 24) return `Il y a ${diffHours}h`;
  if (diffDays < 7) return `Il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`;
  
  return date.toLocaleDateString('fr-FR');
}