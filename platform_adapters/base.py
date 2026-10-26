import abc
import os
import shutil
import platform
from typing import Optional, Dict, Any

class BasePlatformAdapter(abc.ABC):
    @abc.abstractmethod
    def find_nmap(self) -> Optional[str]:
        """Locate the nmap executable on the system."""
        pass

    @abc.abstractmethod
    def check_privileges(self) -> Dict[str, Any]:
        """Check if running with elevated privileges (admin/root) and driver support."""
        pass

    @abc.abstractmethod
    def get_config_dir(self) -> str:
        """Return app configuration directory."""
        pass
