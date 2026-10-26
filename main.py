import os
import sys
import json
import tempfile
import threading
import asyncio
import psutil
import webview
from typing import Dict, Any, List

from platform_adapters import get_platform_adapter
from core.runner import ScanRunner
from core.flags import CATEGORIZED_FLAGS, PROFILES
from core.parser import parse_nmap_xml
from core.nse_manager import NSEManager
from engines.turbo_engine import TurboPortScanner
from engines.subnet_engine import SubnetSweeper

class StudioApi:
    def __init__(self):
        self.adapter = None
        self.nmap_bin = None
        self.runner = None
        self.nse_manager = None
        self._nmap_version_cache = None
        self.turbo_scanner = None
        self.subnet_sweeper = None

    def _ensure_backend(self):
        if self.adapter is None:
            self.adapter = get_platform_adapter()
            self.nmap_bin = self.adapter.find_nmap()
            if self.nmap_bin:
                self.runner = ScanRunner(self.nmap_bin)
                self.nse_manager = NSEManager(self.nmap_bin)

    def _get_active_window(self):
        if webview.windows and len(webview.windows) > 0:
            return webview.windows[0]
        return None

    def on_loaded(self) -> Dict[str, Any]:
        self._ensure_backend()
        return {"status": "ok"}

    def get_system_info(self) -> Dict[str, Any]:
        self._ensure_backend()
        platform_info = self.adapter.check_privileges() if self.adapter else {
            "is_elevated": False,
            "elevation_label": "Unknown",
            "npcap_detected": False,
            "platform": sys.platform
        }

        if self._nmap_version_cache is None and self.nmap_bin and os.path.exists(self.nmap_bin):
            try:
                import subprocess
                out = subprocess.check_output([self.nmap_bin, "--version"], text=True, stderr=subprocess.STDOUT)
                lines = out.strip().splitlines()
                if lines:
                    self._nmap_version_cache = lines[0].replace("Nmap version ", "").split(" ")[0]
            except Exception:
                self._nmap_version_cache = "Installed"

        nmap_info = {
            "path": self.nmap_bin,
            "found": bool(self.nmap_bin),
            "version": self._nmap_version_cache or "Unknown"
        }

        return {
            "platform_info": platform_info,
            "nmap_info": nmap_info,
            "flag_catalog": CATEGORIZED_FLAGS,
            "profiles": PROFILES
        }

    def get_nse_data(self) -> Dict[str, Any]:
        """Returns all 600+ indexed NSE scripts with categories for the NSE Script Browser tab."""
        self._ensure_backend()
        if self.nse_manager:
            scripts = self.nse_manager.load_scripts()
            categories = self.nse_manager.get_categories()
            return {"scripts": scripts, "categories": categories, "count": len(scripts)}
        return {"scripts": [], "categories": [], "count": 0}

    def get_system_resources(self) -> Dict[str, Any]:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent

        nmap_ram_mb = 0.0
        is_scanning = False

        if self.runner and self.runner.is_running and self.runner.current_process:
            is_scanning = True
            try:
                proc = psutil.Process(self.runner.current_process.pid)
                nmap_ram_mb = proc.memory_info().rss / (1024 * 1024)
            except Exception:
                pass

        return {
            "cpu": cpu,
            "ram_percent": ram,
            "nmap_ram_mb": round(nmap_ram_mb, 1),
            "is_scanning": is_scanning
        }

    def start_scan(self, target: str, flags: List[str], engine_mode: str = "nmap") -> Dict[str, Any]:
        """
        Unified Multi-Engine Scan:
          - 'nmap': Standard precision Nmap
          - 'turbo': RustScan-style fast port sweep -> piped to Nmap deep scan
          - 'subnet': Angry IP Scanner style multi-threaded host discovery
        """
        self._ensure_backend()
        if not self.runner or not self.nmap_bin:
            return {"success": False, "error": "Nmap binary not found on this system."}

        def stream_line(line: str):
            win = self._get_active_window()
            if win:
                escaped = json.dumps(line)
                win.evaluate_js(f"window.onStreamLine({escaped});")

        def complete_scan(returncode: int, parsed_data: dict):
            win = self._get_active_window()
            if win:
                js_parsed = json.dumps(parsed_data)
                win.evaluate_js(f"window.onScanComplete({returncode}, {js_parsed});")

        # ---------------- MODE B: TURBO (RustScan-Style) ----------------
        if engine_mode == "turbo":
            def turbo_worker():
                stream_line(f"[🚀 Turbo Engine] Initializing high-speed port sweep on {target}...\n")
                self.turbo_scanner = TurboPortScanner(target=target, port_range=range(1, 10001), concurrency=600, timeout=1.2)
                
                def on_port_open(port: int):
                    stream_line(f"  [⚡ Open Port Discovered] {port}/tcp\n")

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    open_ports = loop.run_until_complete(
                        self.turbo_scanner.scan_ports_async(on_progress=stream_line, on_open=on_port_open)
                    )
                finally:
                    loop.close()

                if not open_ports:
                    stream_line("\n[-] No open ports discovered by Turbo Engine.\n")
                    complete_scan(0, {"summary": {"total_hosts": 1, "open_ports": 0}, "hosts": [{"ip": target, "state": "up", "ports": []}]})
                    return

                # Auto-Pipe discovered ports into Nmap deep scan
                ports_arg = ",".join(map(str, open_ports))
                stream_line(f"\n[+] Piping {len(open_ports)} discovered port(s) into Nmap deep inspection (-sV -sC)...\n")
                
                temp_xml = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
                temp_xml_path = temp_xml.name
                temp_xml.close()

                pipe_args = ["-p", ports_arg, "-sV", "-T4", "-oX", temp_xml_path, target]

                def on_nmap_done(code: int, full_output: str):
                    parsed_data = {}
                    if os.path.exists(temp_xml_path):
                        try:
                            with open(temp_xml_path, "r", encoding="utf-8", errors="replace") as f:
                                parsed_data = parse_nmap_xml(f.read())
                        except Exception as e:
                            parsed_data = {"error": str(e)}
                        finally:
                            try:
                                os.remove(temp_xml_path)
                            except Exception:
                                pass
                    complete_scan(code, parsed_data)

                self.runner.run_scan_stream(pipe_args, stream_line, on_nmap_done)

            threading.Thread(target=turbo_worker, daemon=True).start()
            return {"success": True}

        # ---------------- MODE C: SUBNET SWEEPER (Angry IP-Style) ----------------
        elif engine_mode == "subnet":
            def subnet_worker():
                stream_line(f"[🌐 Subnet Sweeper] Launching concurrent ICMP sweep on {target}...\n")
                self.subnet_sweeper = SubnetSweeper(subnet=target, max_workers=60, timeout=1.0)
                
                live_hosts = self.subnet_sweeper.sweep_subnet(
                    on_host_found=None,
                    on_progress=stream_line
                )

                # Format structured table for UI
                hosts_list = []
                for h in live_hosts:
                    hosts_list.append({
                        "ip": h["ip"],
                        "hostnames": [h["hostname"]] if h["hostname"] else [],
                        "state": "up",
                        "ports": [{
                            "port": "ICMP",
                            "protocol": "ECHO",
                            "state": "open",
                            "service": f"Host Online ({h['latency_ms']}ms)",
                            "product": "",
                            "version": "",
                            "reason": f"Latency: {h['latency_ms']}ms"
                        }]
                    })

                parsed_result = {
                    "scan_info": {"scanner": "Subnet Sweeper", "start_str": "Completed"},
                    "summary": {
                        "total_hosts": len(hosts_list),
                        "open_ports": len(hosts_list),
                        "up_hosts": len(hosts_list),
                        "down_hosts": 0
                    },
                    "hosts": hosts_list
                }
                complete_scan(0, parsed_result)

            threading.Thread(target=subnet_worker, daemon=True).start()
            return {"success": True}

        # ---------------- MODE A: STANDARD NMAP ----------------
        else:
            temp_xml = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
            temp_xml_path = temp_xml.name
            temp_xml.close()

            scan_args = []
            for f in flags:
                scan_args.extend(f.strip().split())

            if "-oX" not in scan_args:
                scan_args.extend(["-oX", temp_xml_path])
            scan_args.append(target)

            def on_complete(returncode: int, full_output: str):
                parsed_data = {}
                if os.path.exists(temp_xml_path):
                    try:
                        with open(temp_xml_path, "r", encoding="utf-8", errors="replace") as f:
                            parsed_data = parse_nmap_xml(f.read())
                    except Exception as e:
                        parsed_data = {"error": str(e)}
                    finally:
                        try:
                            os.remove(temp_xml_path)
                        except Exception:
                            pass
                complete_scan(returncode, parsed_data)

            try:
                self.runner.run_scan_stream(scan_args, stream_line, on_complete)
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}

    def cancel_scan(self) -> Dict[str, Any]:
        if self.runner:
            self.runner.cancel()
        if self.turbo_scanner:
            self.turbo_scanner.cancel()
        if self.subnet_sweeper:
            self.subnet_sweeper.cancel()
        return {"success": True}


def print_cli_banner():
    banner = r"""
 _   _                       ____  _             _ _       
| \ | |_ __ ___   __ _ _ __ / ___|| |_ _   _  __| (_) ___  
|  \| | '_ ` _ \ / _` | '_ \\___ \| __| | | |/ _` | |/ _ \ 
| |\  | | | | | | (_| | |_) |___) | |_| |_| | (_| | | (_) |
|_| \_|_| |_| |_|\__,_| .__/|____/ \__|\__,_|\__,_|_|\___/ 
                      |_| Next-Gen Reconnaissance Suite (v1.0.0)
    """
    print(banner)

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
        prog="nmap-studio",
        description="Nmap Studio — High-performance desktop reconnaissance suite combining Nmap, RustScan-speed async port discovery, Angry IP subnet sweeps, and an interactive 600+ NSE script browser.",
        epilog="Examples:\n  python main.py              # Launch the GUI Workspace\n  python main.py --check-env  # Validate local Nmap, Npcap & permissions\n  python main.py --version    # Print version info\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-v", "--version", action="version", version="Nmap Studio v1.0.0")
    parser.add_argument("--check-env", action="store_true", help="Diagnose local environment (Nmap binary, Npcap drivers, and privilege level)")
    parser.add_argument("--debug", action="store_true", help="Launch with Webview inspection DevTools enabled")
    parser.add_argument("--target", type=str, default="", help="Optional pre-filled target IP or CIDR on launch")
    return parser.parse_args()

def check_environment():
    print_cli_banner()
    adapter = get_platform_adapter()
    privs = adapter.check_privileges()
    nmap_bin = adapter.find_nmap()

    print("[*] Environment Diagnostic Check:")
    print(f"  • Operating System   : {privs['platform'].upper()} ({sys.platform})")
    print(f"  • Privilege Status   : {privs['elevation_label']} (Elevated: {privs['is_elevated']})")
    print(f"  • Raw Packet Driver  : {'Installed (Npcap)' if privs['npcap_detected'] else 'Not Detected'}")
    
    if nmap_bin and os.path.exists(nmap_bin):
        import subprocess
        try:
            ver = subprocess.check_output([nmap_bin, "--version"], text=True, stderr=subprocess.STDOUT).splitlines()[0]
        except Exception:
            ver = "Installed"
        print(f"  • Nmap Executable    : Found at {nmap_bin}")
        print(f"  • Nmap Version       : {ver}")
    else:
        print("  • Nmap Executable    : [!] Not found on PATH or standard directories.")

    # Check NSE scripts
    nse_mgr = NSEManager(nmap_bin)
    scripts = nse_mgr.load_scripts()
    print(f"  • NSE Script DB      : {len(scripts)} scripts indexed")
    print("\n[+] System is ready to launch Nmap Studio!\n")

def main():
    args = parse_args()

    if args.check_env:
        check_environment()
        return

    api = StudioApi()
    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    index_path = os.path.join(web_dir, "index.html")

    window = webview.create_window(
        title="NMAP STUDIO - All-in-One Pentest Recon Suite",
        url=index_path,
        js_api=api,
        width=1200,
        height=800,
        min_size=(950, 620),
        background_color="#080c14"
    )
    webview.start(debug=args.debug)

if __name__ == "__main__":
    main()

