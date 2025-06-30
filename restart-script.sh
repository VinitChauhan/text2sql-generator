#!/bin/bash

# Docker Compose Project Restart Script
# This script scans docker-compose files, brings down containers, and rebuilds them

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}[HEADER]${NC} $1"
}

# Function to find docker-compose files
find_compose_files() {
    local compose_files=()
    
    # Common docker-compose file names
    local file_patterns=("docker-compose.yml" "docker-compose.yaml" "compose.yml" "compose.yaml")
    
    for pattern in "${file_patterns[@]}"; do
        if [ -f "$pattern" ]; then
            compose_files+=("$pattern")
        fi
    done
    
    # Also check for docker-compose files with different suffixes
    for file in docker-compose*.yml docker-compose*.yaml; do
        if [ -f "$file" ] && [[ ! " ${compose_files[@]} " =~ " ${file} " ]]; then
            compose_files+=("$file")
        fi
    done
    
    echo "${compose_files[@]}"
}

# Function to get compose command with file arguments
get_compose_command() {
    local files=("$@")
    local cmd="docker-compose"
    
    for file in "${files[@]}"; do
        cmd="$cmd -f $file"
    done
    
    echo "$cmd"
}

# Function to scan and display containers from compose file
scan_containers() {
    local compose_cmd="$1"
    print_status "Scanning containers from docker-compose configuration..."
    
    # Get service names
    local services=$(eval "$compose_cmd config --services" 2>/dev/null || echo "")
    
    if [ -z "$services" ]; then
        print_warning "No services found in docker-compose configuration"
        return 1
    fi
    
    print_header "Found the following services:"
    echo "$services" | while read -r service; do
        echo -e "  ${CYAN}→${NC} $service"
    done
    
    # Get currently running containers for this project
    local running_containers=$(eval "$compose_cmd ps -q" 2>/dev/null || echo "")
    
    if [ -n "$running_containers" ]; then
        print_header "Currently running containers:"
        eval "$compose_cmd ps --format table"
    else
        print_warning "No containers are currently running for this project"
    fi
    
    return 0
}

# Function to bring down containers
bring_down_containers() {
    local compose_cmd="$1"
    print_status "Bringing down all containers..."
    
    # Stop and remove containers, networks, volumes, and images created by docker-compose
    if eval "$compose_cmd down --volumes --remove-orphans" 2>/dev/null; then
        print_success "All containers brought down successfully"
    else
        print_warning "Some issues occurred while bringing down containers, continuing..."
    fi
}

# Function to build and bring up containers
build_and_bring_up() {
    local compose_cmd="$1"
    print_status "Building and bringing up all containers..."
    
    # Build and start containers in detached mode
    if eval "$compose_cmd up --build -d"; then
        print_success "All containers built and started successfully"
    else
        print_error "Failed to build and start containers"
        return 1
    fi
}

# Function to show final status
show_final_status() {
    local compose_cmd="$1"
    print_header "Final container status:"
    eval "$compose_cmd ps"
    
    print_header "Container logs (last 10 lines per service):"
    eval "$compose_cmd logs --tail=10"
}

# Main script starts here
print_header "Docker Compose Project Restart Script"
print_status "Starting container restart process..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Get current directory name for project identification
PROJECT_DIR=$(basename "$(pwd)")
print_status "Working on project: $PROJECT_DIR"

# Find docker-compose files
COMPOSE_FILES=($(find_compose_files))

if [ ${#COMPOSE_FILES[@]} -eq 0 ]; then
    print_error "No docker-compose files found in current directory!"
    print_error "Please run this script from a directory containing docker-compose.yml or similar files."
    exit 1
fi

print_success "Found docker-compose files: ${COMPOSE_FILES[*]}"

# Build the compose command
COMPOSE_CMD=$(get_compose_command "${COMPOSE_FILES[@]}")
print_status "Using command: $COMPOSE_CMD"

# Step 1: Scan and display current containers
if ! scan_containers "$COMPOSE_CMD"; then
    print_error "Failed to scan docker-compose configuration"
    exit 1
fi

# Ask for confirmation
# echo
# read -p "Do you want to proceed with restarting all containers? (y/n): " -n 1 -r
# echo
# if [[ ! $REPLY =~ ^[Yy]$ ]]; then
#     print_warning "Operation cancelled by user"
#     exit 0
# fi

# Step 2: Bring down all containers
bring_down_containers "$COMPOSE_CMD"

# Step 3: Wait for 5 seconds
print_status "Waiting 5 seconds before rebuilding..."
for i in {3..1}; do
    echo -ne "\rWaiting... $i seconds remaining"
    sleep 1
done
echo -e "\n"

# Step 4: Build and bring up containers
if ! build_and_bring_up "$COMPOSE_CMD"; then
    print_error "Failed to restart containers"
    exit 1
fi

# Step 5: Wait a moment for containers to fully start
print_status "Waiting for containers to fully start..."
sleep 3

# Step 6: Show final status
show_final_status "$COMPOSE_CMD"

print_success "Container restart process completed successfully!"

# Optional: Show real-time logs
# echo
# read -p "Do you want to follow the logs in real-time? (y/n): " -n 1 -r
# echo
# if [[ $REPLY =~ ^[Yy]$ ]]; then
#     print_status "Following logs... (Press Ctrl+C to stop)"
#     eval "$compose_cmd logs -f"
# fi