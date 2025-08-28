#!/usr/bin/env python3
"""
Comprehensive Test Cases for /etc/passwd Privilege Escalation
This script tests various scenarios with if-else logic
"""

import os
import subprocess
import sys
import time

class PrivilegeEscalationTester:
    def __init__(self, namespace="passwd-lab"):
        self.namespace = namespace
        self.test_results = {}
        
    def log_test(self, test_name, result, details=""):
        """Log test results"""
        status = "✅ PASS" if result else "❌ FAIL"
        self.test_results[test_name] = {
            'result': result,
            'details': details,
            'status': status
        }
        print(f"{status} {test_name}: {details}")
    
    def check_pod_exists(self, pod_name):
        """Check if a pod exists and is running"""
        try:
            result = subprocess.run([
                'kubectl', 'get', 'pod', pod_name, 
                '-n', self.namespace, '-o', 'jsonpath={.status.phase}'
            ], capture_output=True, text=True, check=True)
            return result.stdout.strip() == 'Running'
        except subprocess.CalledProcessError:
            return False
    
    def exec_in_pod(self, pod_name, command):
        """Execute command in pod"""
        try:
            result = subprocess.run([
                'kubectl', 'exec', '-n', self.namespace, pod_name, '--', 'bash', '-c', command
            ], capture_output=True, text=True, check=True)
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            return e.stdout.strip(), e.stderr.strip()
    
    def test_case_1_vulnerable_pod(self):
        """Test Case 1: Standard vulnerable pod"""
        print("\n🔍 Test Case 1: Standard Vulnerable Pod")
        print("=" * 50)
        
        pod_name = "vuln-passwd-pod"
        
        # Check if pod exists
        if not self.check_pod_exists(pod_name):
            self.log_test("Pod Existence", False, f"Pod {pod_name} not found")
            return False
        
        self.log_test("Pod Existence", True, f"Pod {pod_name} is running")
        
        # Check file permissions
        stdout, stderr = self.exec_in_pod(pod_name, "ls -la /etc/passwd")
        if "666" in stdout:
            self.log_test("File Permissions", True, "/etc/passwd is world writable")
        else:
            self.log_test("File Permissions", False, "/etc/passwd is not world writable")
            return False
        
        # Test privilege escalation
        stdout, stderr = self.exec_in_pod(pod_name, "python3 passwd.py")
        if "SUCCESSFUL" in stdout or "hacked" in stdout:
            self.log_test("Privilege Escalation", True, "Successfully exploited /etc/passwd")
        else:
            self.log_test("Privilege Escalation", False, "Failed to exploit /etc/passwd")
            return False
        
        return True
    
    def test_case_2_no_capabilities(self):
        """Test Case 2: Pod with no capabilities"""
        print("\n🔍 Test Case 2: No Capabilities Pod")
        print("=" * 50)
        
        pod_name = "vuln-passwd-pod-no-caps"
        
        # Check if pod exists
        if not self.check_pod_exists(pod_name):
            self.log_test("Pod Existence", False, f"Pod {pod_name} not found")
            return False
        
        self.log_test("Pod Existence", True, f"Pod {pod_name} is running")
        
        # Check capabilities
        stdout, stderr = self.exec_in_pod(pod_name, "cat /proc/1/status | grep CapEff")
        if "0000000000000000" in stdout:
            self.log_test("Capabilities Check", True, "All capabilities dropped")
        else:
            self.log_test("Capabilities Check", False, "Capabilities not fully dropped")
        
        # Check file permissions
        stdout, stderr = self.exec_in_pod(pod_name, "ls -la /etc/passwd")
        if "666" in stdout:
            self.log_test("File Permissions", True, "/etc/passwd is world writable")
        else:
            self.log_test("File Permissions", False, "/etc/passwd is not world writable")
            return False
        
        # Test privilege escalation attempt
        stdout, stderr = self.exec_in_pod(pod_name, "python3 passwd.py")
        if "SUCCESSFUL" in stdout or "hacked" in stdout:
            self.log_test("Privilege Escalation", True, "WARNING: Privilege escalation still possible despite no capabilities")
        else:
            self.log_test("Privilege Escalation", False, "Privilege escalation blocked (expected behavior)")
        
        return True
    
    def test_case_3_alpine_container(self):
        """Test Case 3: Alpine-based container"""
        print("\n🔍 Test Case 3: Alpine Container")
        print("=" * 50)
        
        pod_name = "vuln-passwd-pod-alpine"
        
        # Check if pod exists
        if not self.check_pod_exists(pod_name):
            self.log_test("Pod Existence", False, f"Pod {pod_name} not found")
            return False
        
        self.log_test("Pod Existence", True, f"Pod {pod_name} is running")
        
        # Check available tools
        stdout, stderr = self.exec_in_pod(pod_name, "which openssl")
        if stdout:
            self.log_test("OpenSSL Available", True, "OpenSSL found in container")
        else:
            self.log_test("OpenSSL Available", False, "OpenSSL not available (expected)")
        
        stdout, stderr = self.exec_in_pod(pod_name, "which su")
        if stdout:
            self.log_test("SU Available", True, "SU command found")
        else:
            self.log_test("SU Available", False, "SU command not available")
        
        stdout, stderr = self.exec_in_pod(pod_name, "which busybox")
        if stdout:
            self.log_test("Busybox Available", True, "Busybox found")
        else:
            self.log_test("Busybox Available", False, "Busybox not available")
        
        # Check file permissions
        stdout, stderr = self.exec_in_pod(pod_name, "ls -la /etc/passwd")
        if "666" in stdout:
            self.log_test("File Permissions", True, "/etc/passwd is world writable")
        else:
            self.log_test("File Permissions", False, "/etc/passwd is not world writable")
            return False
        
        # Test privilege escalation
        stdout, stderr = self.exec_in_pod(pod_name, "python3 passwd_busybox.py")
        if "SUCCESSFUL" in stdout or "hacked" in stdout:
            self.log_test("Privilege Escalation", True, "Successfully exploited /etc/passwd in busybox container")
        else:
            self.log_test("Privilege Escalation", False, "Failed to exploit /etc/passwd in busybox container")
        
        return True
    
    def test_case_4_conditional_scenarios(self):
        """Test Case 4: Conditional privilege escalation scenarios"""
        print("\n🔍 Test Case 4: Conditional Scenarios")
        print("=" * 50)
        
        # Test different conditions
        test_conditions = [
            {
                'name': 'File Writable + User 1000',
                'condition': lambda: self.test_file_writable_and_user_1000(),
                'expected': True
            },
            {
                'name': 'File Writable + User 0',
                'condition': lambda: self.test_file_writable_and_user_0(),
                'expected': True
            },
            {
                'name': 'File Not Writable + Any User',
                'condition': lambda: self.test_file_not_writable(),
                'expected': False
            }
        ]
        
        for test in test_conditions:
            result = test['condition']()
            expected = test['expected']
            
            if result == expected:
                self.log_test(test['name'], True, f"Expected: {expected}, Got: {result}")
            else:
                self.log_test(test['name'], False, f"Expected: {expected}, Got: {result}")
    
    def test_file_writable_and_user_1000(self):
        """Test if files are writable and user is 1000"""
        pod_name = "vuln-passwd-pod"
        if not self.check_pod_exists(pod_name):
            return False
        
        stdout, stderr = self.exec_in_pod(pod_name, "id")
        if "uid=1000" not in stdout:
            return False
        
        stdout, stderr = self.exec_in_pod(pod_name, "test -w /etc/passwd && echo 'writable'")
        return "writable" in stdout
    
    def test_file_writable_and_user_0(self):
        """Test if files are writable and user is 0 (root)"""
        pod_name = "vuln-passwd-pod"
        if not self.check_pod_exists(pod_name):
            return False
        
        # Temporarily switch to root
        stdout, stderr = self.exec_in_pod(pod_name, "sudo -n id 2>/dev/null || echo 'no sudo'")
        if "no sudo" in stdout:
            return False
        
        stdout, stderr = self.exec_in_pod(pod_name, "test -w /etc/passwd && echo 'writable'")
        return "writable" in stdout
    
    def test_file_not_writable(self):
        """Test scenario where files are not writable"""
        # This would require a secure pod configuration
        # For now, we'll simulate this by checking if we can make files non-writable
        pod_name = "vuln-passwd-pod"
        if not self.check_pod_exists(pod_name):
            return False
        
        # Try to make files non-writable (this should fail for non-root users)
        stdout, stderr = self.exec_in_pod(pod_name, "chmod 644 /etc/passwd 2>&1")
        if "Permission denied" in stderr or "Operation not permitted" in stderr:
            return True  # Files are protected
        return False
    
    def run_all_tests(self):
        """Run all test cases"""
        print("🚀 Starting Comprehensive Privilege Escalation Tests")
        print("=" * 70)
        
        test_functions = [
            self.test_case_1_vulnerable_pod,
            self.test_case_2_no_capabilities,
            self.test_case_3_alpine_container,
            self.test_case_4_conditional_scenarios
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                self.log_test(test_func.__name__, False, f"Test failed with error: {e}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results.values() if result['result'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            print(f"  {result['status']} {test_name}")
            if result['details']:
                print(f"    Details: {result['details']}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        namespace = sys.argv[1]
    else:
        namespace = "passwd-lab"
    
    tester = PrivilegeEscalationTester(namespace)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 