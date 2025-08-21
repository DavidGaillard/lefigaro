// Bypass Paywalls Clean - Background Script

// Configuration
const BACKEND_URL = 'http://localhost:8001/api';

// Site configurations
const siteConfigs = {
  'lefigaro.fr': {
    domain: 'lefigaro.fr',
    allowCookies: false,
    removeCookies: ['PHPSESSID', '_ga', '_gid', 'tarteaucitron'],
    useragent: 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    referer: 'https://www.google.com/',
    blockJavaScriptOnce: false,
    techniques: ['cookies', 'useragent', 'referer', 'archive']
  }
};

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('Bypass Paywalls Clean installed');
  initializeExtension();
});

function initializeExtension() {
  // Set default options
  chrome.storage.local.set({
    enabled: true,
    sites: siteConfigs,
    lastUpdate: Date.now()
  });
}

// Clear cookies for paywall sites
function clearSiteCookies(domain) {
  const config = siteConfigs[domain];
  if (!config || config.allowCookies) return;
  
  chrome.cookies.getAll({ domain: domain }, (cookies) => {
    cookies.forEach(cookie => {
      if (config.removeCookies.some(name => cookie.name.includes(name))) {
        chrome.cookies.remove({
          url: `http${cookie.secure ? 's' : ''}://${cookie.domain}${cookie.path}`,
          name: cookie.name
        });
        console.log(`Removed cookie: ${cookie.name} for ${domain}`);
      }
    });
  });
}

// Handle messages from content script and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'clearCookies') {
    const url = new URL(message.url);
    const domain = url.hostname.replace(/^www\./, '');
    clearSiteCookies(domain);
    sendResponse({ success: true });
  }
  
  if (message.action === 'getConfig') {
    const url = new URL(message.url);
    const domain = url.hostname.replace(/^www\./, '');
    sendResponse({ config: siteConfigs[domain] || null });
  }
  
  if (message.action === 'redirectToArchive') {
    const archiveUrl = `https://archive.is/newest/${encodeURIComponent(message.url)}`;
    chrome.tabs.update(sender.tab.id, { url: archiveUrl });
    sendResponse({ success: true });
  }
  
  return true;
});

// Log events to backend
async function logToBackend(action, domain, url) {
  try {
    await fetch(`${BACKEND_URL}/bypass-log`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        action,
        domain,
        url,
        timestamp: new Date().toISOString()
      })
    });
  } catch (error) {
    console.log('Failed to log to backend:', error);
  }
}

// Periodic cleanup
setInterval(() => {
  Object.keys(siteConfigs).forEach(domain => {
    clearSiteCookies(domain);
  });
}, 5 * 60 * 1000); // Every 5 minutes