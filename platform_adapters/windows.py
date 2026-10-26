import ctypes
import os
import shutil
from typing import Optional, Dict, Any
from .base import BasePlatformAdapter

class WindowsAdapter(BasePlatformAdapter):
    def find_nmap(self) -> Optional[str]:
        # 1. Check PATH
        path_bin = shutil.which("nmap") or shutil.which("nmap.exe")
        if path_bin and os.path.exists(path_bin):
            return path_bin

        # 2. Known Windows paths
        candidates = [
            r"C:\Program Files (x86)\Nmap\nmap.exe",
            r"C:\Program Files\Nmap\nmap.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Nmap\nmap.exe"),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return None

    def check_privileges(self) -> Dict[str, Any]:
        is_admin = False
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            pass

        # Check Npcap service / dll
        system32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "Npcap")
        npcap_present = os.path.exists(system32) or os.path.exists(r"C:\Windows\System32\wpcap.dll")

        return {
            "is_elevated": is_admin,
            "elevation_label": "Administrator" if is_admin else "Standard User",
            "npcap_detected": npcap_present,
            "platform": "windows"
        }

    def get_config_dir(self) -> str:
        app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
        config_path = os.path.join(app_data, "InfraMapper")
        os.makedirs(config_path, exist_ok=True)
        return config_path
