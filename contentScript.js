// Bypass Paywalls Clean - Content Script

// Wait for DOM to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initBypass);
} else {
  initBypass();
}

function initBypass() {
  const currentDomain = window.location.hostname.replace(/^www\./, '');
  
  if (currentDomain === 'lefigaro.fr') {
    bypassLeFigaro();
  }
}

function bypassLeFigaro() {
  console.log('Bypass Paywalls: Attempting to bypass Le Figaro paywall');
  
  // Method 1: Remove paywall elements
  removePaywallElements();
  
  // Method 2: Clear cookies
  clearPaywallCookies();
  
  // Method 3: Unhide content
  unhideContent();
  
  // Method 4: Check for premium content and redirect if needed
  setTimeout(() => {
    if (isPaywallActive()) {
      console.log('Paywall still active, trying alternative methods');
      tryAlternativeMethods();
    }
  }, 2000);
}

function removePaywallElements() {
  const paywallSelectors = [
    '.fig-paywall',
    '.fig-premium-paywall',
    '.fig-paywall-premium',
    '.subscription-banner',
    '.paywall-banner',
    '[class*="paywall"]',
    '[id*="paywall"]',
    '.fig-premium-article__paywall',
    '.fig-paywall__container'
  ];
  
  paywallSelectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => {
      el.remove();
      console.log(`Removed paywall element: ${selector}`);
    });
  });
}

function clearPaywallCookies() {
  // Clear relevant cookies via background script
  chrome.runtime.sendMessage({
    action: 'clearCookies',
    url: window.location.href
  });
  
  // Clear localStorage
  const localStorageKeys = ['figaro_paywall', 'premium_views', 'article_count'];
  localStorageKeys.forEach(key => {
    if (localStorage.getItem(key)) {
      localStorage.removeItem(key);
      console.log(`Cleared localStorage: ${key}`);
    }
  });
  
  // Clear sessionStorage
  const sessionStorageKeys = ['figaro_session', 'paywall_session'];
  sessionStorageKeys.forEach(key => {
    if (sessionStorage.getItem(key)) {
      sessionStorage.removeItem(key);
      console.log(`Cleared sessionStorage: ${key}`);
    }
  });
}

function unhideContent() {
  // Show hidden content
  const contentSelectors = [
    '.fig-content-body',
    '.fig-article__content',
    '.article-content',
    '.fig-premium-article__content'
  ];
  
  contentSelectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => {
      el.style.display = 'block';
      el.style.visibility = 'visible';
      el.style.opacity = '1';
      el.style.height = 'auto';
      el.style.overflow = 'visible';
      
      // Remove blur effects
      el.style.filter = 'none';
      el.style.webkitFilter = 'none';
    });
  });
  
  // Remove CSS classes that hide content
  const hiddenElements = document.querySelectorAll('.fig-premium-blur, .blurred, .fig-paywall-blur');
  hiddenElements.forEach(el => {
    el.classList.remove('fig-premium-blur', 'blurred', 'fig-paywall-blur');
  });
}

function isPaywallActive() {
  const paywallIndicators = [
    '.fig-paywall',
    '.fig-premium-paywall',
    '.subscription-banner',
    '[class*="paywall"]'
  ];
  
  return paywallIndicators.some(selector => document.querySelector(selector));
}

function tryAlternativeMethods() {
  // Method 1: Try to get full content via JSON-LD
  tryJsonLdContent();
  
  // Method 2: Redirect to archive if paywall persists
  setTimeout(() => {
    if (isPaywallActive()) {
      console.log('Paywall still active, offering archive redirect');
      showArchiveOption();
    }
  }, 3000);
}

function tryJsonLdContent() {
  const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
  
  jsonLdScripts.forEach(script => {
    try {
      const data = JSON.parse(script.textContent);
      if (data['@type'] === 'NewsArticle' && data.articleBody) {
        console.log('Found full article content in JSON-LD');
        insertFullContent(data.articleBody);
      }
    } catch (e) {
      // Ignore parsing errors
    }
  });
}

function insertFullContent(content) {
  const contentContainer = document.querySelector('.fig-article__content, .article-content');
  if (contentContainer) {
    // Create a new paragraph for the full content
    const fullContentDiv = document.createElement('div');
    fullContentDiv.innerHTML = `<p>${content}</p>`;
    fullContentDiv.style.backgroundColor = '#f9f9f9';
    fullContentDiv.style.padding = '15px';
    fullContentDiv.style.border = '1px solid #ddd';
    fullContentDiv.style.marginTop = '20px';
    
    const header = document.createElement('h4');
    header.textContent = 'Contenu complet (via Bypass Paywalls):';
    header.style.color = '#333';
    header.style.marginBottom = '10px';
    
    fullContentDiv.insertBefore(header, fullContentDiv.firstChild);
    contentContainer.appendChild(fullContentDiv);
  }
}

function showArchiveOption() {
  const archiveButton = document.createElement('div');
  archiveButton.innerHTML = `
    <div style="position: fixed; top: 20px; right: 20px; z-index: 10000; background: #ff6b35; color: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.3); cursor: pointer; font-family: Arial, sans-serif;">
      <strong>Paywall détecté!</strong><br>
      <small>Cliquez pour voir la version archivée</small>
    </div>
  `;
  
  archiveButton.onclick = () => {
    chrome.runtime.sendMessage({
      action: 'redirectToArchive',
      url: window.location.href
    });
  };
  
  document.body.appendChild(archiveButton);
  
  // Auto-hide after 10 seconds
  setTimeout(() => {
    if (archiveButton.parentNode) {
      archiveButton.remove();
    }
  }, 10000);
}

// Block specific scripts that enforce paywall
function blockPaywallScripts() {
  const scriptSelectors = [
    'script[src*="paywall"]',
    'script[src*="subscription"]',
    'script[src*="premium"]'
  ];
  
  scriptSelectors.forEach(selector => {
    const scripts = document.querySelectorAll(selector);
    scripts.forEach(script => {
      script.remove();
      console.log(`Blocked paywall script: ${script.src}`);
    });
  });
}

// Initialize script blocking
blockPaywallScripts();

// Monitor for dynamic paywall content
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === 'childList') {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) { // Element node
          // Check if paywall element was added
          if (node.classList && (node.classList.contains('fig-paywall') || node.classList.contains('subscription-banner'))) {
            node.remove();
            console.log('Dynamically removed paywall element');
          }
          
          // Block dynamically added paywall scripts
          if (node.tagName === 'SCRIPT' && node.src && (node.src.includes('paywall') || node.src.includes('subscription'))) {
            node.remove();
            console.log(`Blocked dynamic paywall script: ${node.src}`);
          }
        }
      });
    }
  });
});

// Start observing
observer.observe(document.body, {
  childList: true,
  subtree: true
});

console.log('Bypass Paywalls Clean: Content script loaded for Le Figaro');