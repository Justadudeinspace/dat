"""Enterprise Dev Audit Tool (DAT) - Security and Compliance Scanning."""
from __future__ import annotations

from importlib import metadata
from pathlib import Path
import sys
from typing import Optional

__all__ = [
    "__version__",
    "get_version",
    "repository_root",
    "ensure_python_version",
    "get_package_info",
]

try:
    __version__ = metadata.version("dat")
except metadata.PackageNotFoundError:  # pragma: no cover - fallback for local dev
    __version__ = "3.0.0-alpha.1"


def get_version() -> str:
    """Return the human friendly version string with additional metadata."""
    version = __version__
    
    # Add build information for enterprise tracking
    build_info = ""
    
    # Check if we're in a development environment
    try:
        from ._build_info import BUILD_TIMESTAMP, GIT_COMMIT
        if BUILD_TIMESTAMP and GIT_COMMIT:
            short_commit = GIT_COMMIT[:8]
            build_info = f" (build: {short_commit})"
    except ImportError:
        pass
    
    return f"{version}{build_info}"


def repository_root(start: Path | None = None, marker: str = ".git") -> Path:
    """
    Locate the repository root starting from *start* or the current working directory.
    
    Args:
        start: Starting directory for search (defaults to current directory)
        marker: Repository marker file/directory (default: ".git")
        
    Returns:
        Path to repository root
        
    Raises:
        FileNotFoundError: If no repository root can be found
    """
    current = Path(start or Path.cwd()).resolve()
    
    for parent in (current, *current.parents):
        if (parent / marker).exists():
            return parent
            
        # Support for other VCS markers
        if marker == ".git" and any((parent / vcs_marker).exists() 
                                   for vcs_marker in [".hg", ".svn", "_darcs"]):
            return parent
    
    # For enterprise environments, check for common project structure markers
    for parent in (current, *current.parents):
        if (parent / "pyproject.toml").exists() and "name" in (parent / "pyproject.toml").read_text():
            return parent
        if (parent / "setup.py").exists():
            return parent
        if (parent / "requirements.txt").exists() and (parent / "src").exists():
            return parent
    
    raise FileNotFoundError(f"No repository root found (looking for '{marker}' marker)")


def ensure_python_version(min_version: tuple[int, int] = (3, 8)) -> None:
    """
    Ensure the current Python version meets minimum requirements.
    
    Args:
        min_version: Minimum Python version as (major, minor) tuple
        
    Raises:
        SystemExit: If Python version is insufficient
    """
    if sys.version_info < min_version:
        min_version_str = ".".join(map(str, min_version))
        current_version = ".".join(map(str, sys.version_info[:2]))
        print(
            f"Error: DAT requires Python {min_version_str} or newer. "
            f"Current version: {current_version}",
            file=sys.stderr
        )
        sys.exit(1)


def get_package_info() -> dict[str, str]:
    """
    Get comprehensive package information for debugging and support.
    
    Returns:
        Dictionary containing package metadata
    """
    info = {
        "version": __version__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
    }
    
    # Try to get additional metadata
    try:
        dist = metadata.distribution("dat")
        info.update({
            "package_name": dist.metadata.get("Name", "dat"),
            "summary": dist.metadata.get("Summary", ""),
            "author": dist.metadata.get("Author", ""),
            "author_email": dist.metadata.get("Author-Email", ""),
            "license": dist.metadata.get("License", ""),
            "home_page": dist.metadata.get("Home-Page", ""),
        })
    except metadata.PackageNotFoundError:
        info["package_status"] = "development"
    
    # Add path information
    info["executable"] = sys.executable
    info["package_path"] = str(Path(__file__).parent.resolve())
    
    return info


def check_enterprise_features() -> dict[str, bool]:
    """
    Check availability of enterprise features.
    
    Returns:
        Dictionary indicating feature availability
    """
    features = {
        "encryption": False,
        "signing": False,
        "audit_logging": False,
        "lrc_integration": False,
        "rich_ui": False,
    }
    
    # Check for encryption support
    try:
        import cryptography
        features["encryption"] = True
    except ImportError:
        pass
    
    # Check for signing support
    try:
        import gnupg
        features["signing"] = True
    except ImportError:
        pass
    
    # Check for rich UI
    try:
        import rich
        features["rich_ui"] = True
    except ImportError:
        pass
    
    # Check for audit logging dependencies
    try:
        import json
        import getpass
        from datetime import datetime
        features["audit_logging"] = True
    except ImportError:
        pass
    
    # Check for LRC integration
    try:
        from .integration.lrc import load_integration_config
        features["lrc_integration"] = True
    except ImportError:
        pass
    
    return features


class DATConfig:
    """Global configuration for DAT enterprise features."""
    
    _instance: Optional[DATConfig] = None
    
    def __new__(cls) -> DATConfig:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
            
        self.enterprise_mode = False
        self.strict_validation = False
        self.audit_enabled = True
        self.signing_required = False
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_file_lines = 1000
        
        self._initialized = True
    
    def enable_enterprise_mode(self) -> None:
        """Enable enterprise features and strict validation."""
        self.enterprise_mode = True
        self.strict_validation = True
        self.audit_enabled = True
        self.signing_required = True
    
    def disable_enterprise_mode(self) -> None:
        """Disable enterprise features."""
        self.enterprise_mode = False
        self.strict_validation = False
        self.signing_required = False


# Initialize global configuration
config = DATConfig()

# Backwards compatible CLI access
try:
    from .cli import main
    __all__.append("main")
except ImportError as e:
    def main() -> int:  # type: ignore
        """Fallback main function if CLI cannot be imported."""
        print(f"Error: DAT CLI not available: {e}", file=sys.stderr)
        return 1


# Package initialization checks
def _initialize_package() -> None:
    """Perform package initialization checks."""
    ensure_python_version()
    
    # Log package initialization in enterprise mode
    if config.enterprise_mode:
        try:
            from .logging.audit import log_system_event
            log_system_event("package_initialized", {
                "version": __version__,
                "features": check_enterprise_features()
            })
        except ImportError:
            pass


# Run initialization when package is imported
_initialize_package()
