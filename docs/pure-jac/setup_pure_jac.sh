#!/bin/bash
# =============================================================================
# Jeseci Smart Learning Academy - Pure JAC Setup
# Minimal setup for native JAC architecture
# Author: Cavin Otieno
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

print_header() {
    echo -e "\n${BLUE}🚀 $1${NC}\n"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

file_exists() {
    [ -f "$1" ]
}

dir_exists() {
    [ -d "$1" ]
}

# Show help
show_help() {
    echo "Jeseci Smart Learning Academy - Pure JAC Setup"
    echo ""
    echo "Usage: bash docs/pure-jac/setup_pure_jac.sh [options]"
    echo ""
    echo "Prerequisites:"
    echo "  - Python 3.12+ with pip installed"
    echo ""
    echo "Options:"
    echo "  --recreate    Recreate virtual environment"
    echo "  --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  bash docs/pure-jac/setup_pure_jac.sh              # Standard setup"
    echo "  bash docs/pure-jac/setup_pure_jac.sh --recreate   # Recreate venv"
    echo ""
    echo "If pip is not installed:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3-pip"
    echo "  macOS: brew install python3"
    echo "  Windows: Download Python from python.org (includes pip)"
    echo "  Or: python3 -m ensurepip --upgrade"
    exit 0
}

# Handle command line arguments
if [[ "$1" == "--help" ]]; then
    show_help
fi

main() {
    print_header "Jeseci Smart Learning Academy - Pure JAC Setup"
    print_info "Setting up minimal JAC architecture (no external databases)"
    
    # Check prerequisites
    print_header "Checking Prerequisites"
    
    if ! command_exists python3; then
        print_error "Python 3 is required. Please install Python 3.12+"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_status "Python version: $python_version"
    
    # Check for pip (try both pip and pip3)
    if command_exists pip; then
        print_status "pip found: $(pip --version 2>&1 | head -1)"
        PIP_CMD="pip"
    elif command_exists pip3; then
        print_status "pip3 found: $(pip3 --version 2>&1 | head -1)"
        PIP_CMD="pip3"
    else
        print_error "pip is not found. Please install pip:"
        print_info "On Ubuntu/Debian: sudo apt update && sudo apt install python3-pip"
        print_info "On macOS: brew install python3"
        print_info "On Windows: Download Python from python.org (includes pip)"
        print_info "Or install with: python3 -m ensurepip --upgrade"
        exit 1
    fi
    
    if ! file_exists "app.jac"; then
        print_error "app.jac not found. Run from project root."
        exit 1
    fi
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SCRIPT_PARENT_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Check for requirements file in docs/pure-jac/
    if ! file_exists "requirements_pure_jac.txt" && ! file_exists "$SCRIPT_DIR/requirements_pure_jac.txt"; then
        print_error "requirements_pure_jac.txt not found. Run from project root."
        exit 1
    fi
    
    print_status "All prerequisites met!"
    
    # Step 1: Virtual Environment
    print_header "Step 1: Virtual Environment Setup"
    
    if dir_exists "venv"; then
        print_warning "Virtual environment already exists"
        # Non-interactive: use existing venv by default
        print_info "Using existing virtual environment (pass --recreate to recreate)"
        if [[ "$1" == "--recreate" ]]; then
            print_info "Recreating virtual environment..."
            rm -rf venv
            python3 -m venv venv
        fi
    else
        print_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_status "Virtual environment activated"
    else
        print_error "Virtual environment activation failed"
        exit 1
    fi
    
    # Step 2: Install Dependencies
    print_header "Step 2: Installing JAC Dependencies"
    
    print_info "Upgrading pip..."
    $PIP_CMD install --upgrade pip
    
    print_info "Installing requirements..."
    if [ -f "requirements_pure_jac.txt" ]; then
        $PIP_CMD install -r requirements_pure_jac.txt
    else
        $PIP_CMD install -r "$SCRIPT_DIR/requirements_pure_jac.txt"
    fi
    
    print_status "All dependencies installed!"
    
    # Step 3: Verify JAC Installation
    print_header "Step 3: Verifying JAC Installation"
    
    if command_exists jac; then
        jac_ver=$(jac --version 2>&1 || echo "Version check failed")
        print_status "JAC Language installed: $jac_ver"
    else
        print_warning "JAC command not found - restart shell after setup"
    fi
    
    # Test JAC syntax
    print_info "Testing JAC syntax..."
    if jac build app.jac >/dev/null 2>&1; then
        print_status "JAC syntax validation: PASSED"
    else
        print_warning "JAC syntax validation: Check app.jac for errors"
    fi
    
    # Step 4: Environment Setup
    print_header "Step 4: Environment Configuration"
    
    # Look for .env file in project root or script directory
    ENV_FILE=""
    if [ -f ".env" ]; then
        ENV_FILE=".env"
    elif [ -f "$SCRIPT_DIR/.env_pure_jac" ]; then
        ENV_FILE="$SCRIPT_DIR/.env_pure_jac"
    fi
    
    if [ -n "$ENV_FILE" ]; then
        print_info "Loading environment variables from $ENV_FILE..."
        # Load OpenAI key for byLLM
        export $(grep -v '^#' "$ENV_FILE" | xargs)
        
        if [ -n "$OPENAI_API_KEY" ]; then
            print_status "OpenAI API key loaded"
        else
            print_warning "OpenAI API key not found in $ENV_FILE"
        fi
    else
        print_warning "Environment file not found"
    fi
    
    # Final Instructions
    print_header "🎉 Pure JAC Setup Complete!"
    
    echo -e "${GREEN}Your learning portal is ready!${NC}"
    echo ""
    echo "📋 What You Have:"
    echo "   ✅ JAC Language (v0.9.3+)"
    echo "   ✅ AI-powered byLLM integration"
    echo "   ✅ Native graph persistence (OSP)"
    echo "   ✅ Built-in HTTP server (jac serve)"
    echo "   ✅ React-style frontend components"
    echo ""
    echo "🚀 Start Your Application:"
    echo ""
    echo "1. Activate environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Start the learning portal:"
    echo "   jac serve app.jac"
    echo ""
    echo "3. Access your portal:"
    echo "   http://localhost:8000"
    echo ""
    echo "📊 Available API Endpoints:"
    echo "   GET  /functions/register_user"
    echo "   GET  /functions/get_lesson"
    echo "   GET  /functions/generate_quiz"
    echo "   POST /functions/submit_answer"
    echo "   GET  /functions/update_mastery"
    echo ""
    echo "💡 Architecture Benefits:"
    echo "   • No external database dependencies"
    echo "   • Native graph data persistence"
    echo "   • AI-powered content generation"
    echo "   • Single-language development"
    echo "   • Automatic API endpoint generation"
    echo ""
    echo "🆘 No Database Setup Required!"
    echo "   JAC handles all data persistence natively"
    echo ""
    echo -e "${GREEN}Happy Learning! 🎓${NC}"
}

main "$@"