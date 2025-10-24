# Troubleshooting

## Quick Reference

### 🚨 Critical Issues
- **Command Not Found** - Installation or permissions issue
- **Missing Dependencies** - Python or system libraries missing
- **Permission Denied** - File access or execution permissions
- **Scan Failures** - Configuration or environment problems

### ⚠️ Performance Issues  
- **Slow Scanning** - Large repositories or resource constraints
- **Memory Exhaustion** - Insufficient RAM for large scans
- **Timeout Errors** - Network or process timeouts

### 🔧 Configuration Issues
- **Invalid Configuration** - Malformed config files
- **Environment Problems** - PATH or environment variable issues
- **Platform-Specific** - OS-specific dependencies or limitations

---

## Installation & Setup Issues

### ❌ Command Not Found

**Symptoms**: `dat: command not found` or `./dat: No such file or directory`

**Solutions**:
```bash
# Make executable if in repository
chmod +x dat

# Run with Python directly
python3 dat.py

# Or use module execution
python3 -m dat.cli

# Check if in PATH
which dat || echo "Not in PATH"

# Add to PATH temporarily
export PATH="$PATH:$(pwd)"
```

### Complete Fix:

```bash
# Re-run installation
./install_deps.sh

# Or manual installation
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
chmod +x dat

# Verify installation
./dat --version
```

## ❌ Missing Dependencies

Symptoms: Import errors, missing module warnings, or functionality failures

### Solutions:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Force reinstall if corrupted
pip install --force-reinstall -r requirements.txt

# Install with development dependencies
pip install -e .[dev]

# Check specific dependencies
python -c "import magic, cryptography, reportlab, rich; print('Dependencies OK')"
```

### Platform-Specific Dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libmagic1 libmagic-dev

# Fedora/RHEL  
sudo dnf install python3-devel file-devel file-libs

# macOS
brew install libmagic python3

# Windows
pip install python-magic-bin

# Termux (Android)
pkg install python libmagic file
```

## ⚠️ Bootstrap Fails

Symptoms: Installation script fails with errors or warnings

### Solutions:

```bash
# Ensure basic dependencies
sudo apt install python3-venv libmagic-dev  # Ubuntu/Debian
sudo dnf install python3-virtualenv file-devel  # Fedora/RHEL

# Manual virtual environment setup
python3 -m venv .venv --without-pip
source .venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
pip install -r requirements.txt

# Alternative: Use system Python
pip3 install --user -r requirements.txt
```

### Debug Installation:

```bash
# Run with debug output
bash -x ./install_deps.sh

# Check Python version
python3 --version  # Requires 3.8+

# Verify virtual environment
which python3
python3 -c "import sys; print(sys.prefix)"
```

---

# Scanning & Performance Issues

## 🪲 No Output or Empty Audit

Symptoms: Scan completes but shows no files or empty results

### Solutions:

```bash
# Check file filters - maybe everything is filtered out
dat -a -c  # Include all files and code files

# Disable all filters
dat --no-safe --deep --all

# Check specific directory
dat /path/to/source --verbose

# Test with known files
echo "test" > test-file.txt
dat test-file.txt
```

### Debug File Detection:

```bash
# Enable verbose output
dat . --verbose --debug

# Check what's being scanned
dat . --dry-run --list-files

# Test file type detection
file --mime-type some-file.py
python -c "import magic; print(magic.from_file('some-file.py'))"
```

## 🐌 Slow Scanning Performance

Symptoms: Scan takes excessively long time, high CPU/memory usage

### Solutions:

```bash
# Use fast mode for large repositories
dat . --fast

# Limit scan scope
dat . --max-depth 2 --ignore "**/node_modules/**" --ignore "**/vendor/**"

# Adjust resource limits
dat . --parallel-threads 2 --batch-size 500 --max-memory 1024

# Use safe mode with adjusted limits
dat . --safe --max-size 5242880 --max-lines 2000
```

### Performance Optimization:

```bash
# Profile performance
dat . --profile --report performance.json

# Monitor resource usage
/usr/bin/time -v dat . --fast 2> performance.log

# Check system resources
free -h  # Memory
nproc     # CPU cores
df -h .   # Disk space
```

## 💥 Memory Exhaustion

Symptoms: Process killed, out of memory errors, system slowdown

### Solutions:

```bash
# Reduce memory usage
dat . --batch-size 100 --max-memory 512

# Skip large files
dat . --max-size 1048576  # 1MB limit

# Use streaming mode
dat . --jsonl stream.jsonl

# Process in chunks
find . -name "*.py" -type f | xargs -n 100 dat --files-from -
```

### Memory Management:

```bash
# Check available memory
grep MemTotal /proc/meminfo

# Monitor during scan
while true; do ps aux | grep dat | grep -v grep; sleep 5; done

# Use ulimit for memory constraints
ulimit -v 1048576  # 1GB virtual memory limit
dat . --fast
```

---

# Configuration & Environment Issues

## ⚙️ Invalid Configuration

Symptoms: Configuration errors, unexpected behavior, warning messages

### Solutions:

```bash
# Validate configuration
dat --validate-config

# Show effective configuration
dat --show-config

# Reset to defaults
rm ~/.config/dat/config.ini
rm ~/.datconfig

# Debug configuration loading
DAT_DEBUG=1 dat . --verbose
```

### Configuration Debugging:

```bash
# Check config file syntax
python3 -m json.tool ~/.config/dat/config.ini 2>/dev/null || echo "Invalid INI"
python3 -c "import yaml; yaml.safe_load(open('.datconfig'))" 2>/dev/null || echo "Invalid YAML"

# Test environment variables
env | grep DAT_
env | grep LRC_

# Check configuration precedence
dat . --setting top_n=5 --show-config | grep top_n
```

## 🔐 GPG Signing Issues

Symptoms: Signing failures, missing signature files, verification errors

### Solutions:

```bash
# Check GPG installation
which gpg
gpg --version

# List available keys
gpg --list-secret-keys

# Generate key if missing
gpg --full-generate-key

# Test signing independently
echo "test" | gpg --clearsign

# Disable signing if not needed
dat . --no-sign --report audit.json
```

### GPG Troubleshooting:

```bash
# Set specific key
export DAT_SIGNING_KEY=$(gpg --list-secret-keys --with-colons | grep ^sec | cut -d: -f5 | head -1)

# Fix keyring permissions
chmod 700 ~/.gnupg
chmod 600 ~/.gnupg/*

# Verify signatures manually
gpg --verify audit.json.asc audit.json
```

## 🌐 Network & Connectivity Issues

Symptoms: Timeout errors, download failures, remote resource issues

### Solutions:

```bash
# Disable network-dependent features
dat . --no-external-checks --offline

# Increase timeout limits
dat . --timeout 300 --download-timeout 60

# Use local resources only
dat . --local-rules --no-update-check
```

---

# Platform-Specific Issues

## 🪟 Windows Issues

Symptoms: Path problems, permission errors, compatibility issues

### Solutions:

```bash
# Use Windows-compatible dependencies
pip install python-magic-bin

# Fix path separators
dat C:/Users/username/project --report C:/reports/scan.json

# Run as administrator if needed
# Right-click Command Prompt -> Run as administrator

# Check Windows Defender exclusions
# Add DAT installation directory to exclusions
```

## 🍎 macOS Issues

Symptoms: Library path issues, font problems, permission prompts

### Solutions:

```bash
# Fix library paths on macOS
export DYLD_LIBRARY_PATH="/usr/local/lib:$DYLD_LIBRARY_PATH"

# Install fonts for PDF generation
brew install --cask font-dejavu-sans-mono

# Handle macOS security prompts
# System Preferences -> Security & Privacy -> Allow DAT
```

## 📱 Termux (Android) Issues

Symptoms: Storage permissions, limited resources, environment constraints

### Solutions:

```bash
# Grant storage permissions
termux-setup-storage

# Use device-optimized settings
dat . --fast --max-memory 256 --batch-size 50

# Check available storage
df -h /data/data/com.termux/files/home

# Install required packages
pkg update && pkg install python libmagic file
```

## 🐧 Linux Distribution Issues

### Different distributions may require specific packages:

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libmagic1 libmagic-dev file fonts-dejavu-core

# Fedora/RHEL
sudo dnf install python3-devel file-devel file-libs dejavu-sans-mono-fonts

# Arch Linux
sudo pacman -S python file ttf-dejavu

# openSUSE
sudo zypper install python3-devel file file-devel dejavu-fonts
```

---

# Advanced Debugging

## 🔍 Comprehensive Debug Mode

### Enable full debugging:

```bash
# Maximum verbosity
DAT_DEBUG=1 dat . --verbose --debug --log-level debug

# Log to file
dat . --verbose 2> debug.log

# Profile specific operations
python -m cProfile -o profile.stats dat.py . --safe
```

## 🧪 Diagnostic Script

### Run comprehensive diagnostics:

```bash
#!/bin/bash
echo "=== DAT Diagnostic Check ==="

# Basic checks
echo "Python: $(python3 --version 2>&1)"
echo "DAT: $(./dat --version 2>&1)"
echo "Virtualenv: $(which python3)"

# Dependency check
python3 -c "
import sys
deps = ['magic', 'cryptography', 'reportlab', 'rich', 'colorama']
for dep in deps:
    try:
        __import__(dep)
        print(f'✅ {dep}')
    except ImportError as e:
        print(f'❌ {dep}: {e}')
"

# File detection test
echo "test" > diagnostic-test.txt
./dat diagnostic-test.txt --json - | jq '.scan.files[]' && echo "✅ File scan working"

# Configuration test
./dat --validate-config && echo "✅ Config valid" || echo "❌ Config invalid"

rm diagnostic-test.txt
echo "=== Diagnostic Complete ==="
```

## 📊 Performance Analysis

### Analyze performance bottlenecks:

```bash
# Time different operations
time dat . --fast --json /dev/null

# Memory profiling
pip install memory_profiler
python -m memory_profiler dat.py . --safe

# I/O monitoring
strace -e trace=file dat . 2> strace.log
```

---

## Common Error Messages & Solutions

### ModuleNotFoundError: No module named 'magic'

```bash
pip install python-magic
# On Windows:
pip install python-magic-bin
```

### gpg: signing failed: No secret key

```bash
gpg --list-secret-keys
export DAT_SIGNING_KEY=YOUR_KEY_ID
# Or disable signing:
dat . --no-sign
```

### PermissionError: [Errno 13] Permission denied

```bash
# Fix script permissions
chmod +x dat install_deps.sh

# Use virtual environment
python3 -m venv venv
source venv/bin/activate

# Check file permissions
ls -la dat
```

### OSError: [Errno 28] No space left on device

```bash
# Check disk space
df -h .

# Clean temporary files
rm -rf /tmp/dat-*
dat . --keep-temp-files=false

# Use different output directory
dat . --output /different/partition/report.json
```

### ValueError: Invalid configuration key

```bash
# Validate configuration
dat --validate-config

# Remove invalid config
mv ~/.config/dat/config.ini ~/.config/dat/config.ini.backup

# Check config syntax
python3 -c "import configparser; configparser.ConfigParser().read('~/.config/dat/config.ini')"
```

---

# Getting Help

## 📚 Resources

· Documentation: docs/ directory for detailed guides
· GitHub Issues: Report bugs and request features
· Community Forum: Get help from other users
· Debug Logs: Enable with DAT_DEBUG=1 for detailed logs

## 🐛 Reporting Issues

### When reporting issues, include:

```bash
# System information
./dat --version
python3 --version
uname -a

# Debug information
DAT_DEBUG=1 dat . --verbose 2> debug.log

# Configuration (if relevant)
cat ~/.config/dat/config.ini
```

## 🆘 Emergency Recovery

```bash
# Complete reset
rm -rf ~/.config/dat
rm -rf ~/.cache/dat
rm -f ~/.datconfig

# Fresh installation
git clean -fdx
./install_deps.sh

# Test basic functionality
./dat . --safe --report test.json
```

---

For additional help, check the complete documentation in the docs/ directory or create an issue on GitHub with detailed error information and debug logs.
