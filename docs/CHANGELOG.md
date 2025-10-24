# Changelog

All notable changes to DAT (Dev Audit Tool) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0-alpha.1] - 2024-05-25

### 🚀 Added
- **Enterprise Architecture**: Adopted modular `src/dat` layout with dedicated packages:
  - `scanner/` - High-performance file scanning engine
  - `rules/` - Policy evaluation and violation detection
  - `integration/` - Enterprise feature integration
  - `pdf/` - Professional report generation
  - `logging/` - Encrypted audit system
  - `cli/` - Command-line interface

- **Security Features**:
  - `--from-lrc` - LRC (License and Regulatory Compliance) metadata integration
  - `--sign` - GPG artifact signing for report integrity
  - Encrypted audit logging to `~/.config/dat/auditlog.jsonl`
  - Path traversal protection and file validation

- **Scanning Modes**:
  - `--safe/--no-safe` - Safe scanning mode with configurable limits
  - `--deep` - Deep scan including binary files and no size limits
  - `--max-lines` and `--max-size` - Configurable resource limits

- **Reporting System**:
  - `--report` - Unified report generation with format auto-detection
  - Atomic file writes for all output formats
  - Standardized JSON, Markdown, and PDF outputs
  - Digital fingerprints for report verification

- **Enterprise Integration**:
  - LRC metadata merging from `~/.config/lrc/dat_integration.json`
  - Automatic `.lrc-audit.json` emission with scan results
  - Compliance framework support (SOC2, GDPR, HIPAA)
  - Custom rule engine with severity levels

- **CLI Enhancements**:
  - `--diff` - Compare current scan with previous JSON report
  - `--verbose` - Detailed progress and debug information
  - `--interactive` - Confirmation prompts for sensitive operations
  - File selection options: `-f/--folder`, `-s/--single-file`, `-a/--all`

- **Cross-Platform Improvements**:
  - Enhanced Windows support with python-magic-bin
  - macOS optimization with Homebrew integration
  - Linux distribution-specific package management
  - Termux (Android) compatibility

### 🔧 Changed
- **Architecture**: Refactored from monolithic to modular enterprise architecture
- **Performance**: Async scanning engine for improved large repository performance
- **Output**: Standardized report formats with consistent metadata
- **Security**: Enhanced file validation and security checks
- **Documentation**: Comprehensive guides and enterprise documentation

### 🐛 Fixed
- File encoding detection for international character sets
- Binary file handling in safe mode
- Path resolution across different platforms
- Permission handling for various file systems
- Memory optimization for large file processing

### 🛡️ Security
- Implemented Fernet encryption for audit logs
- Added GPG signature verification for LRC includes
- Enhanced path traversal protection
- File extension validation for security
- Secure temporary file handling

### 📚 Documentation
- Enterprise usage guides and examples
- API documentation for extension development
- Security best practices
- Compliance framework integration guides
- Troubleshooting and debugging guides

### 🔨 Deprecated
- Legacy command-line arguments (replaced with unified `--report`)
- Old configuration file format (migrated to INI-style)
- Basic scanning mode (superseded by safe/deep modes)

### 🗑️ Removed
- Unmaintained legacy modules
- Deprecated output formats
- Platform-specific hacks (replaced with cross-platform solutions)

### ⚠️ Known Issues
- Large repository scans may require tuning of memory limits
- Some edge cases in complex symbolic link structures
- PDF generation font fallback on some Windows systems

---

## [2.1.0] - 2024-03-15

### Added
- Basic file scanning capabilities
- Simple rule engine for TODO and merge conflict detection
- JSON output format
- Cross-platform file detection

### Changed
- Improved error handling
- Better file type detection

### Fixed
- Encoding issues with international text
- Performance improvements for large directories

---

## [2.0.0] - 2024-01-10

### Added
- Initial public release
- Core file scanning functionality
- Basic command-line interface
- Simple text output format

### Changed
- Project renamed to DAT (Dev Audit Tool)

---

## [1.0.0] - 2023-11-01

### Added
- Initial development version
- Basic file system walking
- Simple size and line counting
- Experimental rule system

## Migration Guides

### Upgrading from 2.x to 3.0
- Update configuration files to new INI format
- Replace legacy arguments with new `--report` system
- Review new security features and enable as needed
- Test LRC integration if using compliance features

### Upgrading from 1.x to 2.0
- Update command-line usage to new argument structure
- Migrate custom rules to new rule engine format
- Review output format changes for integration scripts

## Support Timeline

- **Version 3.x**: Active development and support
- **Version 2.x**: Security fixes only (until 2024-12-31)
- **Version 1.x**: End of life

---

*DAT follows semantic versioning. Major versions may introduce breaking changes.*
