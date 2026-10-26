<p align="center">
  <h1 align="center">⚡ NMAP STUDIO</h1>
  <p align="center">
    <strong>The Next-Generation Desktop Reconnaissance Suite for Penetration Testers & Security Engineers</strong>
  </p>
  <p align="center">
    <a href="#-key-features">Features</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-quickstart">Quickstart</a> •
    <a href="#-cli-usage">CLI Usage</a> •
    <a href="#-open-source-roadmap">Roadmap</a> •
    <a href="#-license">License</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Nmap-v7.9%2B-red?logo=kalilinux&logoColor=white" alt="Nmap">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-informational" alt="Platforms">
    <img src="https://img.shields.io/badge/License-MIT-emerald" alt="License">
    <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen" alt="PRs Welcome">
  </p>
</p>

---

## 💡 Overview

**Nmap Studio** is a high-performance, modern graphical workspace designed to replace legacy, unmaintained tools like Zenmap. It bridges the precision and authority of official **Nmap** with the ultra-fast speeds of **RustScan** and the rapid subnet sweeps of **Angry IP Scanner** — all bundled into a single, cohesive, dark-themed desktop application.

> **Zero Extra Clones Required:** Everything runs seamlessly through native Python asynchronous engines and stock Nmap CLI calls.

---

## ✨ Key Features

- **⚡ Precision Nmap Engine**: Full manual flag customization and preset pentesting profiles (*Quick Recon*, *Full TCP*, *Service Fingerprint*, *Intense Scan*, *Ping Sweep*, *Stealth SYN*).
- **🚀 Turbo Recon (RustScan-Style)**: Built-in asynchronous socket engine that sweeps thousands of ports in seconds, automatically piping discovered open ports directly into Nmap for deep version and script auditing (`-sV -sC`).
- **🌐 Subnet Sweeper (Angry IP-Style)**: High-speed multi-threaded ICMP/ARP host discovery across CIDR subnets (`/24`, `/16`), measuring response latency and resolving reverse DNS.
- **📜 600+ NSE Script Browser**: Search, filter by category (`vuln`, `exploit`, `auth`, `safe`, `discovery`), and select Nmap scripts with live command preview generation.
- **💻 Low-Resource Footprint**: Engineered with non-blocking async architecture and a real-time CPU/RAM monitor widget that runs smoothly on low-end hardware (e.g., Intel i3 with 2GB RAM).
- **🛡️ Capability & Privilege Aware**: Automatically detects Administrator/root status and Npcap packet driver presence, clearly badging scans requiring raw socket privileges.
- **📋 Transparent CLI First**: Never obscures underlying commands. Always displays the exact CLI command with a one-click clipboard copy button.

---

## 🏗️ Architecture

```
nmap-studio/
├── main.py                  # CLI argument parser, webview lifecycle & bridge
├── requirements.txt         # Lightweight dependencies (pywebview, psutil)
├── engines/                 # All-in-One Multi-Engine Subsystem
│   ├── turbo_engine.py      # Asyncio port sweeper (RustScan style)
│   └── subnet_engine.py     # Multi-threaded ping sweeper (Angry IP style)
├── core/
│   ├── runner.py            # Async subprocess runner & live stdout streamer
│   ├── flags.py             # Nmap 7.9x flag taxonomy and pentest profiles
│   ├── parser.py            # Machine-readable -oX XML parser to structured tables
│   └── nse_manager.py       # Script.db indexer for 600+ NSE scripts
├── platform_adapters/       # Isolated cross-platform abstraction layer
│   ├── base.py              # Platform interface
│   ├── windows.py           # Windows binary resolution & Npcap detection
│   └── posix.py             # Linux & macOS adapters (sudo / WebKit)
└── web/                     # 3-Column Modern Workspace UI
    ├── index.html           # Pentest workspace layout
    ├── css/app.css          # Cyberpunk dark theme styles
    └── js/app.js            # Frontend reactivity, API bridge, and tab controllers
```

---

## 🚀 Quickstart

### Prerequisites

* **Python**: 3.10 or higher
* **Nmap**: Installed on system (e.g. `nmap` on PATH or standard program files)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/nmap-studio.git
cd nmap-studio

# Install dependencies
pip install -r requirements.txt
```

### Launch the Workspace

```bash
python main.py
```

---

## 💻 CLI Usage

Nmap Studio features a built-in diagnostic and launch CLI:

```bash
# Display help and usage manual
python main.py -h

# Run environment diagnostics (checks Nmap, Npcap & permissions)
python main.py --check-env

# Print application version
python main.py --version

# Launch with frontend DevTools enabled (for developers)
python main.py --debug
```

### CLI Output Example (`--check-env`)

```text
 _   _                       ____  _             _ _       
| \ | |_ __ ___   __ _ _ __ / ___|| |_ _   _  __| (_) ___  
|  \| | '_ ` _ \ / _` | '_ \\___ \| __| | | |/ _` | |/ _ \ 
| |\  | | | | | | (_| | |_) |___) | |_| |_| | (_| | | (_) |
|_| \_|_| |_| |_|\__,_| .__/|____/ \__|\__,_|\__,_|_|\___/ 
                      |_| Next-Gen Reconnaissance Suite (v1.0.0)

[*] Environment Diagnostic Check:
  • Operating System   : WINDOWS (win32)
  • Privilege Status   : Standard User (Elevated: False)
  • Raw Packet Driver  : Installed (Npcap)
  • Nmap Executable    : Found at C:\Program Files (x86)\Nmap\nmap.exe
  • Nmap Version       : Nmap version 7.99 ( https://nmap.org )
  • NSE Script DB      : 612 scripts indexed

[+] System is ready to launch Nmap Studio!
```

---

## 🤝 Contributing

Contributions are welcomed and encouraged! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on code style, non-blocking architecture guidelines, and the pull request submission process.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details. Nmap, RustScan, Masscan, and Angry IP Scanner are the intellectual property of their respective creators.
