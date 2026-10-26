from typing import List, Dict, Any

CATEGORIZED_FLAGS: Dict[str, List[Dict[str, Any]]] = {
    "scan_techniques": [
        {"flag": "-sS", "name": "TCP SYN Stealth", "desc": "Fast, stealthy SYN scan. Doesn't complete 3-way handshake.", "requires_root": True},
        {"flag": "-sT", "name": "TCP Connect", "desc": "Standard 3-way handshake scan. No privileges required.", "requires_root": False},
        {"flag": "-sU", "name": "UDP Scan", "desc": "Scans UDP services (DNS, SNMP, DHCP). Can be slow.", "requires_root": True},
        {"flag": "-sA", "name": "TCP ACK", "desc": "Maps firewall rulesets and filtered ports.", "requires_root": True},
        {"flag": "-sN", "name": "TCP NULL", "desc": "Sets no flags in TCP header to bypass stateful firewalls.", "requires_root": True},
        {"flag": "-sF", "name": "TCP FIN", "desc": "Sets only the TCP FIN bit.", "requires_root": True},
        {"flag": "-sX", "name": "TCP Xmas", "desc": "Sets FIN, PSH, and URG flags (lights up like a Christmas tree).", "requires_root": True},
    ],
    "host_discovery": [
        {"flag": "-Pn", "name": "Skip Ping (Pn)", "desc": "Treat all hosts as online -- bypass host discovery block.", "requires_root": False},
        {"flag": "-sn", "name": "Ping Scan Only", "desc": "Determine live hosts without port scanning.", "requires_root": False},
        {"flag": "-n", "name": "No Reverse DNS", "desc": "Never resolve IP addresses to names (drastically speeds up scan).", "requires_root": False},
        {"flag": "-R", "name": "Always Resolve DNS", "desc": "Always resolve reverse DNS for all target IPs.", "requires_root": False},
        {"flag": "--traceroute", "name": "Traceroute", "desc": "Trace network hop path to each host.", "requires_root": True},
    ],
    "service_os": [
        {"flag": "-sV", "name": "Service Version Detection", "desc": "Probes open ports to determine service name & version.", "requires_root": False},
        {"flag": "-O", "name": "OS Detection", "desc": "TCP/IP fingerprinting to identify Operating System.", "requires_root": True},
        {"flag": "-A", "name": "Aggressive Mode (-A)", "desc": "Enables OS detection, Version detection, Script scanning, and Traceroute.", "requires_root": True},
        {"flag": "-sC", "name": "Default NSE Scripts", "desc": "Runs standard, safe vulnerability & discovery scripts equivalent to --script=default.", "requires_root": False},
    ],
    "timing_perf": [
        {"flag": "-T0", "name": "Paranoid (T0)", "desc": "Extremely slow for IDS evasion.", "requires_root": False},
        {"flag": "-T1", "name": "Sneaky (T1)", "desc": "Slow for IDS evasion.", "requires_root": False},
        {"flag": "-T2", "name": "Polite (T2)", "desc": "Consumes less bandwidth and target resources.", "requires_root": False},
        {"flag": "-T3", "name": "Normal (T3)", "desc": "Standard default timing.", "requires_root": False},
        {"flag": "-T4", "name": "Aggressive (T4)", "desc": "Fast and reliable scan for modern responsive networks.", "requires_root": False},
        {"flag": "-T5", "name": "Insane (T5)", "desc": "Extreme speed. Might miss ports on slow links.", "requires_root": False},
        {"flag": "--min-parallelism 10", "name": "Min Parallelism (10)", "desc": "Forces at least 10 parallel probes for speed on fast networks.", "requires_root": False},
        {"flag": "--max-parallelism 50", "name": "Max Parallelism (50)", "desc": "Limits concurrency to 50 probes to preserve network/CPU stability.", "requires_root": False},
        {"flag": "--min-rate 100", "name": "Min Rate (100 pkt/s)", "desc": "Send at least 100 packets per second.", "requires_root": False},
        {"flag": "--max-rate 1000", "name": "Max Rate (1000 pkt/s)", "desc": "Cap outbound traffic to 1000 packets per second.", "requires_root": False},
        {"flag": "--host-timeout 15m", "name": "Host Timeout (15m)", "desc": "Give up on slow or unresponsive targets after 15 minutes.", "requires_root": False},
    ],
    "output_opts": [
        {"flag": "--open", "name": "Open Ports Only", "desc": "Show only open (or possibly open) ports.", "requires_root": False},
        {"flag": "-v", "name": "Verbose (-v)", "desc": "Increase verbosity level.", "requires_root": False},
        {"flag": "-vv", "name": "Very Verbose (-vv)", "desc": "High verbosity details during scan.", "requires_root": False},
        {"flag": "--reason", "name": "Show Port Reason", "desc": "Display the exact TCP/ICMP packet reason for port state.", "requires_root": False},
    ]
}

PROFILES = [
    {
        "id": "quick_scan",
        "name": "Quick Recon",
        "description": "Fast top 100 ports scan with aggressive timing.",
        "flags": ["-T4", "-F", "--open"]
    },
    {
        "id": "full_tcp",
        "name": "Full TCP Port Scan",
        "description": "Scans all 65,535 TCP ports without DNS resolution.",
        "flags": ["-p-", "-T4", "-n"]
    },
    {
        "id": "service_detection",
        "name": "Service & Version Fingerprint",
        "description": "Determines application versions and banners on open ports.",
        "flags": ["-sV", "-T4", "--open"]
    },
    {
        "id": "intense_scan",
        "name": "Intense Scan (OS + Services + Scripts)",
        "description": "Comprehensive aggressive pentesting scan (-A).",
        "flags": ["-A", "-T4"]
    },
    {
        "id": "ping_sweep",
        "name": "Host Discovery Ping Sweep",
        "description": "Quickly identify online hosts in a subnet without port scanning.",
        "flags": ["-sn", "-n"]
    },
    {
        "id": "stealth_syn",
        "name": "Stealth SYN Scan",
        "description": "SYN half-open scan bypassing connection logging.",
        "flags": ["-sS", "-T3", "-Pn"]
    }
]
