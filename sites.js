// Site configurations for Bypass Paywalls Clean

const sites = {
  'lefigaro.fr': {
    domain: 'lefigaro.fr',
    name: 'Le Figaro',
    enabled: true,
    methods: {
      removeCookies: ['PHPSESSID', '_ga', '_gid', 'tarteaucitron', 'figaro_paywall', 'premium_views'],
      removePaywallSelectors: [
        '.fig-paywall',
        '.fig-premium-paywall',
        '.fig-paywall-premium',
        '.subscription-banner',
        '.paywall-banner',
        '[class*="paywall"]',
        '[id*="paywall"]',
        '.fig-premium-article__paywall',
        '.fig-paywall__container',
        '.fig-paywall-overlay'
      ],
      unhideContentSelectors: [
        '.fig-content-body',
        '.fig-article__content',
        '.article-content',
        '.fig-premium-article__content'
      ],
      removeBlurSelectors: [
        '.fig-premium-blur',
        '.blurred',
        '.fig-paywall-blur'
      ],
      userAgent: 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
      referer: 'https://www.google.com/',
      blockScripts: [
        'paywall',
        'subscription',
        'premium'
      ],
      jsonLdExtraction: true,
      archiveSupport: true
    },
    notes: 'Support complet avec extraction JSON-LD et redirection archive'
  }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = sites;
} else {
  window.BYPASS_SITES = sites;
}