# 🔓 Kubernetes /etc/passwd Privilege Escalation Lab

A comprehensive lab demonstrating privilege escalation vulnerabilities in Kubernetes containers through writable `/etc/passwd` and `/etc/shadow` files.

## 🎯 What This Lab Demonstrates

This lab shows how misconfigured container permissions can lead to privilege escalation, even when security measures like dropping capabilities are implemented.

## 📁 Project Structure

```
passwd-kubernetes/
├── README.md                           # This file
├── Dockerfile                          # Standard vulnerable container
├── Dockerfile-alpine                   # Alpine-based vulnerable container
├── vuln-pod.yaml                      # Standard vulnerable pod
├── vuln-pod-no-capabilities.yaml      # Pod with all capabilities dropped
├── vuln-pod-busybox.yaml              # Busybox-based pod
├── passwd.py                           # Basic exploit script
├── passwd_external.py                  # External testing script
├── passwd_busybox.py                   # Busybox-specific exploit
├── test_cases.py                       # Comprehensive test suite
└── setup_and_run.sh                    # Automated setup script
```

## 🚀 Quick Start

### 1. Build Docker Images
```bash
# Build standard vulnerable image
docker build -t passwd-lab:latest .

# Build alpine-based image
docker build -f Dockerfile-alpine -t passwd-lab-alpine:latest .
```

### 2. Create Kubernetes Namespace
```bash
kubectl create namespace passwd-lab
```

### 3. Deploy Test Pods
```bash
kubectl apply -f vuln-pod.yaml
kubectl apply -f vuln-pod-no-capabilities.yaml
kubectl apply -f vuln-pod-alpine.yaml
```

### 4. Run Tests
```bash
# Run comprehensive test suite
python3 test_cases.py

# Or run individual tests
python3 passwd_external.py
```

## 🧪 Test Cases

### Test Case 1: Standard Vulnerability
- **File:** `vuln-pod.yaml`
- **Purpose:** Basic privilege escalation test
- **Command:** `kubectl exec -it -n passwd-lab vuln-passwd-pod -- python3 passwd.py`

### Test Case 2: No Capabilities
- **File:** `vuln-pod-no-capabilities.yaml`
- **Purpose:** Test if dropping capabilities prevents privilege escalation
- **Command:** `kubectl exec -it -n passwd-lab vuln-passwd-pod-no-caps -- python3 passwd.py`

### Test Case 3: Alpine Container
- **File:** `vuln-pod-alpine.yaml`
- **Purpose:** Test exploitation in minimal Alpine containers without openssl/su
- **Command:** `kubectl exec -it -n passwd-lab vuln-passwd-pod-alpine -- python3 passwd_busybox.py`

### Test Case 4: External Testing
- **File:** `passwd_external.py`
- **Purpose:** Test privilege escalation from outside the container
- **Command:** `python3 passwd_external.py`

## 🔒 Security Lessons

1. **File permissions matter more than capabilities** - Dropping capabilities alone doesn't prevent this attack
2. **Container minimalism doesn't prevent attacks** - Even busybox containers can be exploited
3. **External access is dangerous** - Attacks can be performed remotely via kubectl
4. **Defense in depth is crucial** - Multiple security layers are needed

## 🧹 Cleanup

```bash
kubectl delete namespace passwd-lab
```

## 📚 Detailed Guide

For step-by-step instructions and troubleshooting, see [TEST_CASES_README.md](TEST_CASES_README.md).

## ⚠️ Disclaimer

This lab is for educational purposes only. Do not use these techniques on production systems or systems you don't own.
