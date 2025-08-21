// Content Script executed once per page load

(function() {
  'use strict';
  
  // Prevent multiple executions
  if (window.bypassPaywallsExecuted) {
    return;
  }
  window.bypassPaywallsExecuted = true;
  
  const currentDomain = window.location.hostname.replace(/^www\./, '');
  
  if (currentDomain === 'lefigaro.fr') {
    // Immediate actions before page fully loads
    
    // Override fetch to intercept paywall API calls
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
      const url = args[0];
      if (typeof url === 'string' && (url.includes('paywall') || url.includes('subscription'))) {
        console.log('Blocked paywall API call:', url);
        return Promise.resolve(new Response('{}', { status: 200 }));
      }
      return originalFetch.apply(this, args);
    };
    
    // Override XMLHttpRequest
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
      const xhr = new originalXHR();
      const originalOpen = xhr.open;
      
      xhr.open = function(method, url) {
        if (typeof url === 'string' && (url.includes('paywall') || url.includes('subscription'))) {
          console.log('Blocked paywall XHR call:', url);
          return;
        }
        return originalOpen.apply(this, arguments);
      };
      
      return xhr;
    };
    
    // Disable common paywall JavaScript functions
    const paywallFunctions = [
      'showPaywall',
      'initPaywall',
      'checkSubscription',
      'lockContent',
      'hideContent',
      'blurContent'
    ];
    
    paywallFunctions.forEach(funcName => {
      window[funcName] = function() {
        console.log(`Disabled paywall function: ${funcName}`);
        return false;
      };
    });
    
    // Override localStorage setters for paywall counters
    const originalSetItem = localStorage.setItem;
    localStorage.setItem = function(key, value) {
      if (key.includes('paywall') || key.includes('premium') || key.includes('article_count')) {
        console.log(`Blocked localStorage set: ${key}`);
        return;
      }
      return originalSetItem.apply(this, arguments);
    };
    
    console.log('Bypass Paywalls Clean: Early script injection completed for Le Figaro');
  }
})();