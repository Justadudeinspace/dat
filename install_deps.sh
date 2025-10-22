#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

echo "=== DAT Cross-Platform Installer ==="

# Determine Python command - prefer python3 but fall back to python if it's python3
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
    echo "[+] Using python3"
elif command -v python >/dev/null 2>&1; then
    # Check if 'python' is actually python3
    if python -c "import sys; print(sys.version_info.major)" 2>/dev/null | grep -q "3"; then
        PYTHON_CMD="python"
        echo "[+] Using python (version 3)"
    else
        echo "[-] Python 3 is required but not found as 'python3' or 'python'"
        exit 1
    fi
else
    echo "[-] Python 3 is not installed"
    exit 1
fi

echo "[+] Installing Python dependencies from requirements.txt..."

# Check if requirements.txt exists
if [[ -f "requirements.txt" ]]; then
    echo "[+] Installing packages from requirements.txt..."
    $PYTHON_CMD -m pip install -r requirements.txt
else
    echo "[-] requirements.txt not found!"
    echo "[+] Installing dependencies directly..."
    $PYTHON_CMD -m pip install python-magic configparser reportlab colorama Pillow PyPDF2
fi

# --- Detect OS / environment ---
os="$(uname -s | tr '[:upper:]' '[:lower:]')"
pkg_manager=""
font_installed=0
magic_installed=0

# Termux first (Android)
if [[ -n "${PREFIX:-}" && "$PREFIX" == "/data/data/com.termux/files/usr" ]]; then
    echo "[+] Detected Termux on Android"
    pkg_manager="pkg"
    pkg update -y
    pkg install -y fontconfig fonts-dejavu python3 libmagic
    fc-cache -fv > /dev/null 2>&1 || true
    font_installed=1
    magic_installed=1
fi

# Linux (including WSL2)
if [[ "$os" == "linux" ]]; then
    if grep -qi microsoft /proc/version 2>/dev/null || [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
        echo "[+] Detected WSL2 (Windows Subsystem for Linux)"
    else
        echo "[+] Detected Linux"
    fi
    
    if command -v apt-get >/dev/null 2>&1; then
        pkg_manager="apt-get"
        echo "[+] Using apt-get package manager"
        sudo apt-get update -y
        sudo apt-get install -y fonts-dejavu-core fontconfig libmagic1 libmagic-dev
        sudo fc-cache -fv > /dev/null 2>&1 || true
        font_installed=1
        magic_installed=1
        
    elif command -v dnf >/dev/null 2>&1; then
        pkg_manager="dnf"
        echo "[+] Using dnf package manager"
        sudo dnf install -y dejavu-sans-mono-fonts fontconfig file-devel file-libs
        sudo fc-cache -fv > /dev/null 2>&1 || true
        font_installed=1
        magic_installed=1
        
    elif command -v yum >/dev/null 2>&1; then
        pkg_manager="yum"
        echo "[+] Using yum package manager"
        sudo yum install -y dejavu-sans-mono-fonts fontconfig file-devel file-libs
        sudo fc-cache -fv > /dev/null 2>&1 || true
        font_installed=1
        magic_installed=1
        
    elif command -v pacman >/dev/null 2>&1; then
        pkg_manager="pacman"
        echo "[+] Using pacman package manager"
        sudo pacman -Sy --noconfirm ttf-dejavu fontconfig file
        sudo fc-cache -fv > /dev/null 2>&1 || true
        font_installed=1
        magic_installed=1
        
    elif command -v zypper >/dev/null 2>&1; then
        pkg_manager="zypper"
        echo "[+] Using zypper package manager"
        sudo zypper install -y dejavu-fonts fontconfig file file-devel
        sudo fc-cache -fv > /dev/null 2>&1 || true
        font_installed=1
        magic_installed=1
        
    else
        echo "[-] Unknown Linux distro — please install dependencies manually."
        echo "    Ubuntu/Debian: sudo apt-get install fonts-dejavu-core fontconfig libmagic1 libmagic-dev"
        echo "    Fedora/RHEL: sudo dnf install dejavu-sans-mono-fonts fontconfig file-devel file-libs"
        echo "    Arch: sudo pacman -S ttf-dejavu fontconfig file"
    fi
fi

# macOS
if [[ "$os" == "darwin" ]]; then
    echo "[+] Detected macOS"
    if command -v brew >/dev/null 2>&1; then
        echo "[+] Using Homebrew package manager"
        brew tap homebrew/cask-fonts
        brew install --cask font-dejavu-sans-mono
        brew install libmagic
        # On macOS, fonts are automatically available after installation
        font_installed=1
        magic_installed=1
    else
        echo "[-] Homebrew not found. Please install it from https://brew.sh and rerun."
        echo "    Alternatively, install dependencies manually:"
        echo "    Download fonts: https://dejavu-fonts.github.io/Download.html"
        echo "    Install libmagic: brew install libmagic"
    fi
fi

# Windows (native, not WSL)
if [[ "$os" =~ ^mingw || "$os" =~ ^cygwin || "$os" == "msys" ]]; then
    echo "[+] Detected Windows (Git Bash / MSYS2 / Cygwin)"
    echo "[*] Installing python-magic-bin for Windows compatibility..."
    $PYTHON_CMD -m pip install python-magic-bin
    echo "[*] Please install DejaVu fonts manually:"
    echo "    Download from: https://dejavu-fonts.github.io/Download.html"
    echo "    Or install via Chocolatey: choco install dejavufonts"
    magic_installed=1
fi

# Final checks and verification
echo "[+] Verifying installation..."

# Check Python dependencies using direct import method
echo "[+] Verifying Python dependencies..."
$PYTHON_CMD -c "
import sys

# Define required packages with their import names and pip names
required_packages = [
    ('python-magic', 'magic'),
    ('configparser', 'configparser'), 
    ('reportlab', 'reportlab'),
    ('colorama', 'colorama'),
    ('Pillow', 'PIL'),
    ('PyPDF2', 'PyPDF2')
]

print('Checking required packages:')
all_ok = True

for pip_name, import_name in required_packages:
    try:
        # Try to import the package
        __import__(import_name)
        # Try to get version if possible
        try:
            if import_name == 'magic':
                import magic
                version = 'unknown (import ok)'
            elif import_name == 'configparser':
                import configparser
                version = 'unknown (import ok)'
            elif import_name == 'reportlab':
                from reportlab import __version__
                version = __version__
            elif import_name == 'colorama':
                import colorama
                version = colorama.__version__
            elif import_name == 'PIL':
                from PIL import __version__
                version = __version__
            elif import_name == 'PyPDF2':
                import PyPDF2
                version = PyPDF2.__version__
            else:
                version = 'unknown (import ok)'
            print(f'[✓] {pip_name} - version {version}')
        except (AttributeError, ImportError):
            print(f'[✓] {pip_name} - imported successfully')
    except ImportError as e:
        print(f'[-] {pip_name} - failed to import: {e}')
        all_ok = False

# Test specific functionality
print('\nTesting functionality:')
try:
    import magic
    # Test basic magic functionality
    try:
        magic.from_buffer(b'test')
        print('[✓] python-magic functionality verified')
    except Exception as e:
        print(f'[!] python-magic import ok but functionality issue: {e}')
except ImportError as e:
    print('[-] python-magic not available')

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    print('[✓] reportlab PDF functionality verified')
except ImportError as e:
    print('[-] reportlab PDF functionality not available')

try:
    import configparser
    print('[✓] configparser verified')
except ImportError as e:
    print('[-] configparser not available')

try:
    import colorama
    colorama.init()
    print('[✓] colorama verified')
except ImportError as e:
    print('[-] colorama not available')

try:
    from PIL import Image
    print('[✓] Pillow (PIL) verified')
except ImportError as e:
    print('[-] Pillow not available')

try:
    import PyPDF2
    print('[✓] PyPDF2 verified')
except ImportError as e:
    print('[-] PyPDF2 not available')

if not all_ok:
    print('\n[!] Some dependencies are missing. Please run:')
    print('    pip install -r requirements.txt')
    sys.exit(1)
else:
    print('\n[✓] All Python dependencies verified successfully!')
"

# Check if fontconfig is available and test DejaVu font
echo "[+] Verifying font installation..."
if command -v fc-list >/dev/null 2>&1; then
    if fc-list | grep -i "dejavu" >/dev/null 2>&1; then
        echo "[✓] DejaVu fonts verified as installed"
    else
        echo "[-] DejaVu fonts not found via fontconfig. They may need manual installation."
    fi
else
    echo "[*] fontconfig not available, skipping font verification"
fi

# Check libmagic installation
echo "[+] Verifying libmagic installation..."
if command -v file >/dev/null 2>&1; then
    echo "[✓] file command (libmagic) available"
    # Test file command
    if echo "test" | file - >/dev/null 2>&1; then
        echo "[✓] libmagic functionality verified"
    else
        echo "[!] file command available but has issues"
    fi
else
    echo "[-] file command (libmagic) not available"
fi

# Test the dat script directly
echo "[+] Testing dat script..."
if [[ -f "dat" ]]; then
    if $PYTHON_CMD dat --version >/dev/null 2>&1; then
        echo "[✓] dat script is functional"
        echo "[+] Version info:"
        $PYTHON_CMD dat --version
    else
        echo "[-] dat script has issues"
    fi
else
    echo "[-] dat script not found in current directory"
fi

echo ""
echo "=== Installation Summary ==="
if [[ $font_installed -eq 1 ]]; then
    echo "[✓] Font installation attempted for your platform"
else
    echo "[-] Could not detect OS automatically for font installation"
fi

if [[ $magic_installed -eq 1 ]]; then
    echo "[✓] libmagic installation attempted for your platform"
else
    echo "[-] Could not install libmagic automatically"
fi

echo "[✓] Python dependencies installed from requirements.txt"
echo "[*] Next steps:"
echo "    1. Run: chmod +x dat"
echo "    2. Test: dat --version"
echo "    3. Use: dat -sp file.py (to print single file)"
echo "    4. Use: dat -i .pyc __pycache__ -o output.pdf (ignore patterns + PDF output)"
echo ""
echo "[✓] DAT installation completed!"
