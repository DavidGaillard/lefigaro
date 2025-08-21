#!/usr/bin/env python3
"""
Chrome Extension Structure and Logic Validator
Validates the Bypass Paywalls Clean Chrome extension
"""

import json
import os
import sys
from pathlib import Path

class ChromeExtensionValidator:
    def __init__(self, extension_path="/app"):
        self.extension_path = Path(extension_path)
        self.tests_run = 0
        self.tests_passed = 0
        self.issues = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
            self.issues.append(f"{name}: {details}")

    def validate_manifest(self):
        """Validate manifest.json structure and content"""
        manifest_path = self.extension_path / "manifest.json"
        
        if not manifest_path.exists():
            self.log_test("Manifest File Exists", False, "manifest.json not found")
            return False
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Check required fields
            required_fields = ["manifest_version", "name", "version", "description"]
            missing_fields = [field for field in required_fields if field not in manifest]
            
            if missing_fields:
                self.log_test("Manifest Required Fields", False, f"Missing: {missing_fields}")
                return False
            
            # Check manifest version
            if manifest.get("manifest_version") != 3:
                self.log_test("Manifest Version", False, f"Expected v3, got v{manifest.get('manifest_version')}")
                return False
            
            # Check permissions
            required_permissions = ["storage", "activeTab", "scripting", "cookies"]
            manifest_permissions = manifest.get("permissions", [])
            missing_permissions = [perm for perm in required_permissions if perm not in manifest_permissions]
            
            if missing_permissions:
                self.log_test("Manifest Permissions", False, f"Missing permissions: {missing_permissions}")
                return False
            
            # Check host permissions for Le Figaro
            host_permissions = manifest.get("host_permissions", [])
            if not any("lefigaro.fr" in perm for perm in host_permissions):
                self.log_test("Host Permissions", False, "Missing Le Figaro host permission")
                return False
            
            # Check background script
            if "background" not in manifest or "service_worker" not in manifest["background"]:
                self.log_test("Background Script", False, "Missing background service worker")
                return False
            
            # Check content scripts
            if "content_scripts" not in manifest:
                self.log_test("Content Scripts", False, "Missing content scripts")
                return False
            
            content_scripts = manifest["content_scripts"]
            if not any("lefigaro.fr" in str(cs.get("matches", [])) for cs in content_scripts):
                self.log_test("Content Script Matches", False, "No content script for Le Figaro")
                return False
            
            self.log_test("Manifest Validation", True, f"Valid Manifest v{manifest['manifest_version']}")
            return True
            
        except json.JSONDecodeError as e:
            self.log_test("Manifest JSON", False, f"Invalid JSON: {e}")
            return False
        except Exception as e:
            self.log_test("Manifest Validation", False, f"Error: {e}")
            return False

    def validate_icons(self):
        """Validate extension icons"""
        icons_dir = self.extension_path / "icons"
        required_icons = ["bypass-16.png", "bypass-32.png", "bypass-48.png", "bypass-128.png"]
        
        if not icons_dir.exists():
            self.log_test("Icons Directory", False, "Icons directory not found")
            return False
        
        missing_icons = []
        for icon in required_icons:
            icon_path = icons_dir / icon
            if not icon_path.exists():
                missing_icons.append(icon)
        
        if missing_icons:
            self.log_test("Icon Files", False, f"Missing icons: {missing_icons}")
            return False
        
        self.log_test("Icon Files", True, f"All {len(required_icons)} icons present")
        return True

    def validate_background_script(self):
        """Validate background.js"""
        bg_path = self.extension_path / "background.js"
        
        if not bg_path.exists():
            self.log_test("Background Script File", False, "background.js not found")
            return False
        
        try:
            with open(bg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for essential functions and listeners
            required_elements = [
                "chrome.runtime.onInstalled.addListener",
                "chrome.webRequest.onBeforeSendHeaders.addListener",
                "chrome.runtime.onMessage.addListener",
                "siteConfigs",
                "lefigaro.fr"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.log_test("Background Script Logic", False, f"Missing: {missing_elements}")
                return False
            
            # Check for backend URL configuration
            if "BACKEND_URL" not in content:
                self.log_test("Backend URL Config", False, "Missing BACKEND_URL configuration")
                return False
            
            self.log_test("Background Script", True, "Contains all required functionality")
            return True
            
        except Exception as e:
            self.log_test("Background Script", False, f"Error reading file: {e}")
            return False

    def validate_content_script(self):
        """Validate contentScript.js"""
        cs_path = self.extension_path / "contentScript.js"
        
        if not cs_path.exists():
            self.log_test("Content Script File", False, "contentScript.js not found")
            return False
        
        try:
            with open(cs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for essential bypass functions
            required_functions = [
                "bypassLeFigaro",
                "removePaywallElements",
                "clearPaywallCookies",
                "unhideContent",
                "isPaywallActive",
                "tryAlternativeMethods"
            ]
            
            missing_functions = []
            for func in required_functions:
                if func not in content:
                    missing_functions.append(func)
            
            if missing_functions:
                self.log_test("Content Script Functions", False, f"Missing functions: {missing_functions}")
                return False
            
            # Check for Le Figaro specific selectors
            figaro_selectors = [".fig-paywall", ".fig-premium-paywall", ".fig-article__content"]
            if not any(selector in content for selector in figaro_selectors):
                self.log_test("Le Figaro Selectors", False, "Missing Le Figaro specific selectors")
                return False
            
            # Check for JSON-LD extraction
            if "JSON.parse" not in content or "application/ld+json" not in content:
                self.log_test("JSON-LD Extraction", False, "Missing JSON-LD content extraction")
                return False
            
            self.log_test("Content Script", True, "Contains all required bypass functionality")
            return True
            
        except Exception as e:
            self.log_test("Content Script", False, f"Error reading file: {e}")
            return False

    def validate_popup_files(self):
        """Validate popup.html and popup.js"""
        popup_html = self.extension_path / "popup.html"
        popup_js = self.extension_path / "popup.js"
        
        # Validate popup.html
        if not popup_html.exists():
            self.log_test("Popup HTML", False, "popup.html not found")
            return False
        
        try:
            with open(popup_html, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Check for essential UI elements
            required_elements = [
                "toggleSwitch",
                "currentSite",
                "supportStatus",
                "todayCount",
                "totalCount",
                "clearCookiesBtn",
                "archiveBtn",
                "updateBtn"
            ]
            
            missing_elements = []
            for element in required_elements:
                if f'id="{element}"' not in html_content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.log_test("Popup HTML Elements", False, f"Missing elements: {missing_elements}")
                return False
            
        except Exception as e:
            self.log_test("Popup HTML", False, f"Error reading file: {e}")
            return False
        
        # Validate popup.js
        if not popup_js.exists():
            self.log_test("Popup JS", False, "popup.js not found")
            return False
        
        try:
            with open(popup_js, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # Check for essential functions
            required_functions = [
                "initializePopup",
                "updateCurrentSiteInfo",
                "updateStats",
                "setupEventListeners"
            ]
            
            missing_functions = []
            for func in required_functions:
                if func not in js_content:
                    missing_functions.append(func)
            
            if missing_functions:
                self.log_test("Popup JS Functions", False, f"Missing functions: {missing_functions}")
                return False
            
            # Check for Chrome API usage
            chrome_apis = ["chrome.tabs.query", "chrome.storage.local", "chrome.runtime.sendMessage"]
            missing_apis = []
            for api in chrome_apis:
                if api not in js_content:
                    missing_apis.append(api)
            
            if missing_apis:
                self.log_test("Chrome APIs", False, f"Missing APIs: {missing_apis}")
                return False
            
            self.log_test("Popup Files", True, "Both popup.html and popup.js are valid")
            return True
            
        except Exception as e:
            self.log_test("Popup JS", False, f"Error reading file: {e}")
            return False

    def validate_additional_files(self):
        """Validate additional extension files"""
        # Check sites.js
        sites_js = self.extension_path / "sites.js"
        if not sites_js.exists():
            self.log_test("Sites Configuration", False, "sites.js not found")
            return False
        
        try:
            with open(sites_js, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "lefigaro.fr" not in content:
                self.log_test("Sites Configuration", False, "Le Figaro configuration missing")
                return False
        except Exception as e:
            self.log_test("Sites Configuration", False, f"Error reading sites.js: {e}")
            return False
        
        # Check rules.json
        rules_json = self.extension_path / "rules.json"
        if not rules_json.exists():
            self.log_test("Declarative Rules", False, "rules.json not found")
            return False
        
        try:
            with open(rules_json, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            if not isinstance(rules, list) or len(rules) == 0:
                self.log_test("Declarative Rules", False, "Invalid or empty rules")
                return False
            
            # Check for Le Figaro rules
            lefigaro_rules = [rule for rule in rules if "lefigaro.fr" in str(rule)]
            if not lefigaro_rules:
                self.log_test("Declarative Rules", False, "No rules for Le Figaro")
                return False
                
        except Exception as e:
            self.log_test("Declarative Rules", False, f"Error reading rules.json: {e}")
            return False
        
        # Check contentScript_once.js
        cs_once = self.extension_path / "contentScript_once.js"
        if not cs_once.exists():
            self.log_test("Early Content Script", False, "contentScript_once.js not found")
            return False
        
        self.log_test("Additional Files", True, "All additional files present and valid")
        return True

    def validate_backend_integration(self):
        """Validate backend integration in extension files"""
        files_to_check = ["background.js", "popup.js"]
        backend_integration_found = False
        
        for filename in files_to_check:
            file_path = self.extension_path / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for backend API calls
                    if "api/bypass-log" in content or "api/update-rules" in content:
                        backend_integration_found = True
                        break
                except Exception:
                    continue
        
        if backend_integration_found:
            self.log_test("Backend Integration", True, "Extension integrates with backend API")
            return True
        else:
            self.log_test("Backend Integration", False, "No backend API integration found")
            return False

    def run_all_validations(self):
        """Run all extension validations"""
        print("🔍 Starting Chrome Extension Validation")
        print(f"📁 Extension path: {self.extension_path}")
        print("=" * 60)
        
        # Core file validations
        self.validate_manifest()
        self.validate_icons()
        self.validate_background_script()
        self.validate_content_script()
        self.validate_popup_files()
        self.validate_additional_files()
        self.validate_backend_integration()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Validation Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 Chrome extension structure is valid and complete!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} validation issues found:")
            for issue in self.issues:
                print(f"   • {issue}")
            return 1

def main():
    """Main validation execution"""
    validator = ChromeExtensionValidator()
    return validator.run_all_validations()

if __name__ == "__main__":
    sys.exit(main())