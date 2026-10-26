import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def generate_inframapper_docx(output_path: str):
    doc = Document()

    # Define color scheme
    c_primary = RGBColor(6, 182, 212)    # Cyan
    c_dark = RGBColor(17, 24, 39)        # Dark Navy
    c_muted = RGBColor(100, 116, 139)    # Muted Gray

    # ------------------ COVER / TITLE PAGE ------------------
    p_title_space = doc.add_paragraph()
    p_title_space.paragraph_format.space_before = Pt(80)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("InfraMapper\n& Nmap Studio")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(36)
    r_title.font.bold = True
    r_title.font.color.rgb = c_primary

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Infrastructure Discovery & Network Asset Mapping Suite\nUser Guide & Technical Manual")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(15)
    r_sub.font.color.rgb = c_muted
    p_sub.paragraph_format.space_after = Pt(120)

    # Metadata Table
    table = doc.add_table(rows=5, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    meta_data = [
        ("Version:", "1.0"),
        ("Document Type:", "Product Guide & Operating Manual"),
        ("Classification:", "Public / Technical"),
        ("Engines Integrated:", "Nmap 7.99 + RustScan Turbo + Angry IP Sweeper"),
        ("NSE Scripts Supported:", "600+ Pre-Indexed Scripts")
    ]
    for idx, (label, val) in enumerate(meta_data):
        row = table.rows[idx]
        p_lbl = row.cells[0].paragraphs[0]
        r_lbl = p_lbl.add_run(label)
        r_lbl.font.bold = True
        r_lbl.font.size = Pt(10)
        
        p_val = row.cells[1].paragraphs[0]
        r_val = p_val.add_run(val)
        r_val.font.size = Pt(10)

    doc.add_page_break()

    # ------------------ TABLE OF CONTENTS ------------------
    p_toc_head = doc.add_heading("Table of Contents", level=1)
    p_toc_head.runs[0].font.color.rgb = c_dark

    toc_items = [
        "1. Introduction",
        "   1.1 Purpose of This Document",
        "   1.2 What is InfraMapper?",
        "   1.3 Key Features",
        "   1.4 Intended Audience",
        "2. Getting Started",
        "   2.1 System Requirements",
        "   2.2 Installation & Verification",
        "   2.3 CLI Diagnostic Usage (--check-env)",
        "3. Core Concepts",
        "   3.1 Host Discovery",
        "   3.2 Port Scanning",
        "   3.3 Service & Version Detection",
        "   3.4 OS Fingerprinting",
        "   3.5 Asset Inventory & Mapping",
        "4. Scanning Engines & Modes",
        "   4.1 Precision Nmap Mode",
        "   4.2 Turbo Recon Mode (RustScan-Style Async Sweeper)",
        "   4.3 Subnet Sweeper Mode (Angry IP Scanner Style)",
        "   4.4 600+ NSE Script Browser",
        "5. Security, Legal & Best Practices",
        "6. Troubleshooting & FAQ",
        "7. Quick Reference Card"
    ]
    for item in toc_items:
        p_item = doc.add_paragraph()
        r_item = p_item.add_run(item)
        r_item.font.size = Pt(10)
        p_item.paragraph_format.space_after = Pt(2)

    doc.add_page_break()

    # ------------------ SECTION 1: INTRODUCTION ------------------
    doc.add_heading("1. Introduction", level=1)
    
    doc.add_heading("1.1 Purpose of This Document", level=2)
    doc.add_paragraph(
        "This guide explains how to install, configure, and use InfraMapper, an infrastructure-based "
        "network discovery and asset mapping suite integrated into Nmap Studio. It is designed for "
        "network administrators, penetration testers, security engineers, and IT operations teams."
    )

    doc.add_heading("1.2 What is InfraMapper?", level=2)
    doc.add_paragraph(
        "InfraMapper is an infrastructure-based scanner that discovers live hosts, open ports, running "
        "services, and operating systems across IP ranges and subnets. It maps your network infrastructure "
        "and produces structured asset inventories. Unlike heavy application-layer fuzzers, InfraMapper "
        "focuses on network visibility, attack surface reduction, and asset inventory validation."
    )

    doc.add_heading("1.3 Key Features", level=2)
    features = [
        "Live host discovery via ICMP ping sweeps, ARP, and TCP/UDP probes.",
        "Ultra-fast asynchronous port sweeps (RustScan-style) checking thousands of ports in seconds.",
        "High-concurrency subnet discovery (Angry IP Scanner style) across CIDR ranges (/24, /16).",
        "Official Nmap service fingerprinting (-sV) and OS detection (-O).",
        "Interactive 600+ NSE Script Browser with real-time categorization and search.",
        "Transparent CLI generation: users always see the exact command line being run.",
        "Resource-optimized: runs smoothly on modest hardware (Intel i3 with 2GB RAM)."
    ]
    for f in features:
        doc.add_paragraph(f, style='List Bullet')

    # Audience Table
    doc.add_heading("1.4 Intended Audience", level=2)
    aud_table = doc.add_table(rows=5, cols=2)
    aud_table.style = 'Table Grid'
    aud_rows = [
        ("Role", "How They Use InfraMapper"),
        ("Network Administrator", "Map subnets, identify rogue/unknown devices, verify firewall rules."),
        ("Security Engineer", "Perform asset discovery, attack-surface mapping, and vulnerability scanning."),
        ("IT Operations", "Track infrastructure changes and maintain accurate CMDB inventories."),
        ("Compliance Auditor", "Audit exposed ports, services, and verify network segmentation policies.")
    ]
    for idx, (r, desc) in enumerate(aud_rows):
        row = aud_table.rows[idx]
        row.cells[0].paragraphs[0].add_run(r).bold = (idx == 0)
        row.cells[1].paragraphs[0].add_run(desc).bold = (idx == 0)

    # ------------------ SECTION 2: GETTING STARTED ------------------
    doc.add_heading("2. Getting Started", level=1)
    doc.add_heading("2.1 System Requirements", level=2)
    
    req_table = doc.add_table(rows=6, cols=3)
    req_table.style = 'Table Grid'
    req_rows = [
        ("Component", "Minimum", "Recommended"),
        ("Operating System", "Windows 10/11, Linux, or macOS", "Windows 11 / Kali Linux"),
        ("Processor (CPU)", "2 Cores (Intel i3 supported)", "4+ Cores"),
        ("Memory (RAM)", "2 GB", "8 GB+"),
        ("Disk Space", "500 MB", "2 GB"),
        ("Privileges", "Standard user (TCP Connect)", "Administrator / Root (SYN & OS scans)")
    ]
    for idx, (c, m, r) in enumerate(req_rows):
        row = req_table.rows[idx]
        row.cells[0].paragraphs[0].add_run(c).bold = (idx == 0)
        row.cells[1].paragraphs[0].add_run(m).bold = (idx == 0)
        row.cells[2].paragraphs[0].add_run(r).bold = (idx == 0)

    doc.add_heading("2.2 Installation & Verification", level=2)
    doc.add_paragraph("Clone the repository and install the lightweight Python dependencies:")
    p_cmd = doc.add_paragraph("git clone https://github.com/your-username/nmap-studio.git\ncd nmap-studio\npip install -r requirements.txt")
    p_cmd.style = 'Quote'

    doc.add_paragraph("Run the built-in diagnostic command to check local Nmap, Npcap drivers, and privilege state:")
    p_diag = doc.add_paragraph("python main.py --check-env")
    p_diag.style = 'Quote'

    # ------------------ SECTION 3: SCANNING ENGINES & MODES ------------------
    doc.add_heading("3. Scanning Engines & Modes", level=1)
    
    doc.add_heading("3.1 Precision Nmap Mode", level=2)
    doc.add_paragraph(
        "Directly wraps the installed Nmap binary with all selected flags. Provides full manual control "
        "over timing templates (-T0 to -T5), scan techniques (-sS, -sT, -sU), and output options."
    )

    doc.add_heading("3.2 Turbo Recon Mode (RustScan Style)", level=2)
    doc.add_paragraph(
        "Utilizes a high-concurrency non-blocking asyncio socket scanner. It sweeps thousands of ports in "
        "seconds, filters out dead ports, and automatically pipes only the discovered open ports into Nmap "
        "for deep version and NSE script inspection."
    )

    doc.add_heading("3.3 Subnet Sweeper Mode (Angry IP Style)", level=2)
    doc.add_paragraph(
        "A multi-threaded concurrent ICMP/ARP ping engine designed to map entire subnets (/24, /16) rapidly. "
        "It outputs latency in milliseconds, performs reverse DNS resolution, and displays online hosts."
    )

    doc.add_heading("3.4 Interactive 600+ NSE Script Browser", level=2)
    doc.add_paragraph(
        "Accessible directly via the '📜 NSE Script Browser' tab in the UI. Automatically parses the official "
        "Nmap script.db, organizing scripts into categories (vuln, safe, auth, discovery, exploit). Selecting "
        "any script automatically constructs and preview the exact --script= CLI argument."
    )

    # ------------------ SECTION 4: SECURITY & QUICK REF ------------------
    doc.add_heading("4. Security & Legal Best Practices", level=1)
    doc.add_paragraph(
        "Warning: Port scanning networks without explicit prior written authorization is illegal in most jurisdictions. "
        "Always adhere to the following rules:\n"
        "• Obtain written scope, target CIDRs, and testing windows before scanning.\n"
        "• Avoid aggressive timing (-T4/-T5) on delicate OT, medical, or legacy embedded systems.\n"
        "• Maintain detailed scan logs for auditability and compliance."
    )

    doc.add_heading("5. Quick Reference Card", level=1)
    ref_card = (
        "+----------------------------------------------------------------------+\n"
        "|                    InfraMapper Quick Reference                       |\n"
        "+----------------------------------------------------------------------+\n"
        "| Discover live hosts:       nmap -sn <CIDR>                           |\n"
        "| Port + service inventory:  nmap -sS -sV <IP>                         |\n"
        "| Full profile scan:         nmap -sS -sV -O <IP>                      |\n"
        "| Turbo async scan:          Select 'Turbo (RustScan)' in GUI          |\n"
        "| Subnet IP sweep:           Select 'Subnet (Angry IP)' in GUI         |\n"
        "| NSE Script Browser:        Click 'NSE Script Browser' Tab            |\n"
        "| Run Environment Check:     python main.py --check-env                |\n"
        "+----------------------------------------------------------------------+"
    )
    p_ref = doc.add_paragraph(ref_card)
    p_ref.style = 'Quote'

    # Save to file
    doc.save(output_path)

if __name__ == "__main__":
    out = os.path.abspath(r"d:\Nmap-Custom\nmap-studio\InfraMapper_User_Guide.docx")
    generate_inframapper_docx(out)
    print(f"Generated DOCX at: {out}")
