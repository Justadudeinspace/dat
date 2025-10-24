#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_debug() { echo -e "${CYAN}[DEBUG]${NC} $1"; }

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   DAT Installer v3.0.0-alpha.1               ║"
    echo "║         Enterprise Security Scanning Tool                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root user - this is not recommended"
        read -p "Continue anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Detect Python with version checking
detect_python() {
    local python_cmd=""
    
    # Try python3 first
    if command -v python3 >/dev/null 2>&1; then
        python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null || echo "unknown")
        if python3 -c "import sys; sys.exit(0) if sys.version_info >= (3, 8) else sys.exit(1)" 2>/dev/null; then
            python_cmd="python3"
            log_success "Found Python 3: $python_version"
        else
            log_error "Python 3.8+ required, found $python_version"
            return 1
        fi
    # Fall back to python
    elif command -v python >/dev/null 2>&1; then
        python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null || echo "unknown")
        if python -c "import sys; sys.exit(0) if sys.version_info >= (3, 8) else sys.exit(1)" 2>/dev/null; then
            python_cmd="python"
            log_success "Found Python 3: $python_version"
        else
            log_error "Python 3.8+ required, found $python_version"
            return 1
        fi
    else
        log_error "Python 3.8+ is not installed"
        log_info "Download from: https://python.org/downloads/"
        return 1
    fi
    
    echo "$python_cmd"
}

# Install Python dependencies
install_python_deps() {
    local python_cmd="$1"
    log_info "Installing Python dependencies..."
    
    # Upgrade pip first
    log_info "Upgrading pip..."
    $python_cmd -m pip install --upgrade pip --quiet
    
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing from requirements.txt..."
        if $python_cmd -m pip install -r requirements.txt --quiet; then
            log_success "Python dependencies installed from requirements.txt"
        else
            log_error "Failed to install from requirements.txt"
            return 1
        fi
    else
        log_warning "requirements.txt not found, installing core dependencies..."
        local core_deps=(
            "rich>=13.0.0"
            "cryptography>=41.0.0"
            "reportlab>=4.0.0"
            "python-magic>=0.4.27"
            "Pillow>=10.0.0"
            "colorama>=0.4.6"
        )
        
        if $python_cmd -m pip install "${core_deps[@]}" --quiet; then
            log_success "Core Python dependencies installed"
        else
            log_error "Failed to install core dependencies"
            return 1
        fi
    fi
}

# Detect platform and install system dependencies
install_system_deps() {
    local os=$(uname -s | tr '[:upper:]' '[:lower:]')
    local platform_specific=0
    
    log_info "Detected platform: $os"
    
    case "$os" in
        linux*)
            install_linux_deps
            platform_specific=1
            ;;
        darwin*)
            install_macos_deps
            platform_specific=1
            ;;
        mingw*|cygwin*|msys*)
            install_windows_deps
            platform_specific=1
            ;;
        *)
            log_warning "Unsupported platform: $os"
            log_info "You may need to install dependencies manually"
            ;;
    esac
    
    return $platform_specific
}

# Linux distribution detection and package installation
install_linux_deps() {
    local distro=""
    local install_cmd=""
    local font_pkg=""
    local magic_pkg=""
    
    # Detect distribution
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        distro=$ID
    fi
    
    # Check for WSL
    if grep -qi "microsoft" /proc/version 2>/dev/null || [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
        log_info "Detected WSL2 (Windows Subsystem for Linux)"
    fi
    
    case "$distro" in
        ubuntu|debian|linuxmint)
            log_info "Detected Ubuntu/Debian-based system"
            install_cmd="sudo apt-get install -y"
            font_pkg="fonts-dejavu-core fontconfig"
            magic_pkg="libmagic1 libmagic-dev file"
            sudo apt-get update -y --quiet
            ;;
        fedora|rhel|centos)
            log_info "Detected Fedora/RHEL-based system"
            install_cmd="sudo dnf install -y"
            font_pkg="dejavu-sans-mono-fonts fontconfig"
            magic_pkg="file-devel file-libs"
            ;;
        arch|manjaro)
            log_info "Detected Arch Linux-based system"
            install_cmd="sudo pacman -S --noconfirm"
            font_pkg="ttf-dejavu fontconfig"
            magic_pkg="file"
            ;;
        opensuse*)
            log_info "Detected openSUSE-based system"
            install_cmd="sudo zypper install -y"
            font_pkg="dejavu-fonts fontconfig"
            magic_pkg="file file-devel"
            ;;
        *)
            log_warning "Unknown Linux distribution: $distro"
            show_manual_instructions
            return 1
            ;;
    esac
    
    # Install packages
    log_info "Installing system dependencies..."
    if $install_cmd $font_pkg $magic_pkg 2>/dev/null; then
        log_success "System dependencies installed"
        
        # Update font cache
        if command -v fc-cache >/dev/null 2>&1; then
            sudo fc-cache -fv > /dev/null 2>&1 && log_success "Font cache updated"
        fi
        return 0
    else
        log_error "Failed to install system dependencies"
        show_manual_instructions
        return 1
    fi
}

# macOS dependency installation
install_macos_deps() {
    log_info "Detected macOS"
    
    if command -v brew >/dev/null 2>&1; then
        log_info "Using Homebrew package manager"
        
        # Install libmagic
        if brew install libmagic --quiet; then
            log_success "libmagic installed via Homebrew"
        else
            log_error "Failed to install libmagic"
            return 1
        fi
        
        # Install fonts (optional on macOS as system fonts may suffice)
        log_info "Installing DejaVu fonts..."
        brew tap homebrew/cask-fonts --quiet
        if brew install --cask font-dejavu-sans-mono --quiet; then
            log_success "DejaVu fonts installed"
        else
            log_warning "Font installation failed, but DAT should work with system fonts"
        fi
        return 0
    else
        log_warning "Homebrew not found"
        log_info "Install Homebrew from: https://brew.sh"
        log_info "Or install manually:"
        log_info "  - Download fonts: https://dejavu-fonts.github.io/"
        log_info "  - Install libmagic: brew install libmagic"
        return 1
    fi
}

# Windows dependency installation
install_windows_deps() {
    log_info "Detected Windows (Git Bash / MSYS2 / Cygwin)"
    
    # Install Windows-compatible python-magic
    log_info "Installing Windows-compatible file detection..."
    if $PYTHON_CMD -m pip install python-magic-bin --quiet; then
        log_success "Windows file detection installed"
    else
        log_error "Failed to install Windows file detection"
        return 1
    fi
    
    log_info "For optimal PDF generation, install DejaVu fonts:"
    log_info "  Download: https://dejavu-fonts.github.io/Download.html"
    log_info "  Or use Chocolatey: choco install dejavufonts"
    return 0
}

# Show manual installation instructions
show_manual_instructions() {
    log_info "Manual installation instructions:"
    log_info "Ubuntu/Debian: sudo apt-get install fonts-dejavu-core fontconfig libmagic1 libmagic-dev"
    log_info "Fedora/RHEL:   sudo dnf install dejavu-sans-mono-fonts fontconfig file-devel file-libs"
    log_info "Arch Linux:    sudo pacman -S ttf-dejavu fontconfig file"
    log_info "macOS:         brew install libmagic && brew install --cask font-dejavu-sans-mono"
}

# Verify Python dependencies
verify_python_deps() {
    local python_cmd="$1"
    log_info "Verifying Python dependencies..."
    
    $python_cmd -c "
import sys
import importlib.util

# Required packages with minimum versions
required_packages = {
    'rich': '13.0.0',
    'cryptography': '41.0.0', 
    'reportlab': '4.0.0',
    'python-magic': '0.4.27',
    'Pillow': '10.0.0',
    'colorama': '0.4.6'
}

print('🔍 Checking Python dependencies...')
all_ok = True

for package, min_version in required_packages.items():
    try:
        # Try to import
        spec = importlib.util.find_spec(package.split('-')[-1])
        if spec is None:
            print(f'❌ {package}: NOT INSTALLED')
            all_ok = False
            continue
            
        # Import successfully
        module = __import__(package.split('-')[-1])
        
        # Try to get version
        try:
            version = getattr(module, '__version__', 'unknown')
            status = '✅' if version != 'unknown' else '⚠️'
            print(f'{status} {package}: {version}')
            
            # Check version if we can
            if version != 'unknown' and version < min_version:
                print(f'   ⚠️  Version {version} < {min_version}, consider upgrading')
                
        except AttributeError:
            print(f'⚠️  {package}: imported (version unknown)')
            
    except ImportError as e:
        print(f'❌ {package}: IMPORT FAILED - {e}')
        all_ok = False

# Test functionality
print('\n🧪 Testing functionality...')
try:
    import magic
    # Test basic functionality
    magic.from_buffer(b'test')
    print('✅ python-magic: functional')
except Exception as e:
    print(f'❌ python-magic: {e}')

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    print('✅ reportlab: PDF functionality OK')
except Exception as e:
    print(f'❌ reportlab: {e}')

try:
    import cryptography
    print('✅ cryptography: encryption ready')
except Exception as e:
    print(f'❌ cryptography: {e}')

try:
    from rich.console import Console
    print('✅ rich: terminal output ready')
except Exception as e:
    print(f'❌ rich: {e}')

if not all_ok:
    print('\n💥 Some dependencies failed verification')
    sys.exit(1)
else:
    print('\n🎉 All Python dependencies verified!')
"
}

# Verify system dependencies
verify_system_deps() {
    log_info "Verifying system dependencies..."
    
    # Check file command (libmagic)
    if command -v file >/dev/null 2>&1; then
        if echo "test" | file - >/dev/null 2>&1; then
            log_success "file command (libmagic): functional"
        else
            log_warning "file command available but has issues"
        fi
    else
        log_warning "file command (libmagic) not available"
    fi
    
    # Check fonts
    if command -v fc-list >/dev/null 2>&1; then
        if fc-list | grep -i "dejavu" >/dev/null 2>&1; then
            log_success "DejaVu fonts: installed"
        else
            log_warning "DejaVu fonts not found via fontconfig"
        fi
    else
        log_info "fontconfig not available, skipping font verification"
    fi
}

# Make dat executable and test
setup_dat() {
    local python_cmd="$1"
    
    # Make executable if dat file exists
    if [[ -f "dat" ]]; then
        log_info "Making dat script executable..."
        chmod +x dat
        log_success "dat script is now executable"
    else
        log_warning "dat script not found in current directory"
        return 1
    fi
    
    # Test basic functionality
    log_info "Testing DAT installation..."
    if $python_cmd dat --version >/dev/null 2>&1; then
        local version=$($python_cmd dat --version 2>/dev/null || echo "unknown")
        log_success "DAT functional - version $version"
        return 0
    else
        log_error "DAT functionality test failed"
        return 1
    fi
}

# Main installation function
main() {
    print_banner
    check_root
    
    log_info "Starting DAT installation..."
    
    # Detect Python
    PYTHON_CMD=$(detect_python) || exit 1
    
    # Install Python dependencies
    install_python_deps "$PYTHON_CMD" || exit 1
    
    # Install system dependencies
    if install_system_deps; then
        log_success "Platform-specific dependencies handled"
    else
        log_warning "Platform-specific dependencies may need manual installation"
    fi
    
    # Verify installations
    verify_python_deps "$PYTHON_CMD" || exit 1
    verify_system_deps
    
    # Setup DAT
    setup_dat "$PYTHON_CMD" || exit 1
    
    # Final success message
    echo
    log_success "🎉 DAT installation completed successfully!"
    echo
    log_info "🚀 Quick Start:"
    log_info "  dat                          # Scan current directory"
    log_info "  dat --deep                   # Deep scan (includes binaries)"
    log_info "  dat --pdf report.pdf         # Generate PDF report"
    log_info "  dat -f src                   # Scan only src folder"
    log_info "  dat -s main.py               # Scan only main.py file"
    log_info "  dat --help                   # Show all options"
    echo
    log_info "📖 Documentation: https://github.com/your-org/dat"
    log_info "🐛 Issues: https://github.com/your-org/dat/issues"
    echo
}

# Run main function
main "$@"
