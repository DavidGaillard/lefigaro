#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Bypass Paywalls Clean Extension
Tests all API endpoints and functionality
"""

import requests
import sys
import json
from datetime import datetime
from urllib.parse import urljoin

class BypassPaywallsAPITester:
    def __init__(self, base_url="https://article-unlocker-95.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_api_root(self):
        """Test the root API endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["message", "version", "endpoints"]
                
                if all(field in data for field in expected_fields):
                    self.log_test("API Root Endpoint", True, f"Status: {response.status_code}")
                    return True
                else:
                    self.log_test("API Root Endpoint", False, f"Missing expected fields in response")
                    return False
            else:
                self.log_test("API Root Endpoint", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_site_config_lefigaro(self):
        """Test Le Figaro site configuration endpoint"""
        try:
            response = requests.get(f"{self.api_url}/site-config/lefigaro.fr", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["domain", "name", "enabled", "methods"]
                
                if all(field in data for field in expected_fields):
                    # Verify Le Figaro specific configuration
                    if (data["domain"] == "lefigaro.fr" and 
                        data["name"] == "Le Figaro" and
                        "removeCookies" in data["methods"]):
                        self.log_test("Le Figaro Site Config", True, f"Configuration loaded correctly")
                        return True
                    else:
                        self.log_test("Le Figaro Site Config", False, f"Invalid configuration data")
                        return False
                else:
                    self.log_test("Le Figaro Site Config", False, f"Missing expected fields")
                    return False
            else:
                self.log_test("Le Figaro Site Config", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Le Figaro Site Config", False, f"Exception: {str(e)}")
            return False

    def test_site_config_unsupported(self):
        """Test unsupported site configuration"""
        try:
            response = requests.get(f"{self.api_url}/site-config/example.com", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data is None:
                    self.log_test("Unsupported Site Config", True, "Correctly returns None for unsupported site")
                    return True
                else:
                    self.log_test("Unsupported Site Config", False, "Should return None for unsupported site")
                    return False
            else:
                self.log_test("Unsupported Site Config", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unsupported Site Config", False, f"Exception: {str(e)}")
            return False

    def test_bypass_log_creation(self):
        """Test creating bypass logs"""
        try:
            log_data = {
                "action": "test_bypass",
                "domain": "lefigaro.fr",
                "url": "https://www.lefigaro.fr/test-article",
                "user_agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
                "success": True
            }
            
            response = requests.post(f"{self.api_url}/bypass-log", 
                                   json=log_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["id", "action", "domain", "url", "timestamp", "success"]
                
                if all(field in data for field in expected_fields):
                    self.log_test("Bypass Log Creation", True, f"Log created with ID: {data['id']}")
                    return data["id"]
                else:
                    self.log_test("Bypass Log Creation", False, "Missing expected fields in response")
                    return None
            else:
                self.log_test("Bypass Log Creation", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Bypass Log Creation", False, f"Exception: {str(e)}")
            return None

    def test_bypass_stats(self):
        """Test bypass statistics endpoint"""
        try:
            response = requests.get(f"{self.api_url}/bypass-stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["total_bypasses", "bypasses_today", "bypasses_this_week", 
                                 "most_bypassed_sites", "success_rate"]
                
                if all(field in data for field in expected_fields):
                    # Verify data types
                    if (isinstance(data["total_bypasses"], int) and
                        isinstance(data["bypasses_today"], int) and
                        isinstance(data["success_rate"], (int, float)) and
                        isinstance(data["most_bypassed_sites"], list)):
                        self.log_test("Bypass Statistics", True, 
                                    f"Total: {data['total_bypasses']}, Today: {data['bypasses_today']}, Success Rate: {data['success_rate']}%")
                        return True
                    else:
                        self.log_test("Bypass Statistics", False, "Invalid data types in response")
                        return False
                else:
                    self.log_test("Bypass Statistics", False, "Missing expected fields")
                    return False
            else:
                self.log_test("Bypass Statistics", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Bypass Statistics", False, f"Exception: {str(e)}")
            return False

    def test_update_rules(self):
        """Test rules update endpoint"""
        try:
            response = requests.post(f"{self.api_url}/update-rules", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["success", "message", "updated_sites", "timestamp"]
                
                if all(field in data for field in expected_fields):
                    if data["success"] and data["updated_sites"] > 0:
                        self.log_test("Update Rules", True, f"Updated {data['updated_sites']} sites")
                        return True
                    else:
                        self.log_test("Update Rules", False, "Update reported as unsuccessful")
                        return False
                else:
                    self.log_test("Update Rules", False, "Missing expected fields")
                    return False
            else:
                self.log_test("Update Rules", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Update Rules", False, f"Exception: {str(e)}")
            return False

    def test_supported_sites(self):
        """Test supported sites endpoint"""
        try:
            response = requests.get(f"{self.api_url}/supported-sites", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Supported Sites", True, f"Found {len(data)} supported sites")
                    return True
                else:
                    self.log_test("Supported Sites", False, "Response should be a list")
                    return False
            else:
                self.log_test("Supported Sites", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Supported Sites", False, f"Exception: {str(e)}")
            return False

    def test_bypass_test(self):
        """Test bypass test endpoint"""
        try:
            test_url = "https://www.lefigaro.fr/test-article"
            response = requests.post(f"{self.api_url}/test-bypass", 
                                   params={"url": test_url}, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["success", "domain", "supported", "message"]
                
                if all(field in data for field in expected_fields):
                    if data["success"] and data["domain"] == "lefigaro.fr" and data["supported"]:
                        self.log_test("Bypass Test", True, f"Test successful for {data['domain']}")
                        return True
                    else:
                        self.log_test("Bypass Test", False, "Test failed or unsupported domain")
                        return False
                else:
                    self.log_test("Bypass Test", False, "Missing expected fields")
                    return False
            else:
                self.log_test("Bypass Test", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Bypass Test", False, f"Exception: {str(e)}")
            return False

    def test_legacy_status_endpoints(self):
        """Test legacy status endpoints for compatibility"""
        try:
            # Test status creation
            status_data = {"client_name": "test_extension"}
            response = requests.post(f"{self.api_url}/status", 
                                   json=status_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "client_name" in data:
                    # Test status retrieval
                    response = requests.get(f"{self.api_url}/status", timeout=10)
                    if response.status_code == 200:
                        status_list = response.json()
                        if isinstance(status_list, list):
                            self.log_test("Legacy Status Endpoints", True, f"Created and retrieved status checks")
                            return True
                        else:
                            self.log_test("Legacy Status Endpoints", False, "Status list should be array")
                            return False
                    else:
                        self.log_test("Legacy Status Endpoints", False, f"GET status failed: {response.status_code}")
                        return False
                else:
                    self.log_test("Legacy Status Endpoints", False, "Missing fields in status creation response")
                    return False
            else:
                self.log_test("Legacy Status Endpoints", False, f"Status creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Legacy Status Endpoints", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Bypass Paywalls Clean Backend API Tests")
        print(f"🔗 Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Core API tests
        self.test_api_root()
        self.test_site_config_lefigaro()
        self.test_site_config_unsupported()
        
        # Bypass functionality tests
        log_id = self.test_bypass_log_creation()
        self.test_bypass_stats()
        self.test_update_rules()
        self.test_supported_sites()
        self.test_bypass_test()
        
        # Legacy compatibility tests
        self.test_legacy_status_endpoints()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the issues above.")
            return 1

def main():
    """Main test execution"""
    tester = BypassPaywallsAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())