# Installation Guide

`dat` supports Linux, macOS, Windows, WSL2, and Termux (Android) with enterprise-grade security features.

---

## System Requirements

### Python Requirements
- **Python**: 3.8 or newer
- **pip**: Latest version recommended
- **Virtual Environment**: Recommended for isolation

### Platform Support
| Platform | Status | Notes |
|----------|---------|-------|
| **Linux** | ✅ Full Support | Ubuntu, Debian, Fedora, RHEL, Arch, openSUSE |
| **macOS** | ✅ Full Support | 10.15+ with Homebrew or native Python |
| **Windows** | ✅ Full Support | Git Bash, WSL2, Cygwin, MSYS2 |
| **Android** | ✅ Full Support | Termux environment |
| **WSL2** | ✅ Full Support | Ubuntu, Debian distributions |

### Dependencies
- **libmagic**: File type detection (auto-installed)
- **GPG**: Artifact signing (optional)
- **Fonts**: DejaVu Sans Mono for PDF reports (auto-installed)

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Justadudeinspace/dat.git
cd dat

# Or download and extract
wget https://github.com/Justadudeinspace/dat/archive/refs/heads/main.zip
unzip main.zip && cd dat-main
```

### Alternative: Download Release

```bash
# Download latest release
wget https://github.com/Justadudeinspace/dat/releases/latest/download/dat-v3.0.0-alpha.1.zip
unzip dat-v3.0.0-alpha.1.zip && cd dat
```

---

## Step 2: Automated Installation (Recommended)

### Full Automated Setup

```bash
# Run the comprehensive installer
chmod +x install_deps.sh
./install_deps.sh
```

### What the installer does:

· ✅ Detects your platform and architecture
· ✅ Creates Python virtual environment
· ✅ Installs all Python dependencies
· ✅ Handles system dependencies (libmagic, fonts)
· ✅ Creates executable shims
· ✅ Sets up global command access
· ✅ Verifies installation integrity

## Platform-Specific Notes

### Linux

```bash
# Ubuntu/Debian
sudo apt-get update
./install_deps.sh

# Fedora/RHEL
sudo dnf groupinstall "Development Tools"
./install_deps.sh

# Arch Linux
sudo pacman -S base-devel
./install_deps.sh
```

### macOS

```bash
# With Homebrew (recommended)
brew install python3 libmagic
./install_deps.sh

# Without Homebrew
python3 -m ensurepip
./install_deps.sh
```

### Windows

```bash
# Git Bash / WSL2
./install_deps.sh

# If Python not found, install from:
# https://python.org/downloads/
```

### Android (Termux)

```bash
pkg update && pkg upgrade
pkg install python libmagic
./install_deps.sh
```

---

## Step 3: Manual Installation (Advanced)

### Python Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate environment
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -e .[dev]
```

## System Dependencies

### Linux

```bash
# Ubuntu/Debian
sudo apt-get install libmagic1 libmagic-dev file fonts-dejavu-core

# Fedora/RHEL
sudo dnf install file-devel file-libs dejavu-sans-mono-fonts

# Arch Linux
sudo pacman -S file ttf-dejavu

# openSUSE
sudo zypper install file file-devel dejavu-fonts
```

### macOS

```bash
# With Homebrew
brew install libmagic
brew install --cask font-dejavu-sans-mono

# Without Homebrew (manual font installation)
# Download from: https://dejavu-fonts.github.io/
```

### Windows

```bash
# Install python-magic-bin for Windows compatibility
pip install python-magic-bin

# Manual font installation recommended
# Download DejaVu fonts from: https://dejavu-fonts.github.io/
```

### Android (Termux)

```bash
pkg install libmagic file
# Fonts are handled automatically
```

---

## Step 4: Verification

### Basic Verification

```bash
# Check installation
./dat --version

# Expected output:
# DAT v3.0.0-alpha.1
# Platform: [Your Platform]
```

### Comprehensive Verification

```bash
# Test core functionality
./dat --help

# Test scanning
./dat . --safe --report test-scan.json

# Verify dependencies
python -c "
import sys
print(f'Python: {sys.version}')
try:
    import magic; print('✅ python-magic: OK')
    import cryptography; print('✅ cryptography: OK') 
    import reportlab; print('✅ reportlab: OK')
    import rich; print('✅ rich: OK')
except ImportError as e:
    print(f'❌ {e}')
"
```

## Platform-Specific Verification

### Linux/macOS

```bash
# Verify system dependencies
which gpg && echo "✅ GPG available" || echo "⚠️ GPG not installed"
file --version && echo "✅ file command available" || echo "⚠️ file command missing"
```

### Windows

```bash
# Verify Windows compatibility
python -c "import python_magic_bin; print('✅ Windows file detection: OK')"
```

### Termux

```bash
# Verify Termux setup
pkg list-installed | grep -E "(python|libmagic)" && echo "✅ Dependencies installed"
```

---

## Step 5: Global Installation (Optional)

### Create Global Symlink

```bash
# Make dat available system-wide
sudo ln -sf "$(pwd)/dat" /usr/local/bin/dat

# Or for user-only installation
mkdir -p ~/.local/bin
ln -sf "$(pwd)/dat" ~/.local/bin/dat
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Verify Global Access

```bash
# Should work from any directory
cd /tmp
dat --version
```

---

## Enterprise Installation

### Docker Installation

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN chmod +x dat install_deps.sh

ENTRYPOINT ["./dat"]
```

```bash
# Build and run
docker build -t dat .
docker run -v $(pwd):/scan dat /scan --deep --json report.json
```

### CI/CD Pipeline Integration

```yaml
# GitHub Actions
- name: Install DAT
  run: |
    git clone https://github.com/Justadudeinspace/dat.git
    cd dat
    ./install_deps.sh

- name: Security Scan
  run: |
    cd dat
    ./dat . --safe --json security-report.json
```

### System Package Installation

```bash
# Build package (developers)
python -m build
pip install dist/dat-3.0.0a1-py3-none-any.whl
```

---

# Troubleshooting

## Common Installation Issues

### Python Not Found

```bash
# Check Python installation
python3 --version || python --version

# Install Python if missing
# Ubuntu/Debian: sudo apt-get install python3 python3-pip
# macOS: brew install python3
# Windows: https://python.org/downloads/
```

### Permission Denied

```bash
# Fix script permissions
chmod +x dat install_deps.sh bootstrap.sh

# Use virtual environment to avoid system installs
python3 -m venv venv
source venv/bin/activate
./install_deps.sh
```

### Missing Dependencies

```bash
# Manual dependency installation
pip install --force-reinstall -r requirements.txt

# System libraries (Linux)
sudo apt-get install libmagic1 libmagic-dev  # Ubuntu/Debian
sudo dnf install file-devel file-libs        # Fedora/RHEL
```

### GPG Signing Issues

```bash
# Install GPG if missing
sudo apt-get install gnupg    # Ubuntu/Debian
brew install gnupg            # macOS
choco install gnupg           # Windows

# Or disable signing
dat . --no-sign --report audit.json
```

## Platform-Specific Issues

### Windows Font Problems

```bash
# Install fonts manually or use fallback
dat . --pdf report.pdf --pdf-theme light
```

### macOS Library Path

```bash
# Fix library paths on macOS
export DYLD_LIBRARY_PATH="/usr/local/lib:$DYLD_LIBRARY_PATH"
```

### Termux Storage

```bash
# Grant storage permissions
termux-setup-storage

# Install in home directory
cd ~/storage/shared
git clone https://github.com/Justadudeinspace/dat.git
```

---

## Post-Installation Setup

### Configuration (Optional)

```bash
# Create configuration directory
mkdir -p ~/.config/dat

# Basic configuration
cat > ~/.config/dat/config.ini << 'EOF'
[Settings]
default_mode = safe
color = auto
top_n = 10

[Security]
audit_logging = true
EOF
```

### Test Complete Workflow

```bash
# Run comprehensive test
dat . --deep --pdf test-report.pdf --json test-scan.json --sign --verbose

# Verify outputs
ls -la *.pdf *.json *.asc && echo "✅ Installation successful"
```

### Update DAT

```bash
# Update to latest version
cd dat
git pull origin main
./install_deps.sh --upgrade

# Or reinstall completely
rm -rf .venv
./install_deps.sh
```

---

## Support

### Getting Help

· Documentation: docs/ directory
· Issues: GitHub Issues page
· Troubleshooting: docs/TROUBLESHOOTING.md

### Verification

```bash
# Final verification script
#!/bin/bash
echo "=== DAT Installation Verification ==="
./dat --version
python -c "import sys, dat; print(f'Python: {sys.version}'); print(f'DAT: {dat.__version__}')"
./dat . --safe --report install-test.json && echo "✅ Scan successful" || echo "❌ Scan failed"
```

### Expected Output:

```
=== DAT Installation Verification ===
DAT v3.0.0-alpha.1
Python: 3.11.0 (main, Oct 24 2023, 18:15:12) [GCC 11.3.0]
DAT: 3.0.0-alpha.1
✅ Scan successful
```

---

DAT is now installed and ready for enterprise security scanning and compliance auditing.

