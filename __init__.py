"""
Dev Audit Tool (dat) - v1.0.0

A comprehensive tool for auditing codebases, with cross-platform support,
file type filtering, and detailed reporting.
"""

__version__ = "1.0.0"
__author__ = "~JADIS | Justadudeinspace"
__description__ = "Dev Audit Tool - Comprehensive codebase auditing"

# Core functionality exports
from .core import (
    cat_file,
    cat_all,
    print_summary,
    should_process_file,
    get_file_color,
    format_size,
    is_text_file,
    get_file_mime_type,
    DOC_EXTENSIONS,
    CODE_EXTENSIONS,
    MEDIA_EXTENSIONS,
    STATS,
    TOP_LINES,
    TOP_SIZE
)

# Make main functions available at package level
__all__ = [
    'cat_file',
    'cat_all', 
    'print_summary',
    'should_process_file',
    'get_file_color',
    'format_size',
    'is_text_file',
    'get_file_mime_type',
    'DOC_EXTENSIONS',
    'CODE_EXTENSIONS',
    'MEDIA_EXTENSIONS',
    'STATS',
    'TOP_LINES',
    'TOP_SIZE'
]
