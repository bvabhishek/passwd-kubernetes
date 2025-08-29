#!/bin/bash

# Build Images Script with Rate Limit Handling
# This script builds Docker images with fallback options for rate limits

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[*]${NC} $1"
}

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        print_info "Trying podman..."
        if command -v podman &> /dev/null; then
            print_status "Podman found, using it instead"
            DOCKER_CMD="podman"
        else
            print_error "Neither Docker nor Podman found"
            exit 1
        fi
    else
        DOCKER_CMD="docker"
        print_status "Docker found"
    fi
}

# Function to build with fallback
build_with_fallback() {
    local dockerfile=$1
    local tag=$2
    local fallback_base=$3
    
    print_info "Building $tag from $dockerfile..."
    
    # Try building with original Dockerfile
    if $DOCKER_CMD build -t "$tag" -f "$dockerfile" .; then
        print_status "Successfully built $tag"
        return 0
    else
        print_warning "Build failed, trying with fallback base image..."
        
        # Create temporary Dockerfile with fallback base
        local temp_dockerfile="Dockerfile.temp"
        sed "s|^FROM .*|FROM $fallback_base|" "$dockerfile" > "$temp_dockerfile"
        
        if $DOCKER_CMD build -t "$tag" -f "$temp_dockerfile" .; then
            print_status "Successfully built $tag with fallback base image"
            rm -f "$temp_dockerfile"
            return 0
        else
            print_error "Failed to build $tag even with fallback"
            rm -f "$temp_dockerfile"
            return 1
        fi
    fi
}

# Function to handle rate limit
handle_rate_limit() {
    print_warning "Docker Hub rate limit detected!"
    print_info "Solutions:"
    echo "  1. Wait 6 hours for rate limit to reset"
    echo "  2. Login to Docker Hub: docker login"
    echo "  3. Use alternative base images (already configured)"
    echo "  4. Use local images if available"
}

# Main execution
main() {
    print_info "🔓 Kubernetes /etc/passwd Privilege Escalation Lab - Image Builder"
    print_info "================================================================"
    
    # Check Docker/Podman availability
    check_docker
    
    print_info "Using: $DOCKER_CMD"
    
    # Build standard image
    print_info "Building standard vulnerable image..."
    if build_with_fallback "Dockerfile" "passwd-lab:latest" "debian:bullseye-slim"; then
        print_status "Standard image built successfully"
    else
        print_error "Failed to build standard image"
        exit 1
    fi
    
    # Build Alpine image
    print_info "Building Alpine-based image..."
    if build_with_fallback "Dockerfile-alpine" "passwd-lab-alpine:latest" "debian:bullseye-slim"; then
        print_status "Alpine image built successfully"
    else
        print_error "Failed to build Alpine image"
        exit 1
    fi
    
    print_info "All images built successfully!"
    print_info "You can now deploy the pods:"
    echo "  kubectl apply -f vuln-pod.yaml"
    echo "  kubectl apply -f vuln-pod-alpine.yaml"
    echo "  kubectl apply -f vuln-pod-no-capabilities.yaml"
}

# Handle errors
trap 'print_error "Build failed. Check the error messages above."' ERR

# Run main function
main "$@"
