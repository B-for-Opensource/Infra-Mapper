import sys
from .base import BasePlatformAdapter
from .windows import WindowsAdapter
from .posix import LinuxAdapter, MacOSAdapter

def get_platform_adapter() -> BasePlatformAdapter:
    if sys.platform == "win32":
        return WindowsAdapter()
    elif sys.platform == "darwin":
        return MacOSAdapter()
    else:
        return LinuxAdapter()

__all__ = ["get_platform_adapter", "BasePlatformAdapter"]
