# 🚀 Step-by-Step Guide: Running /etc/passwd Privilege Escalation Test Cases

This guide will walk you through setting up and running all the test cases for the Kubernetes privilege escalation lab.

## 📋 Prerequisites

Before starting, ensure you have:
- `kubectl` installed and configured
- `docker` installed and running
- `python3` installed
- Access to a Kubernetes cluster (local or remote)

## 🔧 Step 1: Build Docker Images

### 1.1 Build Standard Vulnerable Image
```bash
# Build the main vulnerable image
docker build -t abhishekbv/passwd-lab:latest .
```

### 1.2 Build Busybox-based Image
```bash
# Build the busybox-based image
docker build -f Dockerfile-busybox -t abhishekbv/passwd-lab-busybox:latest .
```

### 1.3 (Optional) Push Images to Registry
```bash
# If you want to push to Docker Hub
docker push abhishekbv/passwd-lab:latest
docker push abhishekbv/passwd-lab-busybox:latest
```

## 🏗️ Step 2: Create Kubernetes Namespace

```bash
# Create the namespace for our lab
kubectl create namespace passwd-lab
```

## 📦 Step 3: Deploy Test Pods

### 3.1 Deploy Standard Vulnerable Pod
```bash
kubectl apply -f vuln-pod.yaml
```

### 3.2 Deploy No-Capabilities Pod
```bash
kubectl apply -f vuln-pod-no-capabilities.yaml
```

### 3.3 Deploy Busybox Pod
```bash
kubectl apply -f vuln-pod-busybox.yaml
```

### 3.4 Verify Pods are Running
```bash
kubectl get pods -n passwd-lab
```

Wait until all pods show `Running` status.

## 🧪 Step 4: Run Test Cases

### Test Case 1: External Python Script (Runs from outside container)

This script tests the privilege escalation scenario from outside the container:

```bash
python3 passwd_external.py
```

**What it does:**
- Connects to the vulnerable pod via kubectl
- Checks file permissions remotely
- Attempts privilege escalation
- Reports success/failure

**Expected Output:**
```
🔓 Kubernetes /etc/passwd Privilege Escalation Test
============================================================
[+] Pod vuln-passwd-pod is running in namespace passwd-lab
[*] Testing file permissions inside the pod...
[*] /etc/passwd permissions: -rw-rw-rw- 1 root root 1234 Dec 1 12:00 /etc/passwd
[*] /etc/shadow permissions: -rw-rw-rw- 1 root shadow 1234 Dec 1 12:00 /etc/shadow
[+] Files are writable. Proceeding with exploitation...
[*] Attempting privilege escalation...
[*] Generated password hash: $6$...
[+] Successfully added fake user 'hacked' with UID 0
[*] Verification - /etc/passwd entry: hacked:x:0:0:root:/root:/bin/bash
[*] User ID as 'hacked': uid=0(root) gid=0(root) groups=0(root)

🎯 PRIVILEGE ESCALATION SUCCESSFUL!
[*] The container is vulnerable to /etc/passwd exploitation
```

### Test Case 2: No Capabilities Scenario

This tests the scenario where all capabilities are dropped:

```bash
# First, check the pod's capabilities
kubectl exec -it -n passwd-lab vuln-passwd-pod-no-caps -- bash -c "cat /proc/1/status | grep CapEff"

# Expected output: CapEff: 0000000000000000 (all capabilities dropped)

# Now test privilege escalation
kubectl exec -it -n passwd-lab vuln-passwd-pod-no-caps -- python3 passwd.py
```

**Expected Behavior:**
- Files are still writable (due to Dockerfile configuration)
- Privilege escalation should still work (demonstrating that dropping capabilities alone doesn't prevent this attack)
- This shows the importance of proper file permissions

### Test Case 3: Busybox Container (No OpenSSL, No SU)

This tests exploitation in a minimal container:

```bash
# Check what tools are available
kubectl exec -it -n passwd-lab vuln-passwd-pod-busybox -- bash -c "which openssl || echo 'No openssl'"
kubectl exec -it -n passwd-lab vuln-passwd-pod-busybox -- bash -c "which su || echo 'No su'"
kubectl exec -it -n passwd-lab vuln-passwd-pod-busybox -- bash -c "which busybox && echo 'Busybox available'"

# Run the busybox-specific exploit script
kubectl exec -it -n passwd-lab vuln-passwd-pod-busybox -- python3 passwd_busybox.py
```

**What it does:**
- Detects available tools (busybox, openssl, su)
- Uses alternative methods for password hash generation
- Handles missing `su` command gracefully
- Tests privilege escalation with limited tools

### Test Case 4: Comprehensive Test Suite

Run all test cases with detailed reporting:

```bash
python3 test_cases.py
```

**What it does:**
- Tests all scenarios automatically
- Provides detailed pass/fail results
- Shows test summary with success rates
- Tests conditional scenarios (if-else logic)

**Expected Output:**
```
🚀 Starting Comprehensive Privilege Escalation Tests
======================================================================

🔍 Test Case 1: Standard Vulnerable Pod
==================================================
✅ PASS Pod Existence: Pod vuln-passwd-pod is running
✅ PASS File Permissions: /etc/passwd is world writable
✅ PASS Privilege Escalation: Successfully exploited /etc/passwd

🔍 Test Case 2: No Capabilities Pod
==================================================
✅ PASS Pod Existence: Pod vuln-passwd-pod-no-caps is running
✅ PASS Capabilities Check: All capabilities dropped
✅ PASS File Permissions: /etc/passwd is world writable
✅ PASS Privilege Escalation: WARNING: Privilege escalation still possible despite no capabilities

📊 TEST SUMMARY
======================================================================
Total Tests: 12
Passed: 12
Failed: 0
Success Rate: 100.0%
```

## 🎯 Manual Testing (Alternative Approach)

If you prefer to test manually instead of using the automated scripts:

### Manual Test 1: Inside Standard Container
```bash
# Access the container
kubectl exec -it -n passwd-lab vuln-passwd-pod -- /bin/bash

# Check file permissions
ls -la /etc/passwd
ls -la /etc/shadow

# Run exploit
python3 passwd.py

# Verify user was added
grep hacked /etc/passwd
grep hacked /etc/shadow

# Try to switch to hacked user
su hacked
id
```

### Manual Test 2: No Capabilities
```bash
# Access the no-capabilities container
kubectl exec -it -n passwd-lab vuln-passwd-pod-no-caps -- /bin/bash

# Check capabilities
cat /proc/1/status | grep CapEff

# Check file permissions
ls -la /etc/passwd

# Try exploit
python3 passwd.py
```

### Manual Test 3: Busybox Container
```bash
# Access the busybox container
kubectl exec -it -n passwd-lab vuln-passwd-pod-busybox -- /bin/bash

# Check available tools
which openssl
which su
which busybox

# Run busybox exploit
python3 passwd_busybox.py
```

## 🧹 Step 5: Cleanup

When you're done testing:

```bash
# Delete all pods and namespace
kubectl delete namespace passwd-lab

# Or use the cleanup script
./setup_and_run.sh cleanup
```

## 🚨 Troubleshooting

### Common Issues:

1. **Pods not starting:**
   ```bash
   kubectl describe pod <pod-name> -n passwd-lab
   kubectl logs <pod-name> -n passwd-lab
   ```

2. **Permission denied errors:**
   - Ensure you have access to the namespace
   - Check if your kubectl context is correct

3. **Docker build failures:**
   - Ensure Docker daemon is running
   - Check available disk space

4. **Python import errors:**
   - Ensure all required Python packages are installed
   - Check Python version compatibility

### Verification Commands:

```bash
# Check namespace exists
kubectl get namespace passwd-lab

# Check pod status
kubectl get pods -n passwd-lab

# Check pod details
kubectl describe pod vuln-passwd-pod -n passwd-lab

# Check container logs
kubectl logs vuln-passwd-pod -n passwd-lab
```

## 📊 Expected Results Summary

| Test Case | Expected Result | Security Implication |
|-----------|----------------|---------------------|
| Standard Pod | ✅ Privilege escalation successful | Container is vulnerable |
| No Capabilities | ✅ Privilege escalation still works | Dropping capabilities alone is insufficient |
| Busybox Container | ✅ Privilege escalation successful | Minimal containers are still vulnerable |
| External Script | ✅ Remote exploitation possible | Attack can be performed from outside |

## 🔒 Security Lessons

1. **File permissions matter more than capabilities** - Even with all capabilities dropped, writable `/etc/passwd` allows privilege escalation
2. **Container minimalism doesn't prevent attacks** - Busybox containers can still be exploited
3. **External access is dangerous** - Attacks can be performed remotely via kubectl
4. **Defense in depth is crucial** - Multiple security layers are needed

## 🎓 Learning Objectives

By completing these test cases, you'll understand:
- How `/etc/passwd` writability leads to privilege escalation
- Why dropping capabilities alone isn't sufficient
- How to exploit containers with minimal tools
- The importance of proper file permissions in container security
- How to test security configurations systematically 