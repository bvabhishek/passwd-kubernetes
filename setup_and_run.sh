#!/bin/bash

# Kubernetes /etc/passwd Privilege Escalation Lab Setup and Test Script
# This script sets up the lab environment and runs all test cases

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="passwd-lab"
REGISTRY="abhishekbv"

echo -e "${BLUE}🔓 Kubernetes /etc/passwd Privilege Escalation Lab${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    print_status "kubectl found"
}

# Function to check if docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "docker is not installed or not in PATH"
        exit 1
    fi
    print_status "docker found"
}

# Function to build and push Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build standard vulnerable image
    print_status "Building standard vulnerable image..."
    docker build -t ${REGISTRY}/passwd-lab:latest .
    
    # Build busybox-based image
    print_status "Building busybox-based image..."
    docker build -f Dockerfile-busybox -t ${REGISTRY}/passwd-lab-busybox:latest .
    
    print_status "Docker images built successfully"
}

# Function to push Docker images
push_images() {
    print_status "Pushing Docker images to registry..."
    
    # Check if user wants to push images
    read -p "Do you want to push images to Docker Hub? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker push ${REGISTRY}/passwd-lab:latest
        docker push ${REGISTRY}/passwd-lab-busybox:latest
        print_status "Images pushed successfully"
    else
        print_warning "Skipping image push. Using local images."
    fi
}

# Function to create namespace
create_namespace() {
    print_status "Creating namespace: ${NAMESPACE}"
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
}

# Function to deploy pods
deploy_pods() {
    print_status "Deploying test pods..."
    
    # Deploy standard vulnerable pod
    print_status "Deploying standard vulnerable pod..."
    kubectl apply -f vuln-pod.yaml
    
    # Deploy no-capabilities pod
    print_status "Deploying no-capabilities pod..."
    kubectl apply -f vuln-pod-no-capabilities.yaml
    
    # Deploy busybox pod
    print_status "Deploying busybox pod..."
    kubectl apply -f vuln-pod-busybox.yaml
    
    # Wait for pods to be ready
    print_status "Waiting for pods to be ready..."
    kubectl wait --for=condition=Ready pod/vuln-passwd-pod -n ${NAMESPACE} --timeout=60s
    kubectl wait --for=condition=Ready pod/vuln-passwd-pod-no-caps -n ${NAMESPACE} --timeout=60s
    kubectl wait --for=condition=Ready pod/vuln-passwd-pod-busybox -n ${NAMESPACE} --timeout=60s
    
    print_status "All pods are ready"
}

# Function to show pod status
show_pod_status() {
    print_status "Current pod status:"
    kubectl get pods -n ${NAMESPACE}
    echo
}

# Function to run test cases
run_tests() {
    print_status "Running test cases..."
    
    # Test Case 1: External Python script
    print_status "Test Case 1: Running external Python script..."
    python3 passwd_external.py
    
    echo
    print_status "Test Case 2: Testing no-capabilities scenario..."
    # This will be tested in the comprehensive test suite
    
    echo
    print_status "Test Case 3: Testing busybox container..."
    # This will be tested in the comprehensive test suite
    
    echo
    print_status "Test Case 4: Running comprehensive test suite..."
    python3 test_cases.py
}

# Function to show manual test instructions
show_manual_tests() {
    echo
    print_status "Manual Test Instructions:"
    echo "=============================="
    echo
    echo "1. Test from inside containers:"
    echo "   kubectl exec -it -n ${NAMESPACE} vuln-passwd-pod -- /bin/bash"
    echo "   python3 passwd.py"
    echo
    echo "2. Test no-capabilities pod:"
    echo "   kubectl exec -it -n ${NAMESPACE} vuln-passwd-pod-no-caps -- /bin/bash"
    echo "   python3 passwd.py"
    echo
    echo "3. Test busybox container:"
    echo "   kubectl exec -it -n ${NAMESPACE} vuln-passwd-pod-busybox -- /bin/bash"
    echo "   python3 passwd_busybox.py"
    echo
    echo "4. Check file permissions:"
    echo "   ls -la /etc/passwd"
    echo "   ls -la /etc/shadow"
    echo
    echo "5. Check capabilities:"
    echo "   cat /proc/1/status | grep CapEff"
}

# Function to cleanup
cleanup() {
    print_warning "Cleaning up lab environment..."
    kubectl delete namespace ${NAMESPACE} --ignore-not-found=true
    print_status "Cleanup completed"
}

# Main execution
main() {
    echo "Choose an option:"
    echo "1. Full setup and run all tests"
    echo "2. Setup only (build images and deploy pods)"
    echo "3. Run tests only (assumes setup is complete)"
    echo "4. Manual test instructions"
    echo "5. Cleanup"
    echo "6. Exit"
    
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1)
            check_kubectl
            check_docker
            build_images
            push_images
            create_namespace
            deploy_pods
            show_pod_status
            run_tests
            show_manual_tests
            ;;
        2)
            check_kubectl
            check_docker
            build_images
            push_images
            create_namespace
            deploy_pods
            show_pod_status
            ;;
        3)
            run_tests
            ;;
        4)
            show_manual_tests
            ;;
        5)
            cleanup
            ;;
        6)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
}

# Handle script arguments
if [[ $# -eq 0 ]]; then
    main
else
    case $1 in
        "setup")
            check_kubectl
            check_docker
            build_images
            push_images
            create_namespace
            deploy_pods
            show_pod_status
            ;;
        "test")
            run_tests
            ;;
        "cleanup")
            cleanup
            ;;
        "help")
            echo "Usage: $0 [setup|test|cleanup|help]"
            echo "  setup   - Build images and deploy pods"
            echo "  test    - Run all test cases"
            echo "  cleanup - Remove lab environment"
            echo "  help    - Show this help message"
            echo "  no args - Interactive menu"
            ;;
        *)
            print_error "Unknown argument: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
fi 