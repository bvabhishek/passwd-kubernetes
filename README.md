# ☸️ Kubernetes Privilege Escalation Lab: `/etc/passwd` Exploitation

This lab demonstrates how writable permissions on `/etc/passwd` and `/etc/shadow` inside a container can lead to **privilege escalation** in a Kubernetes environment.

---

## 📁 Project Structure

passwd-kubernetes/
├── Dockerfile # Builds the vulnerable image
├── passwd.py # Exploit script
├── namespace.yaml # Namespace definition
└── vuln-pod.yaml # Pod definition using the custom image

---

## 🐳 Step 1: Build & Push Docker Image

Make sure you're in the `passwd-kubernetes/` directory.

```bash
docker build -t abhishekbv/passwd-lab:latest .
docker push abhishekbv/passwd-lab:latest
🛠️ Step 2: Create Kubernetes Namespace

# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: passwd-lab
Apply it:


kubectl apply -f namespace.yaml
📦 Step 3: Create Vulnerable Pod
# vuln-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: vuln-passwd-pod
  namespace: passwd-lab
spec:
  containers:
    - name: passwd-container
      image: abhishekbv/passwd-lab:latest
      command: ["/bin/bash", "-c", "sleep infinity"]
      securityContext:
        privileged: true
        runAsUser: 0
  restartPolicy: Always
Apply the pod:

kubectl apply -f vuln-pod.yaml
🔍 Step 4: Access the Pod

kubectl get pods -n passwd-lab
kubectl exec -it -n passwd-lab vuln-passwd-pod -- /bin/bash
📝 Step 5: Inspect File Permissions
Inside the pod:

ls -la /etc/passwd
ls -la /etc/shadow
✅ If both files are world-writable, the container is vulnerable to privilege escalation.

💥 Step 6: Run the Exploit
Still inside the pod:

python3 passwd.py
When prompted, enter:

password123
🔐 What Just Happened?
The script adds a fake user hacked with UID 0 to /etc/passwd and /etc/shadow.

This grants root-level access within the container.

Demonstrates poor container hardening and potential container escape risk.

🧠 Learning Outcome
This lab shows the critical risk of writable sensitive files inside containers. When deployed in Kubernetes (even as non-root), misconfigured containers can lead to root-level access and lateral movement if proper isolation is not enforced.

📌 Docker Image Used

DockerHub: abhishekbv/passwd-lab:latest
🧼 Cleanup

kubectl delete pod vuln-passwd-pod -n passwd-lab
kubectl delete ns passwd-lab
