import subprocess
import sys
import threading
import queue
import time
from typing import List, Callable, Optional, Dict, Any

class ScanRunner:
    def __init__(self, nmap_path: str):
        self.nmap_path = nmap_path
        self.current_process: Optional[subprocess.Popen] = None
        self.is_running = False

    def run_scan_stream(
        self,
        args: List[str],
        on_line: Callable[[str], None],
        on_complete: Callable[[int, str], None]
    ):
        """Runs nmap asynchronously and streams stdout/stderr lines."""
        if self.is_running:
            raise RuntimeError("A scan is already in progress.")

        cmd = [self.nmap_path] + args
        self.is_running = True
        full_output = []

        def worker():
            try:
                # Windows startupinfo to avoid popping up a black console window
                startupinfo = None
                creationflags = 0
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    startupinfo=startupinfo,
                    creationflags=creationflags
                )

                for line in iter(self.current_process.stdout.readline, ''):
                    if not line and self.current_process.poll() is not None:
                        break
                    if line:
                        full_output.append(line)
                        on_line(line)

                self.current_process.stdout.close()
                returncode = self.current_process.wait()
            except Exception as e:
                err_msg = f"[Error executing Nmap: {str(e)}]\n"
                full_output.append(err_msg)
                on_line(err_msg)
                returncode = -1
            finally:
                self.is_running = False
                self.current_process = None
                on_complete(returncode, "".join(full_output))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def cancel(self):
        """Terminates active scan cleanly."""
        if self.current_process and self.is_running:
            try:
                self.current_process.terminate()
            except Exception:
                try:
                    self.current_process.kill()
                except Exception:
                    pass
            self.is_running = False
