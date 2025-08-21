#!/usr/bin/env python3
"""
Integration Tests for Bypass Paywalls Clean Extension
Tests the integration between Chrome extension and backend API
"""

import requests
import json
import sys
from datetime import datetime

class IntegrationTester:
    def __init__(self, backend_url="https://article-unlocker-95.preview.emergentagent.com"):
        self.backend_url = backend_url
        self.api_url = f"{backend_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")

    def test_extension_backend_communication(self):
        """Test that extension can communicate with backend"""
        try:
            # Simulate extension logging a bypass action
            log_data = {
                "action": "header_modified",
                "domain": "lefigaro.fr",
                "url": "https://www.lefigaro.fr/actualite-france/test-article-123",
                "user_agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
                "success": True
            }
            
            response = requests.post(f"{self.api_url}/bypass-log", json=log_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("action") == "header_modified" and data.get("domain") == "lefigaro.fr":
                    self.log_test("Extension-Backend Communication", True, "Successfully logged bypass action")
                    return True
                else:
                    self.log_test("Extension-Backend Communication", False, "Invalid response data")
                    return False
            else:
                self.log_test("Extension-Backend Communication", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Extension-Backend Communication", False, f"Exception: {str(e)}")
            return False

    def test_popup_stats_integration(self):
        """Test popup statistics integration"""
        try:
            # First, create some test data
            test_actions = [
                {"action": "cookies_cleared", "domain": "lefigaro.fr", "url": "https://www.lefigaro.fr/test1", "success": True},
                {"action": "paywall_detected", "domain": "lefigaro.fr", "url": "https://www.lefigaro.fr/test2", "success": True},
                {"action": "content_unlocked", "domain": "lefigaro.fr", "url": "https://www.lefigaro.fr/test3", "success": True}
            ]
            
            # Log test actions
            for action_data in test_actions:
                requests.post(f"{self.api_url}/bypass-log", json=action_data, timeout=5)
            
            # Get stats (what popup would do)
            response = requests.get(f"{self.api_url}/bypass-stats", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                if (stats.get("total_bypasses", 0) >= 3 and 
                    isinstance(stats.get("success_rate"), (int, float)) and
                    isinstance(stats.get("most_bypassed_sites"), list)):
                    self.log_test("Popup Stats Integration", True, 
                                f"Stats: {stats['total_bypasses']} total, {stats['success_rate']}% success rate")
                    return True
                else:
                    self.log_test("Popup Stats Integration", False, "Invalid stats format")
                    return False
            else:
                self.log_test("Popup Stats Integration", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Popup Stats Integration", False, f"Exception: {str(e)}")
            return False

    def test_site_config_integration(self):
        """Test site configuration integration"""
        try:
            # Test getting Le Figaro config (what extension would do)
            response = requests.get(f"{self.api_url}/site-config/lefigaro.fr", timeout=10)
            
            if response.status_code == 200:
                config = response.json()
                
                # Verify config has required fields for extension
                required_fields = ["domain", "name", "enabled", "methods"]
                if all(field in config for field in required_fields):
                    methods = config["methods"]
                    
                    # Check for bypass methods
                    if ("removeCookies" in methods and 
                        "useragent" in methods and
                        "referer" in methods):
                        self.log_test("Site Config Integration", True, 
                                    f"Valid config for {config['name']}")
                        return True
                    else:
                        self.log_test("Site Config Integration", False, "Missing bypass methods")
                        return False
                else:
                    self.log_test("Site Config Integration", False, "Missing required fields")
                    return False
            else:
                self.log_test("Site Config Integration", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Site Config Integration", False, f"Exception: {str(e)}")
            return False

    def test_rules_update_integration(self):
        """Test rules update integration"""
        try:
            # Test updating rules (what popup update button would do)
            response = requests.post(f"{self.api_url}/update-rules", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if (result.get("success") and 
                    result.get("updated_sites", 0) > 0 and
                    "message" in result):
                    self.log_test("Rules Update Integration", True, 
                                f"Updated {result['updated_sites']} sites")
                    return True
                else:
                    self.log_test("Rules Update Integration", False, "Update failed or no sites updated")
                    return False
            else:
                self.log_test("Rules Update Integration", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Rules Update Integration", False, f"Exception: {str(e)}")
            return False

    def test_bypass_workflow_simulation(self):
        """Simulate complete bypass workflow"""
        try:
            test_url = "https://www.lefigaro.fr/politique/test-article-paywall-bypass"
            
            # Step 1: Extension detects paywall
            step1_data = {
                "action": "paywall_detected",
                "domain": "lefigaro.fr", 
                "url": test_url,
                "success": True
            }
            response1 = requests.post(f"{self.api_url}/bypass-log", json=step1_data, timeout=5)
            
            # Step 2: Extension modifies headers
            step2_data = {
                "action": "header_modified",
                "domain": "lefigaro.fr",
                "url": test_url,
                "user_agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
                "success": True
            }
            response2 = requests.post(f"{self.api_url}/bypass-log", json=step2_data, timeout=5)
            
            # Step 3: Extension clears cookies
            step3_data = {
                "action": "cookies_cleared",
                "domain": "lefigaro.fr",
                "url": test_url,
                "success": True
            }
            response3 = requests.post(f"{self.api_url}/bypass-log", json=step3_data, timeout=5)
            
            # Step 4: Extension unlocks content
            step4_data = {
                "action": "content_unlocked",
                "domain": "lefigaro.fr",
                "url": test_url,
                "success": True
            }
            response4 = requests.post(f"{self.api_url}/bypass-log", json=step4_data, timeout=5)
            
            # Verify all steps succeeded
            if all(r.status_code == 200 for r in [response1, response2, response3, response4]):
                # Check that stats were updated
                stats_response = requests.get(f"{self.api_url}/bypass-stats", timeout=5)
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    if stats.get("total_bypasses", 0) >= 4:
                        self.log_test("Complete Bypass Workflow", True, 
                                    f"All 4 steps logged, total bypasses: {stats['total_bypasses']}")
                        return True
                    else:
                        self.log_test("Complete Bypass Workflow", False, "Stats not updated correctly")
                        return False
                else:
                    self.log_test("Complete Bypass Workflow", False, "Failed to get updated stats")
                    return False
            else:
                self.log_test("Complete Bypass Workflow", False, "One or more steps failed")
                return False
                
        except Exception as e:
            self.log_test("Complete Bypass Workflow", False, f"Exception: {str(e)}")
            return False

    def test_error_handling(self):
        """Test error handling in integration"""
        try:
            # Test invalid domain
            invalid_data = {
                "action": "test",
                "domain": "",  # Invalid empty domain
                "url": "invalid-url",
                "success": True
            }
            
            response = requests.post(f"{self.api_url}/bypass-log", json=invalid_data, timeout=5)
            
            # Should still accept the log (backend is lenient)
            if response.status_code in [200, 400]:
                # Test unsupported site config
                response2 = requests.get(f"{self.api_url}/site-config/unsupported-site.com", timeout=5)
                
                if response2.status_code == 200:
                    data = response2.json()
                    if data is None:  # Should return None for unsupported sites
                        self.log_test("Error Handling", True, "Properly handles invalid/unsupported requests")
                        return True
                    else:
                        self.log_test("Error Handling", False, "Should return None for unsupported sites")
                        return False
                else:
                    self.log_test("Error Handling", False, f"Unexpected status: {response2.status_code}")
                    return False
            else:
                self.log_test("Error Handling", False, f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        print("🔗 Starting Integration Tests")
        print(f"🌐 Backend URL: {self.backend_url}")
        print("=" * 60)
        
        # Run integration tests
        self.test_extension_backend_communication()
        self.test_popup_stats_integration()
        self.test_site_config_integration()
        self.test_rules_update_integration()
        self.test_bypass_workflow_simulation()
        self.test_error_handling()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Integration Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All integration tests passed! Extension-Backend integration is working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} integration tests failed.")
            return 1

def main():
    """Main test execution"""
    tester = IntegrationTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())