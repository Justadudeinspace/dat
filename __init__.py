"""
Dev Audit Tool (dat) - v2.0.0-Stable

A comprehensive tool for auditing codebases with cross-platform support,
file type filtering, PDF output, and detailed reporting.
"""

__version__ = "2.0.0-Stable"
__author__ = "~JADIS | Justadudeinspace"
__contributors__ = ["GPT-5", "Deepseek AI", "Gemini 2.0 Flash"]
__description__ = "Dev Audit Tool - Comprehensive codebase auditing with PDF support"

# Core functionality exports
from .core import (
    # File processing
    cat_file,
    cat_all,
    print_single_file,
    process_single_file,
    
    # File type detection
    should_process_file,
    is_text_file,
    get_file_mime_type,
    get_file_color,
    
    # Utilities
    format_size,
    print_summary,
    resolve_target_path,
    should_ignore,
    
    # Configuration
    DOC_EXTENSIONS,
    CODE_EXTENSIONS, 
    MEDIA_EXTENSIONS,
    DEFAULT_IGNORES,
    
    # Statistics
    STATS,
    TOP_LINES,
    TOP_SIZE,
    
    # Platform info
    IS_WINDOWS,
    IS_TERMUX,
    supports_color
)

# PDF functionality exports
from .pdf_export import (
    export_to_pdf,
    md_to_pdf,
    sanitize,
    REPORTLAB_OK
)

# Bootstrap and installation
from .bootstrap import (
    bootstrap,
    get_install_path,
    INSTALL_PATH,
    add_windows_to_path
)

# Configuration management
from .config import (
    get_config_value,
    CONFIG,
    CONFIG_PATH
)

# Make main functions available at package level
__all__ = [
    # Core file processing
    'cat_file',
    'cat_all', 
    'print_single_file',
    'process_single_file',
    
    # File type handling
    'should_process_file',
    'is_text_file',
    'get_file_mime_type',
    'get_file_color',
    
    # Utilities
    'format_size',
    'print_summary',
    'resolve_target_path', 
    'should_ignore',
    
    # Configuration
    'DOC_EXTENSIONS',
    'CODE_EXTENSIONS',
    'MEDIA_EXTENSIONS',
    'DEFAULT_IGNORES',
    'get_config_value',
    'CONFIG',
    'CONFIG_PATH',
    
    # Statistics
    'STATS',
    'TOP_LINES', 
    'TOP_SIZE',
    
    # PDF functionality
    'export_to_pdf',
    'md_to_pdf',
    'sanitize',
    'REPORTLAB_OK',
    
    # Bootstrap
    'bootstrap',
    'get_install_path',
    'INSTALL_PATH',
    'add_windows_to_path',
    
    # Platform info
    'IS_WINDOWS',
    'IS_TERMUX',
    'supports_color'
]

# Package metadata
__package_name__ = "dat"
__license__ = "MIT"
__url__ = "https://github.com/justadudeinspace/dat"

# Compatibility imports for backward compatibility
try:
    from .cli import main
    __all__.append('main')
except ImportError:
    # Fallback for direct script execution
    pass

def get_version():
    """Return the complete version information."""
    return f"{__version__} (Python {'.'.join(map(str, __import__('sys').version_info[:3]))})"

def show_info():
    """Display package information."""
    info = f"""
Dev Audit Tool (dat)
Version: {__version__}
Author: {__author__}
Contributors: {', '.join(__contributors__)}
Description: {__description__}

Platform: {__import__('platform').system()} {__import__('platform').release()}
Python: {__import__('sys').version}

Features:
  • Cross-platform support (Windows, Linux, macOS, Android/Termux)
  • Smart file type detection
  • PDF report generation
  • Configurable file filters
  • Single file and directory auditing
  • Colorized terminal output
  • Extension resolution for files
"""
    print(info)
