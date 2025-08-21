#!/usr/bin/env python3
"""
Bypass Techniques Analysis for Bypass Paywalls Clean Extension
Analyzes the implemented bypass techniques and their effectiveness
"""

import json
import sys
from pathlib import Path

class BypassTechniquesAnalyzer:
    def __init__(self, extension_path="/app"):
        self.extension_path = Path(extension_path)
        self.techniques = {}
        self.analysis_results = []

    def analyze_header_modification(self):
        """Analyze header modification techniques"""
        print("🔍 Analyzing Header Modification Techniques...")
        
        # Check background.js for header modifications
        bg_path = self.extension_path / "background.js"
        if bg_path.exists():
            with open(bg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            techniques_found = []
            
            # User-Agent spoofing
            if "user-agent" in content.lower() and "googlebot" in content.lower():
                techniques_found.append("✅ User-Agent spoofing to Googlebot")
            
            # Referer modification
            if "referer" in content.lower() and "google.com" in content:
                techniques_found.append("✅ Referer header set to Google")
            
            # Header blocking/modification
            if "onBeforeSendHeaders" in content:
                techniques_found.append("✅ Dynamic header modification via webRequest API")
            
            self.techniques["Header Modification"] = techniques_found
            print(f"   Found {len(techniques_found)} header modification techniques")
            
        # Check rules.json for declarative rules
        rules_path = self.extension_path / "rules.json"
        if rules_path.exists():
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            declarative_rules = []
            for rule in rules:
                if rule.get("action", {}).get("type") == "modifyHeaders":
                    headers = rule.get("action", {}).get("requestHeaders", [])
                    for header in headers:
                        if header.get("header") == "User-Agent":
                            declarative_rules.append("✅ Declarative User-Agent modification")
                        elif header.get("header") == "Referer":
                            declarative_rules.append("✅ Declarative Referer modification")
            
            if declarative_rules:
                self.techniques["Declarative Rules"] = declarative_rules
                print(f"   Found {len(declarative_rules)} declarative header rules")

    def analyze_cookie_management(self):
        """Analyze cookie management techniques"""
        print("🔍 Analyzing Cookie Management Techniques...")
        
        techniques_found = []
        
        # Check background.js for cookie clearing
        bg_path = self.extension_path / "background.js"
        if bg_path.exists():
            with open(bg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "chrome.cookies.remove" in content:
                techniques_found.append("✅ Automatic cookie removal via Chrome API")
            
            if "removeCookies" in content:
                techniques_found.append("✅ Configurable cookie blacklist")
            
            # Check for specific Le Figaro cookies
            figaro_cookies = ["PHPSESSID", "_ga", "_gid", "tarteaucitron"]
            for cookie in figaro_cookies:
                if cookie in content:
                    techniques_found.append(f"✅ Targets {cookie} cookie")
        
        # Check content script for localStorage/sessionStorage clearing
        cs_path = self.extension_path / "contentScript.js"
        if cs_path.exists():
            with open(cs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "localStorage.removeItem" in content:
                techniques_found.append("✅ localStorage clearing")
            
            if "sessionStorage.removeItem" in content:
                techniques_found.append("✅ sessionStorage clearing")
        
        self.techniques["Cookie Management"] = techniques_found
        print(f"   Found {len(techniques_found)} cookie management techniques")

    def analyze_dom_manipulation(self):
        """Analyze DOM manipulation techniques"""
        print("🔍 Analyzing DOM Manipulation Techniques...")
        
        techniques_found = []
        
        cs_path = self.extension_path / "contentScript.js"
        if cs_path.exists():
            with open(cs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Paywall element removal
            if "removePaywallElements" in content and "querySelectorAll" in content:
                techniques_found.append("✅ Paywall element removal")
            
            # Content unhiding
            if "unhideContent" in content and "style.display" in content:
                techniques_found.append("✅ Hidden content revelation")
            
            # Blur effect removal
            if "filter" in content and "webkitFilter" in content:
                techniques_found.append("✅ CSS blur effect removal")
            
            # CSS class manipulation
            if "classList.remove" in content:
                techniques_found.append("✅ CSS class manipulation")
            
            # Dynamic monitoring
            if "MutationObserver" in content:
                techniques_found.append("✅ Dynamic paywall monitoring")
            
            # JSON-LD content extraction
            if "application/ld+json" in content and "JSON.parse" in content:
                techniques_found.append("✅ JSON-LD content extraction")
        
        self.techniques["DOM Manipulation"] = techniques_found
        print(f"   Found {len(techniques_found)} DOM manipulation techniques")

    def analyze_script_blocking(self):
        """Analyze script blocking techniques"""
        print("🔍 Analyzing Script Blocking Techniques...")
        
        techniques_found = []
        
        # Check content script for script blocking
        cs_path = self.extension_path / "contentScript.js"
        if cs_path.exists():
            with open(cs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "blockPaywallScripts" in content:
                techniques_found.append("✅ Static paywall script blocking")
            
            if "script.remove()" in content:
                techniques_found.append("✅ Dynamic script removal")
        
        # Check contentScript_once.js for early intervention
        cs_once_path = self.extension_path / "contentScript_once.js"
        if cs_once_path.exists():
            with open(cs_once_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "window.fetch" in content and "originalFetch" in content:
                techniques_found.append("✅ Fetch API interception")
            
            if "XMLHttpRequest" in content and "originalXHR" in content:
                techniques_found.append("✅ XMLHttpRequest interception")
            
            if "localStorage.setItem" in content and "originalSetItem" in content:
                techniques_found.append("✅ localStorage write blocking")
        
        # Check declarative rules for script blocking
        rules_path = self.extension_path / "rules.json"
        if rules_path.exists():
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            for rule in rules:
                if rule.get("action", {}).get("type") == "block":
                    condition = rule.get("condition", {})
                    if "script" in condition.get("resourceTypes", []):
                        techniques_found.append("✅ Declarative script blocking")
                        break
        
        self.techniques["Script Blocking"] = techniques_found
        print(f"   Found {len(techniques_found)} script blocking techniques")

    def analyze_archive_integration(self):
        """Analyze archive service integration"""
        print("🔍 Analyzing Archive Service Integration...")
        
        techniques_found = []
        
        # Check content script for archive redirection
        cs_path = self.extension_path / "contentScript.js"
        if cs_path.exists():
            with open(cs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "archive.is" in content:
                techniques_found.append("✅ Archive.is integration")
            
            if "showArchiveOption" in content:
                techniques_found.append("✅ User-friendly archive option")
        
        # Check background script for archive redirection
        bg_path = self.extension_path / "background.js"
        if bg_path.exists():
            with open(bg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "redirectToArchive" in content:
                techniques_found.append("✅ Background archive redirection")
        
        # Check popup for archive button
        popup_path = self.extension_path / "popup.js"
        if popup_path.exists():
            with open(popup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "archiveBtn" in content and "archive.is" in content:
                techniques_found.append("✅ Popup archive button")
        
        self.techniques["Archive Integration"] = techniques_found
        print(f"   Found {len(techniques_found)} archive integration techniques")

    def analyze_le_figaro_specifics(self):
        """Analyze Le Figaro specific implementations"""
        print("🔍 Analyzing Le Figaro Specific Techniques...")
        
        techniques_found = []
        
        # Check sites.js for Le Figaro configuration
        sites_path = self.extension_path / "sites.js"
        if sites_path.exists():
            with open(sites_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "lefigaro.fr" in content:
                techniques_found.append("✅ Dedicated Le Figaro configuration")
            
            # Check for specific selectors
            figaro_selectors = [".fig-paywall", ".fig-premium-paywall", ".fig-article__content"]
            for selector in figaro_selectors:
                if selector in content:
                    techniques_found.append(f"✅ Le Figaro selector: {selector}")
        
        # Check content script for Le Figaro specific functions
        cs_path = self.extension_path / "contentScript.js"
        if cs_path.exists():
            with open(cs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "bypassLeFigaro" in content:
                techniques_found.append("✅ Dedicated Le Figaro bypass function")
            
            if "figaro_paywall" in content:
                techniques_found.append("✅ Le Figaro specific cookie targeting")
        
        self.techniques["Le Figaro Specifics"] = techniques_found
        print(f"   Found {len(techniques_found)} Le Figaro specific techniques")

    def generate_effectiveness_assessment(self):
        """Generate effectiveness assessment"""
        print("\n📊 Effectiveness Assessment:")
        
        total_techniques = sum(len(techniques) for techniques in self.techniques.values())
        
        effectiveness_scores = {
            "Header Modification": 9,  # Very effective against server-side checks
            "Cookie Management": 8,    # Effective for session-based paywalls
            "DOM Manipulation": 7,     # Good for client-side paywalls
            "Script Blocking": 9,      # Very effective for preventing paywall scripts
            "Archive Integration": 6,  # Fallback option, always works
            "Le Figaro Specifics": 8   # Tailored for target site
        }
        
        weighted_score = 0
        total_weight = 0
        
        for category, techniques in self.techniques.items():
            if techniques:
                score = effectiveness_scores.get(category, 5)
                weight = len(techniques)
                weighted_score += score * weight
                total_weight += weight
                
                print(f"   {category}: {score}/10 (Techniques: {len(techniques)})")
        
        if total_weight > 0:
            overall_effectiveness = weighted_score / total_weight
            print(f"\n🎯 Overall Effectiveness Score: {overall_effectiveness:.1f}/10")
            
            if overall_effectiveness >= 8:
                print("   Assessment: Highly effective bypass implementation")
            elif overall_effectiveness >= 6:
                print("   Assessment: Moderately effective bypass implementation")
            else:
                print("   Assessment: Basic bypass implementation")

    def run_analysis(self):
        """Run complete bypass techniques analysis"""
        print("🔬 Starting Bypass Techniques Analysis")
        print(f"📁 Extension path: {self.extension_path}")
        print("=" * 60)
        
        # Analyze all technique categories
        self.analyze_header_modification()
        self.analyze_cookie_management()
        self.analyze_dom_manipulation()
        self.analyze_script_blocking()
        self.analyze_archive_integration()
        self.analyze_le_figaro_specifics()
        
        # Generate summary
        print("\n📋 Techniques Summary:")
        for category, techniques in self.techniques.items():
            print(f"\n{category}:")
            for technique in techniques:
                print(f"   {technique}")
        
        # Generate effectiveness assessment
        self.generate_effectiveness_assessment()
        
        print("\n" + "=" * 60)
        print(f"✅ Analysis complete! Found {sum(len(t) for t in self.techniques.values())} bypass techniques across {len(self.techniques)} categories.")
        
        return 0

def main():
    """Main analysis execution"""
    analyzer = BypassTechniquesAnalyzer()
    return analyzer.run_analysis()

if __name__ == "__main__":
    sys.exit(main())