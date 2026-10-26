import os
import re
from typing import List, Dict, Any, Optional

class NSEManager:
    """
    Parses and manages Nmap Scripting Engine (NSE) scripts from the installed Nmap directory.
    Reads script.db to categorize and provide instant search across 600+ NSE scripts.
    """
    def __init__(self, nmap_bin_path: Optional[str] = None):
        self.nmap_bin_path = nmap_bin_path
        self._scripts_cache: List[Dict[str, Any]] = []
        self._categories_cache: List[str] = []

    def get_scripts_dir(self) -> Optional[str]:
        if not self.nmap_bin_path:
            return None
        bin_dir = os.path.dirname(self.nmap_bin_path)
        candidates = [
            os.path.join(bin_dir, "scripts"),
            os.path.join(bin_dir, "..", "share", "nmap", "scripts"),
            "/usr/share/nmap/scripts",
            "/usr/local/share/nmap/scripts",
            r"C:\Program Files (x86)\Nmap\scripts",
            r"C:\Program Files\Nmap\scripts",
        ]
        for c in candidates:
            if os.path.exists(c) and os.path.isdir(c):
                return os.path.abspath(c)
        return None

    def load_scripts(self) -> List[Dict[str, Any]]:
        if self._scripts_cache:
            return self._scripts_cache

        scripts_dir = self.get_scripts_dir()
        if not scripts_dir:
            return []

        db_path = os.path.join(scripts_dir, "script.db")
        if not os.path.exists(db_path):
            return []

        entry_pattern = re.compile(r'Entry\s*\{\s*filename\s*=\s*"([^"]+)",\s*categories\s*=\s*\{([^}]+)\}\s*\}')
        scripts = []
        all_categories = set()

        try:
            with open(db_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            for match in entry_pattern.finditer(content):
                filename = match.group(1)
                name = filename[:-4] if filename.endswith(".nse") else filename
                raw_cats = match.group(2)
                cats = [c.strip().strip('"') for c in raw_cats.split(",") if c.strip().strip('"')]
                for c in cats:
                    all_categories.add(c)

                scripts.append({
                    "filename": filename,
                    "name": name,
                    "categories": cats,
                    "is_vuln": "vuln" in cats or "exploit" in cats,
                    "is_safe": "safe" in cats,
                    "is_default": "default" in cats,
                    "is_auth": "auth" in cats or "brute" in cats,
                })
        except Exception:
            pass

        self._scripts_cache = sorted(scripts, key=lambda s: s["name"])
        self._categories_cache = sorted(list(all_categories))
        return self._scripts_cache

    def get_categories(self) -> List[str]:
        if not self._categories_cache:
            self.load_scripts()
        return self._categories_cache
