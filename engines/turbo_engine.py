import asyncio
import socket
import time
from typing import List, Callable, Optional

class TurboPortScanner:
    """
    High-speed asynchronous port scanner inspired by RustScan.
    Sweeps ports concurrently using non-blocking asyncio sockets,
    then returns discovered open ports to pipe directly into Nmap.
    No Rust/Cargo installation required.
    """
    def __init__(self, target: str, port_range: range = range(1, 1001), concurrency: int = 500, timeout: float = 1.0):
        self.target = target
        self.port_range = port_range
        self.concurrency = concurrency
        self.timeout = timeout
        self.open_ports: List[int] = []
        self._cancelled = False

    async def _check_port(self, port: int, sem: asyncio.Semaphore, on_open: Optional[Callable[[int], None]]):
        if self._cancelled:
            return
        async with sem:
            try:
                conn = asyncio.open_connection(self.target, port)
                _, writer = await asyncio.wait_for(conn, timeout=self.timeout)
                writer.close()
                await writer.wait_closed()
                self.open_ports.append(port)
                if on_open:
                    on_open(port)
            except Exception:
                pass

    async def scan_ports_async(self, on_progress: Optional[Callable[[str], None]], on_open: Optional[Callable[[int], None]]) -> List[int]:
        self.open_ports = []
        self._cancelled = False
        sem = asyncio.Semaphore(self.concurrency)
        
        total = len(self.port_range)
        if on_progress:
            on_progress(f"[TurboScan] Sweeping {total} ports on {self.target} (Concurrency: {self.concurrency}, Timeout: {self.timeout}s)...\n")

        start_time = time.time()
        tasks = [self._check_port(port, sem, on_open) for port in self.port_range]
        await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = round(time.time() - start_time, 2)
        self.open_ports.sort()
        if on_progress:
            on_progress(f"[TurboScan] Sweep finished in {elapsed}s. Found {len(self.open_ports)} open port(s): {self.open_ports}\n")

        return self.open_ports

    def cancel(self):
        self._cancelled = True
