import ipaddress
import socket
import concurrent.futures
import time
import subprocess
import sys
from typing import List, Dict, Any, Callable, Optional

class SubnetSweeper:
    """
    Fast multi-threaded subnet and network discovery engine inspired by Angry IP Scanner (ipscan).
    Pings and resolves hosts, hostnames, and response latencies across CIDR ranges (/24, /16).
    """
    def __init__(self, subnet: str, max_workers: int = 50, timeout: float = 1.0):
        self.subnet_str = subnet
        self.max_workers = max_workers
        self.timeout = timeout
        self._cancelled = False

    def _ping_host(self, ip_str: str) -> Optional[Dict[str, Any]]:
        if self._cancelled:
            return None

        # Windows vs POSIX ping command
        if sys.platform == "win32":
            cmd = ["ping", "-n", "1", "-w", str(int(self.timeout * 1000)), ip_str]
        else:
            cmd = ["ping", "-c", "1", "-W", str(int(self.timeout)), ip_str]

        start_time = time.time()
        try:
            startupinfo = None
            creationflags = 0
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

            proc = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=self.timeout + 0.5
            )
            is_up = (proc.returncode == 0)
        except Exception:
            is_up = False

        latency = round((time.time() - start_time) * 1000, 1)

        if is_up:
            # Try hostname resolution
            hostname = ""
            try:
                hostname = socket.gethostbyaddr(ip_str)[0]
            except Exception:
                pass

            return {
                "ip": ip_str,
                "hostname": hostname,
                "latency_ms": latency,
                "state": "up"
            }
        return None

    def sweep_subnet(
        self,
        on_host_found: Optional[Callable[[Dict[str, Any]], None]],
        on_progress: Optional[Callable[[str], None]]
    ) -> List[Dict[str, Any]]:
        self._cancelled = False
        live_hosts: List[Dict[str, Any]] = []

        try:
            network = ipaddress.ip_network(self.subnet_str, strict=False)
            hosts = list(network.hosts())
            if not hosts:
                hosts = [ipaddress.ip_address(self.subnet_str)]
        except Exception as e:
            if on_progress:
                on_progress(f"[SubnetSweeper] Invalid target subnet: {str(e)}\n")
            return live_hosts

        total = len(hosts)
        if on_progress:
            on_progress(f"[SubnetSweeper] Sweeping {total} IP address(es) across {self.subnet_str}...\n")

        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ip = {executor.submit(self._ping_host, str(ip)): str(ip) for ip in hosts}
            for future in concurrent.futures.as_completed(future_to_ip):
                if self._cancelled:
                    break
                res = future.result()
                if res:
                    live_hosts.append(res)
                    if on_host_found:
                        on_host_found(res)
                    if on_progress:
                        host_info = f" ({res['hostname']})" if res['hostname'] else ""
                        on_progress(f"  [+] Host Alive: {res['ip']}{host_info} [{res['latency_ms']}ms]\n")

        elapsed = round(time.time() - start, 2)
        live_hosts.sort(key=lambda h: ipaddress.ip_address(h["ip"]))
        if on_progress:
            on_progress(f"[SubnetSweeper] Completed in {elapsed}s. {len(live_hosts)} active host(s) discovered.\n")

        return live_hosts

    def cancel(self):
        self._cancelled = True
