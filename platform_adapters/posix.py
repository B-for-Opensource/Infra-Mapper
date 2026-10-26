import os
import shutil
from typing import Optional, Dict, Any
from .base import BasePlatformAdapter

class LinuxAdapter(BasePlatformAdapter):
    def find_nmap(self) -> Optional[str]:
        for bin_name in ["nmap", "nmap.bin"]:
            found = shutil.which(bin_name)
            if found:
                return found
        for default_path in ["/usr/bin/nmap", "/usr/local/bin/nmap", "/bin/nmap"]:
            if os.path.exists(default_path):
                return default_path
        return None

    def check_privileges(self) -> Dict[str, Any]:
        is_root = False
        try:
            is_root = (os.geteuid() == 0)
        except AttributeError:
            pass

        return {
            "is_elevated": is_root,
            "elevation_label": "root" if is_root else "standard user",
            "npcap_detected": True, # Linux uses raw sockets directly via kernel/libpcap
            "platform": "linux"
        }

    def get_config_dir(self) -> str:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        config_path = os.path.join(base, "nmap-studio")
        os.makedirs(config_path, exist_ok=True)
        return config_path


class MacOSAdapter(BasePlatformAdapter):
    def find_nmap(self) -> Optional[str]:
        found = shutil.which("nmap")
        if found:
            return found
        for default_path in [
            "/opt/homebrew/bin/nmap",
            "/usr/local/bin/nmap",
            "/usr/bin/nmap"
        ]:
            if os.path.exists(default_path):
                return default_path
        return None

    def check_privileges(self) -> Dict[str, Any]:
        is_root = False
        try:
            is_root = (os.geteuid() == 0)
        except AttributeError:
            pass

        return {
            "is_elevated": is_root,
            "elevation_label": "root" if is_root else "standard user",
            "npcap_detected": True,
            "platform": "macos"
        }

    def get_config_dir(self) -> str:
        base = os.path.expanduser("~/Library/Application Support/NmapStudio")
        os.makedirs(base, exist_ok=True)
        return base
