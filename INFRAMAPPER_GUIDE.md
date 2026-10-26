# InfraMapper & Nmap Studio User Guide & Documentation

Version: 1.0  
Classification: Public / Technical Manual  

---

## 1. Introduction

### 1.1 Purpose of This Document
This guide explains how to install, configure, and use **InfraMapper** (integrated inside **Nmap Studio**), an infrastructure-based network discovery and asset mapping suite. It is designed for network administrators, security engineers, and IT operations teams.

### 1.2 What is InfraMapper?
**InfraMapper** is an infrastructure-based scanner that discovers live hosts, open ports, running services, and operating systems across IP ranges and subnets. It maps your network infrastructure and produces an asset inventory — focused on **infrastructure mapping and asset visibility** rather than application-layer fuzzing.

> **Category:** Infrastructure / Network & Asset Discovery Scanner (NOT an application scanner).

### 1.3 Key Features
- Live host discovery (ping sweeps, ARP, TCP/UDP probes)
- Ultra-fast port scanning (RustScan-style async port sweep)
- Multi-threaded subnet mapping (Angry IP style)
- Service & version detection via Nmap (`-sV`)
- OS fingerprinting (`-O`)
- Subnet / CIDR range scanning (`/24`, `/16`)
- Interactive 600+ NSE script browser (`--script=...`)
- Real-time command preview and clipboard export
- Asset inventory export (XML, JSON, text)

### 1.4 Intended Audience
| Role | How They Use It |
|---|---|
| Network Admin | Map subnets, find unknown devices |
| Security Engineer | Asset inventory, attack-surface visibility |
| IT Operations | Track infrastructure changes |
| Auditor | Verify asset registers & compliance |

---

## 2. Getting Started

### 2.1 System Requirements
| Component | Minimum | Recommended |
|---|---|---|
| OS | Linux / Windows / macOS | Windows 10/11 or Kali Linux |
| CPU | 2 cores (Intel i3 supported) | 4+ cores |
| RAM | 2 GB | 8 GB |
| Disk | 500 MB | 5 GB |
| Privileges | Standard user for TCP Connect; Admin/Root for SYN & OS scans | Root / Administrator |

### 2.2 Installation
```bash
git clone https://github.com/your-username/nmap-studio.git
cd nmap-studio
pip install -r requirements.txt
```

Verify your environment:
```bash
python main.py --check-env
```

### 2.3 First Scan (Quick Start)
```bash
# Launch GUI Workspace
python main.py

# CLI Environment Verification
python main.py -h
```

---

## 3. Core Concepts

### 3.1 Host Discovery
Determines which hosts are alive using ICMP ping, ARP, or TCP probes.
```bash
nmap -sn 192.168.1.0/24
```

### 3.2 Port Scanning
Identifies open TCP/UDP ports.
```bash
nmap -sS -p 1-1000 10.0.0.5     # SYN scan (stealth, root/admin)
nmap -sT -p 1-1000 10.0.0.5     # TCP connect (standard user)
nmap -p- 10.0.0.5              # Full 65,535 ports
```

### 3.3 Service & Version Detection
Identifies services and versions on open ports.
```bash
nmap -sV 10.0.0.5
```

### 3.4 OS Fingerprinting
Identifies operating systems via TCP/IP stack fingerprinting.
```bash
nmap -O 10.0.0.5
```

---

## 4. Using the Scanning Modes

| Mode | Engine | Best Used For |
|---|---|---|
| Precision Nmap | Stock Nmap CLI | Detailed flag customization and deep pentest scans |
| Turbo Recon | RustScan Async Socket Engine | Sweeps all ports in seconds, then pipes into Nmap |
| Subnet Sweeper | Angry IP Scanner ICMP Engine | Fast live host discovery across `/24` or `/16` networks |

---

## 5. Security & Legal Considerations

> **Warning:** Scanning networks you do not own or do not have explicit written permission to test is illegal in most jurisdictions.

- Always obtain **written authorization** before initiating scans.
- Log scan sessions for auditability.
- Use rate-limiting (`-T2` or `--max-rate`) on sensitive production networks.

---

## 6. Quick Reference Card

```text
+--------------------------------------------------------------+
|                InfraMapper Quick Reference                   |
+--------------------------------------------------------------+
| Discover live hosts:       nmap -sn <CIDR>                   |
| Port + service inventory:  nmap -sS -sV <IP>                 |
| Full profile scan:         nmap -sS -sV -O <IP>              |
| Turbo async scan:          Select "Turbo (RustScan)" in GUI  |
| Subnet IP sweep:           Select "Subnet (Angry IP)" in GUI |
| NSE Script Browser:        Click "NSE Script Browser" Tab    |
| Type:                      Infrastructure / Asset Scanner    |
+--------------------------------------------------------------+
```
