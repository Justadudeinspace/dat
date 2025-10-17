#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────────────────────
#  Dev Audit Tool (dat) - Bootstrap Script v1.0.0
#  Author: ~JADIS | Justadudeinspace  
#  Updated by: GPT-5, Deepseek AI, & Gemini 2.0 Flash
#
#  Purpose:
#    • Auto-initialize project environment with cross-platform support
#    • Create & activate a virtual environment
#    • Install dependencies from requirements.txt  
#    • Create global shim (dat) if missing
#    • Handle Windows, Linux, macOS, and Android/Termux environments
# ───────────────────────────────────────────────────────────────────────────────

set -euo pipefail
IFS=$'\n\t'

# Script configuration
SCRIPT_NAME="dat"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$REPO_ROOT/.venv"
REQUIREMENTS="$REPO_ROOT/requirements.txt"
MAIN_SCRIPT="$REPO_ROOT/dat.py"
PYTHON_BIN="python3"

# Platform detection
PLATFORM="$(uname -s)"
ARCHITECTURE="$(uname -m)"
IS_WINDOWS=false
IS_TERMUX=false

# Detect platform
case "$PLATFORM" in
    Linux*)
        if [[ -n "${ANDROID_ROOT:-}" || -n "${TERMUX_VERSION:-}" ]]; then
            PLATFORM="Android"
            IS_TERMUX=true
        elif grep -q "microsoft" /proc/version 2>/dev/null || [[ "$(uname -r)" == *"microsoft"* ]]; then
            PLATFORM="WSL"
        else
            PLATFORM="Linux"
        fi
        ;;
    Darwin*) PLATFORM="macOS" ;;
    CYGWIN*|MINGW*|MSYS*) 
        PLATFORM="Windows" 
        IS_WINDOWS=true
        ;;
    *) PLATFORM="Unknown" ;;
esac

# Color support detection
SUPPORTS_COLOR=false
if [[ -t 1 ]] && [[ -z "${NO_COLOR:-}" ]]; then
    case "$PLATFORM" in
        Windows|CYGWIN*|MINGW*|MSYS*)
            if [[ "$TERM" == "xterm"* ]] || [[ "$TERM" == "cygwin" ]]; then
                SUPPORTS_COLOR=true
            fi
            ;;
        *)
            SUPPORTS_COLOR=true
            ;;
    esac
fi

# Color definitions
if [[ "$SUPPORTS_COLOR" == true ]]; then
    RESET="\033[0m"
    HEADER_COLOR="\033[95m"
    SUCCESS_COLOR="\033[92m"
    WARNING_COLOR="\033[93m"
    ERROR_COLOR="\033[91m"
    INFO_COLOR="\033[96m"
    CODE_COLOR="\033[94m"
    
    # Windows color adjustments
    if [[ "$IS_WINDOWS" == true ]]; then
        HEADER_COLOR="\033[35m"
        INFO_COLOR="\033[36m"
        SUCCESS_COLOR="\033[32m"
    fi
else
    RESET=""
    HEADER_COLOR=""
    SUCCESS_COLOR=""
    WARNING_COLOR=""
    ERROR_COLOR=""
    INFO_COLOR=""
    CODE_COLOR=""
fi

# Print functions
print_header() {
    echo -e "${HEADER_COLOR}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                   Dev Audit Tool - Bootstrap                   ║"  
    echo "║                         dat v1.0.0                             ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${RESET}"
}

print_success() {
    echo -e "${SUCCESS_COLOR}✅  $1${RESET}"
}

print_warning() {
    echo -e "${WARNING_COLOR}⚠️  $1${RESET}"
}

print_error() {
    echo -e "${ERROR_COLOR}❌  $1${RESET}"
}

print_info() {
    echo -e "${INFO_COLOR}💡  $1${RESET}"
}

print_code() {
    echo -e "${CODE_COLOR}$1${RESET}"
}

print_step() {
    echo -e "${INFO_COLOR}🔧  $1${RESET}"
}

# Platform-specific path functions
get_install_path() {
    case "$PLATFORM" in
        Linux|WSL|macOS)
            echo "$HOME/.local/bin/$SCRIPT_NAME"
            ;;
        Windows)
            echo "$HOME/AppData/Local/Programs/Python/Scripts/$SCRIPT_NAME"
            ;;
        Android)
            echo "/data/data/com.termux/files/usr/bin/$SCRIPT_NAME"
            ;;
        *)
            echo "$HOME/.local/bin/$SCRIPT_NAME"
            ;;
    esac
}

# Main bootstrap function
bootstrap() {
    print_header
    
    echo -e "${INFO_COLOR}📂  Repository: $REPO_ROOT${RESET}"
    echo -e "${INFO_COLOR}🖥️   Platform: $PLATFORM ($ARCHITECTURE)${RESET}"
    echo -e "${INFO_COLOR}🐍  Python: $(which $PYTHON_BIN)${RESET}"
    echo "────────────────────────────────────────────────────────────────"

    # --- Python availability check ---
    print_step "Checking Python installation..."
    if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
        print_error "Python3 not found. Please install Python 3.8+ first."
        
        case "$PLATFORM" in
            macOS)
                echo "Install with: brew install python3"
                ;;
            Linux)
                echo "Install with: sudo apt-get install python3 python3-pip"
                ;;
            Windows)
                echo "Download from: https://www.python.org/downloads/"
                ;;
            Android)
                echo "Install with: pkg install python"
                ;;
        esac
        exit 1
    fi
    print_success "Python found: $($PYTHON_BIN --version 2>&1)"

    # --- Virtual environment setup ---
    print_step "Setting up virtual environment..."
    if [[ ! -d "$VENV_DIR" ]]; then
        print_info "Creating virtual environment..."
        if ! "$PYTHON_BIN" -m venv "$VENV_DIR"; then
            print_error "Failed to create virtual environment"
            print_info "Trying with virtualenv fallback..."
            if command -v virtualenv >/dev/null 2>&1; then
                virtualenv "$VENV_DIR"
            else
                print_error "Please install venv or virtualenv"
                exit 1
            fi
        fi
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi

    # --- Platform-specific activation ---
    print_step "Activating virtual environment..."
    if [[ "$IS_WINDOWS" == true ]]; then
        VENV_ACTIVATE="$VENV_DIR/Scripts/activate"
    else
        VENV_ACTIVATE="$VENV_DIR/bin/activate"
    fi

    if [[ ! -f "$VENV_ACTIVATE" ]]; then
        print_error "Virtual environment activation script not found"
        exit 1
    fi

    # shellcheck source=/dev/null
    source "$VENV_ACTIVATE"
    print_success "Virtual environment activated"

    # --- Install dependencies ---
    print_step "Installing dependencies..."
    if [[ -f "$REQUIREMENTS" ]]; then
        print_info "Upgrading pip..."
        pip install --upgrade pip >/dev/null
        
        print_info "Installing from requirements.txt..."
        if pip install -r "$REQUIREMENTS"; then
            print_success "Dependencies installed successfully"
        else
            print_warning "Some dependencies failed to install"
        fi
    else
        print_warning "No requirements.txt found — installing core dependencies..."
        pip install python-magic >/dev/null
        print_success "Core dependencies installed"
    fi

    # --- Create executable shim ---
    print_step "Creating executable shim..."
    if [[ ! -f "$MAIN_SCRIPT" ]]; then
        print_error "Main script $MAIN_SCRIPT not found"
        exit 1
    fi

    LOCAL_SHIM="$REPO_ROOT/$SCRIPT_NAME"
    if [[ ! -f "$LOCAL_SHIM" ]]; then
        print_info "Creating local shim: $LOCAL_SHIM"
        
        cat > "$LOCAL_SHIM" << 'EOF'
#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────────────────────
#  Dev Audit Tool (dat) - Shim v1.0.0
#  Author: ~JADIS | Justadudeinspace
#  Purpose: Auto-activates virtual environment and runs main Python script
# ───────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PY_SCRIPT="$SCRIPT_DIR/dat.py"

# Platform detection
IS_WINDOWS=false
if [[ "$(uname -s)" == "CYGWIN"* ]] || [[ "$(uname -s)" == "MINGW"* ]] || [[ "$(uname -s)" == "MSYS"* ]]; then
    IS_WINDOWS=true
fi

# Virtual environment activation
if [[ ! -d "$VENV_DIR" ]]; then
    echo "❌  Virtual environment not found. Run ./bootstrap.sh first."
    exit 1
fi

if [[ "$IS_WINDOWS" == true ]]; then
    source "$VENV_DIR/Scripts/activate"
else
    source "$VENV_DIR/bin/activate"
fi

# Main script execution
if [[ ! -f "$PY_SCRIPT" ]]; then
    echo "❌  dat.py not found in repository root."
    exit 1
fi

python "$PY_SCRIPT" "$@"
EOF
        
        chmod +x "$LOCAL_SHIM"
        print_success "Local shim created and made executable"
    else
        print_success "Local shim already exists"
    fi

    # --- Global installation check ---
    print_step "Checking global installation..."
    GLOBAL_INSTALL_PATH="$(get_install_path)"
    
    if ! command -v "$SCRIPT_NAME" >/dev/null 2>&1 && [[ ! -f "$GLOBAL_INSTALL_PATH" ]]; then
        print_info "Global command '$SCRIPT_NAME' not found in PATH"
        print_info "Install path: $GLOBAL_INSTALL_PATH"
        
        read -p "Would you like to create a global symlink? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mkdir -p "$(dirname "$GLOBAL_INSTALL_PATH")"
            if ln -sf "$LOCAL_SHIM" "$GLOBAL_INSTALL_PATH" 2>/dev/null; then
                print_success "Global symlink created: $GLOBAL_INSTALL_PATH"
                print_warning "Ensure $(dirname "$GLOBAL_INSTALL_PATH") is in your PATH"
            else
                print_warning "Failed to create global symlink - using local shim"
            fi
        fi
    else
        print_success "Global command available"
    fi

    # --- Post-setup summary ---
    echo "────────────────────────────────────────────────────────────────"
    print_success "Dev Audit Tool environment ready!"
    echo ""
    echo -e "${INFO_COLOR}Usage Examples:${RESET}"
    print_code "  ./dat                        # Audit current directory"
    print_code "  ./dat /path/to/project       # Audit specific directory" 
    print_code "  ./dat -c -f                  # Code files in current folder only"
    print_code "  ./dat -e py,js,html          # Filter by specific extensions"
    print_code "  ./dat -o audit.txt           # Output to file"
    print_code "  ./dat -a                     # Include hidden files"
    print_code "  ./dat --version              # Show version info"
    echo ""
    echo -e "${INFO_COLOR}Configuration:${RESET}"
    print_code "  Edit ~/.datconfig to customize file types and settings"
    echo ""
    echo -e "${INFO_COLOR}Testing:${RESET}"
    print_code "  python -m pytest dat/tests/  # Run test suite"
    print_code "  ./dat --help                 # Full help documentation"
    echo "────────────────────────────────────────────────────────────────"
    echo -e "${HEADER_COLOR}🌌  ~JADIS | 2025 — Dev Audit Tool initialized.${RESET}"
    echo ""
}

# Help function
show_help() {
    echo -e "${HEADER_COLOR}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                   dat Bootstrap Help                           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${RESET}"
    echo "Usage: ./bootstrap.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo "  -v, --version   Show version information"
    echo "  --no-color      Disable colored output"
    echo ""
    echo "Description:"
    echo "  Initializes the Dev Audit Tool environment by:"
    echo "  • Creating a Python virtual environment"
    echo "  • Installing required dependencies"
    echo "  • Creating executable shims"
    echo "  • Setting up global command access"
    echo ""
    echo "Platform Support:"
    echo "  • Linux (including WSL)"
    echo "  • macOS"
    echo "  • Windows (Git Bash, Cygwin, WSL)"
    echo "  • Android (Termux)"
    echo ""
    echo -e "${INFO_COLOR}After running: Use './dat' or 'dat' if globally installed${RESET}"
}

# Version function
show_version() {
    echo -e "${HEADER_COLOR}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║             Dev Audit Tool - Bootstrap v1.0.0                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${RESET}"
    echo "Platform: $PLATFORM $ARCHITECTURE"
    echo "Python: $(which $PYTHON_BIN)"
    echo "Repository: $REPO_ROOT"
    echo ""
    echo "Author: ~JADIS | Justadudeinspace"
    echo "Updated by: GPT-5, Deepseek AI, & Gemini 2.0 Flash"
}

# Argument parsing
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -v|--version)
        show_version
        exit 0
        ;;
    --no-color)
        SUPPORTS_COLOR=false
        RESET=""; HEADER_COLOR=""; SUCCESS_COLOR=""; WARNING_COLOR=""
        ERROR_COLOR=""; INFO_COLOR=""; CODE_COLOR=""
        bootstrap
        ;;
    *)
        bootstrap
        ;;
esac
