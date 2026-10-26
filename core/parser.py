import xml.etree.ElementTree as ET
from typing import Dict, Any, List

def parse_nmap_xml(xml_content: str) -> Dict[str, Any]:
    """Parses raw Nmap XML output (-oX) into a clean structured dictionary."""
    result: Dict[str, Any] = {
        "hosts": [],
        "scan_info": {},
        "summary": {"total_hosts": 0, "up_hosts": 0, "down_hosts": 0, "open_ports": 0}
    }

    if not xml_content or not xml_content.strip():
        return result

    try:
        root = ET.fromstring(xml_content)
    except Exception as e:
        result["error"] = f"Failed to parse XML: {str(e)}"
        return result

    # Extract scan run metadata
    result["scan_info"] = {
        "scanner": root.get("scanner", "nmap"),
        "args": root.get("args", ""),
        "start_str": root.get("startstr", ""),
        "version": root.get("version", "")
    }

    # Extract hosts
    total_open_ports = 0
    for host_el in root.findall("host"):
        status_el = host_el.find("status")
        state = status_el.get("state", "unknown") if status_el is not None else "unknown"

        # Addresses
        ipv4 = ""
        ipv6 = ""
        mac = ""
        mac_vendor = ""
        for addr_el in host_el.findall("address"):
            addr_type = addr_el.get("addrtype", "")
            addr_val = addr_el.get("addr", "")
            if addr_type == "ipv4":
                ipv4 = addr_val
            elif addr_type == "ipv6":
                ipv6 = addr_val
            elif addr_type == "mac":
                mac = addr_val
                mac_vendor = addr_el.get("vendor", "")

        # Hostnames
        hostnames = []
        hostnames_el = host_el.find("hostnames")
        if hostnames_el is not None:
            for h_el in hostnames_el.findall("hostname"):
                name = h_el.get("name", "")
                if name:
                    hostnames.append(name)

        # Ports
        ports = []
        ports_el = host_el.find("ports")
        if ports_el is not None:
            for p_el in ports_el.findall("port"):
                protocol = p_el.get("protocol", "tcp")
                port_id = p_el.get("portid", "")
                state_el = p_el.find("state")
                port_state = state_el.get("state", "") if state_el is not None else ""
                reason = state_el.get("reason", "") if state_el is not None else ""

                service_el = p_el.find("service")
                service_name = service_el.get("name", "") if service_el is not None else ""
                service_product = service_el.get("product", "") if service_el is not None else ""
                service_version = service_el.get("version", "") if service_el is not None else ""
                service_extrainfo = service_el.get("extrainfo", "") if service_el is not None else ""

                if port_state == "open":
                    total_open_ports += 1

                ports.append({
                    "port": int(port_id) if port_id.isdigit() else port_id,
                    "protocol": protocol,
                    "state": port_state,
                    "reason": reason,
                    "service": service_name,
                    "product": service_product,
                    "version": service_version,
                    "extra_info": service_extrainfo
                })

        # OS detection
        os_matches = []
        os_el = host_el.find("os")
        if os_el is not None:
            for osmatch_el in os_el.findall("osmatch"):
                os_matches.append({
                    "name": osmatch_el.get("name", ""),
                    "accuracy": osmatch_el.get("accuracy", "")
                })

        result["hosts"].append({
            "ip": ipv4 or ipv6 or "Unknown",
            "ipv4": ipv4,
            "ipv6": ipv6,
            "mac": mac,
            "mac_vendor": mac_vendor,
            "hostnames": hostnames,
            "state": state,
            "ports": ports,
            "os_matches": os_matches
        })

    # Summary
    up_count = sum(1 for h in result["hosts"] if h["state"] == "up")
    result["summary"]["total_hosts"] = len(result["hosts"])
    result["summary"]["up_hosts"] = up_count
    result["summary"]["down_hosts"] = len(result["hosts"]) - up_count
    result["summary"]["open_ports"] = total_open_ports

    return result
