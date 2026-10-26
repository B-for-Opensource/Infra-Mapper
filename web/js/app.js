let currentProfileId = "quick_scan";
let currentEngineMode = "nmap"; // "nmap" | "turbo" | "subnet"
let selectedCustomFlags = new Set();
let isScanning = false;
let catalog = {};
let profiles = [];
let systemStatus = {};
let activeCategoryKey = "scan_techniques";
let monitorIntervalId = null;

const categoryDisplayMap = {
  scan_techniques: "Scan Types",
  host_discovery: "Discovery",
  service_os: "Service & OS",
  timing_perf: "Timing & Perf",
  output_opts: "Output"
};

// Listen for pywebview ready event
window.addEventListener("pywebviewready", async () => {
  // First notify python that webview DOM is alive
  if (window.pywebview && window.pywebview.api && window.pywebview.api.on_loaded) {
    try {
      await window.pywebview.api.on_loaded();
    } catch (e) {
      console.warn("on_loaded ping:", e);
    }
  }

  // Load system data without blocking
  await loadInitialData();
  startResourceMonitor();
});

// Fallback for direct browser testing
window.addEventListener("DOMContentLoaded", () => {
  if (!window.pywebview) {
    setTimeout(loadInitialData, 500);
  }
});

async function loadInitialData() {
  if (!window.pywebview || !window.pywebview.api) {
    return;
  }

  try {
    const data = await window.pywebview.api.get_system_info();
    systemStatus = data.platform_info;
    catalog = data.flag_catalog;
    profiles = data.profiles;
    const nmapInfo = data.nmap_info;

    // Set navbar status pills
    document.getElementById("platform-label").textContent = (systemStatus.platform || "OS").toUpperCase();
    
    const privLabel = document.getElementById("privilege-label");
    privLabel.textContent = systemStatus.elevation_label;
    const privInd = document.getElementById("priv-indicator");
    if (!systemStatus.is_elevated) {
      privInd.classList.add("warning");
    }

    const binLabel = document.getElementById("binary-label");
    const binInd = document.getElementById("bin-indicator");
    if (nmapInfo.found) {
      binLabel.textContent = `Nmap ${nmapInfo.version}`;
    } else {
      binLabel.textContent = "Nmap Missing";
      binInd.classList.add("warning");
    }

    // Initialize Default Profile
    const defaultProf = profiles.find(p => p.id === currentProfileId);
    if (defaultProf) {
      defaultProf.flags.forEach(f => selectedCustomFlags.add(f));
    }

    renderProfilesList();
    renderCategoryTabs();
    renderFlagsGrid(activeCategoryKey);
    updateCommandPreview();
  } catch (err) {
    console.error("Initialization error:", err);
  }
}

// Resource Monitor (Polls every 1.5s with non-blocking psutil query)
function startResourceMonitor() {
  if (monitorIntervalId) return;

  monitorIntervalId = setInterval(async () => {
    if (!window.pywebview || !window.pywebview.api || !window.pywebview.api.get_system_resources) {
      return;
    }
    try {
      const res = await window.pywebview.api.get_system_resources();
      const cpuEl = document.getElementById("cpu-val");
      const ramEl = document.getElementById("ram-val");
      const monitorDot = document.getElementById("monitor-dot");

      if (cpuEl) cpuEl.textContent = `CPU: ${res.cpu}%`;
      
      if (ramEl) {
        if (res.is_scanning && res.nmap_ram_mb > 0) {
          ramEl.textContent = `Nmap: ${res.nmap_ram_mb}MB`;
        } else {
          ramEl.textContent = `RAM: ${res.ram_percent}%`;
        }
      }

      if (monitorDot) {
        if (res.is_scanning) {
          monitorDot.style.backgroundColor = "var(--accent-cyan)";
        } else {
          monitorDot.style.backgroundColor = "var(--accent-emerald)";
        }
      }
    } catch (e) {
      // Ignore background monitor error
    }
  }, 1500);
}

// 1. Render Profiles in Column 1
function renderProfilesList() {
  const container = document.getElementById("profile-container");
  container.innerHTML = "";

  profiles.forEach(p => {
    const item = document.createElement("div");
    item.className = `profile-item ${p.id === currentProfileId ? "active" : ""}`;
    item.onclick = () => selectProfile(p.id);

    item.innerHTML = `
      <div class="profile-header-row">
        <span class="profile-name">
          <span style="font-size: 11px;">⚡</span> ${p.name}
        </span>
      </div>
      <div class="profile-flags-tag">${p.flags.join(" ")}</div>
    `;

    container.appendChild(item);
  });
}

function selectProfile(profileId) {
  currentProfileId = profileId;
  selectedCustomFlags.clear();

  const found = profiles.find(p => p.id === profileId);
  if (found) {
    found.flags.forEach(f => selectedCustomFlags.add(f));
  }

  // Update visual selection
  document.querySelectorAll(".profile-item").forEach((el, idx) => {
    el.classList.toggle("active", profiles[idx].id === profileId);
  });

  // Re-render flags grid to show active checked flags
  renderFlagsGrid(activeCategoryKey);
  updateCommandPreview();
}

function resetToCustom() {
  currentProfileId = null;
  document.querySelectorAll(".profile-item").forEach(el => el.classList.remove("active"));
  selectedCustomFlags.clear();
  renderFlagsGrid(activeCategoryKey);
  updateCommandPreview();
}

// 2. Render Flag Tabs & Grid in Column 2
function renderCategoryTabs() {
  const nav = document.getElementById("category-tabs-nav");
  nav.innerHTML = "";

  const keys = Object.keys(catalog);
  if (keys.length > 0 && !catalog[activeCategoryKey]) {
    activeCategoryKey = keys[0];
  }

  keys.forEach(catKey => {
    const btn = document.createElement("button");
    btn.className = `category-tab-btn ${catKey === activeCategoryKey ? "active" : ""}`;
    btn.textContent = categoryDisplayMap[catKey] || catKey;
    btn.onclick = () => {
      activeCategoryKey = catKey;
      document.querySelectorAll(".category-tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderFlagsGrid(catKey);
    };
    nav.appendChild(btn);
  });
}

function renderFlagsGrid(categoryKey) {
  const container = document.getElementById("flags-grid-container");
  container.innerHTML = "";

  const flags = catalog[categoryKey] || [];
  flags.forEach(item => {
    const isChecked = selectedCustomFlags.has(item.flag);
    const card = document.createElement("div");
    card.className = `flag-pill ${isChecked ? "checked" : ""}`;
    card.setAttribute("title", item.desc);
    
    // Toggle on card click
    card.onclick = (e) => {
      if (e.target.tagName !== "INPUT") {
        const cb = card.querySelector("input[type='checkbox']");
        cb.checked = !cb.checked;
        toggleFlag(item.flag, cb.checked);
      }
    };

    const left = document.createElement("div");
    left.className = "flag-pill-left";

    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.className = "flag-checkbox";
    cb.checked = isChecked;
    cb.onchange = (e) => toggleFlag(item.flag, e.target.checked);

    const titleWrap = document.createElement("div");
    titleWrap.innerHTML = `
      <span class="flag-title">${item.name}</span>
      <span class="flag-code">${item.flag}</span>
    `;

    left.appendChild(cb);
    left.appendChild(titleWrap);
    card.appendChild(left);

    if (item.requires_root) {
      const rootBadge = document.createElement("span");
      rootBadge.className = "flag-badge-root";
      rootBadge.textContent = "ROOT";
      card.appendChild(rootBadge);
    }

    container.appendChild(card);
  });

  updateActiveFlagsCount();
}

function toggleFlag(flag, isChecked) {
  if (isChecked) {
    selectedCustomFlags.add(flag);
  } else {
    selectedCustomFlags.delete(flag);
  }

  // Deselect active preset if custom modified
  if (currentProfileId) {
    const activeProf = profiles.find(p => p.id === currentProfileId);
    if (activeProf) {
      const match = activeProf.flags.length === selectedCustomFlags.size &&
                    activeProf.flags.every(f => selectedCustomFlags.has(f));
      if (!match) {
        currentProfileId = null;
        document.querySelectorAll(".profile-item").forEach(el => el.classList.remove("active"));
      }
    }
  }

  renderFlagsGrid(activeCategoryKey);
  updateCommandPreview();
}

function updateActiveFlagsCount() {
  const countEl = document.getElementById("active-flags-count");
  if (countEl) {
    countEl.textContent = `${selectedCustomFlags.size} flag${selectedCustomFlags.size === 1 ? "" : "s"} active`;
  }
}

// Engine Mode Switcher (Nmap Precision vs RustScan Turbo vs Angry IP Subnet)
function setEngineMode(mode) {
  currentEngineMode = mode;
  document.querySelectorAll(".engine-btn").forEach(btn => {
    btn.classList.toggle("active", btn.id === `engine-btn-${mode}`);
  });

  const matrixHeader = document.getElementById("matrix-header");
  const targetInput = document.getElementById("target-input");

  if (mode === "turbo") {
    if (matrixHeader) matrixHeader.querySelector("span").textContent = "Turbo Scanner Mode (RustScan Pipe)";
    if (targetInput.value.includes("/")) {
      targetInput.value = "127.0.0.1";
    }
  } else if (mode === "subnet") {
    if (matrixHeader) matrixHeader.querySelector("span").textContent = "Subnet Sweeper Mode (Angry IP)";
    if (!targetInput.value.includes("/")) {
      targetInput.value = "192.168.1.0/24";
    }
  } else {
    if (matrixHeader) matrixHeader.querySelector("span").textContent = "Flag Matrix (Nmap)";
  }

  updateCommandPreview();
}

// 3. Command Preview in Column 3
function updateCommandPreview() {
  const target = document.getElementById("target-input").value.trim() || "<target>";
  const flags = Array.from(selectedCustomFlags);
  
  let cmd = "";
  if (currentEngineMode === "turbo") {
    cmd = `rustscan -a ${target} -- -sV -T4 (Auto-Pipes open ports into Nmap)`;
  } else if (currentEngineMode === "subnet") {
    cmd = `ipscan ${target} (Angry IP Fast Multi-Threaded Subnet Sweep)`;
  } else {
    cmd = `nmap ${flags.join(" ")} ${target}`.trim();
  }

  document.getElementById("cmd-preview").textContent = cmd;
  updateActiveFlagsCount();
}

document.getElementById("target-input").addEventListener("input", updateCommandPreview);

function copyCommand() {
  const text = document.getElementById("cmd-preview").textContent;
  navigator.clipboard.writeText(text);
  const btn = document.querySelector(".btn-copy-cmd");
  const orig = btn.textContent;
  btn.textContent = "Copied!";
  setTimeout(() => {
    btn.textContent = orig;
  }, 1400);
}

// 4. Results Navigation Tabs
function switchResultTab(tabName) {
  document.getElementById("tab-btn-console").classList.toggle("active", tabName === "console");
  document.getElementById("tab-btn-inventory").classList.toggle("active", tabName === "inventory");
  document.getElementById("tab-btn-nse").classList.toggle("active", tabName === "nse");

  document.getElementById("view-console").classList.toggle("active", tabName === "console");
  document.getElementById("view-inventory").classList.toggle("active", tabName === "inventory");
  document.getElementById("view-nse").classList.toggle("active", tabName === "nse");

  if (tabName === "nse" && allNSEScripts.length === 0) {
    loadNSEScripts();
  }
}

// ---------------- NSE Script Browser Logic ----------------
let allNSEScripts = [];
let nseCategories = [];
let activeNSECategory = "all";
let selectedNSEScripts = new Set();

async function loadNSEScripts() {
  if (!window.pywebview || !window.pywebview.api || !window.pywebview.api.get_nse_data) return;

  try {
    const data = await window.pywebview.api.get_nse_data();
    allNSEScripts = data.scripts || [];
    nseCategories = data.categories || [];

    const badge = document.getElementById("nse-total-badge");
    if (badge) badge.textContent = `${allNSEScripts.length}`;

    renderNSECategories();
    renderNSEGrid();
  } catch (e) {
    console.error("Failed to load NSE scripts:", e);
  }
}

function renderNSECategories() {
  const container = document.getElementById("nse-cat-pills");
  if (!container) return;
  container.innerHTML = "";

  const allBtn = document.createElement("button");
  allBtn.className = `nse-cat-btn ${activeNSECategory === "all" ? "active" : ""}`;
  allBtn.textContent = `All (${allNSEScripts.length})`;
  allBtn.onclick = () => {
    activeNSECategory = "all";
    document.querySelectorAll(".nse-cat-btn").forEach(b => b.classList.remove("active"));
    allBtn.classList.add("active");
    renderNSEGrid();
  };
  container.appendChild(allBtn);

  // Common high-value pentest categories
  const priorityCats = ["default", "vuln", "exploit", "auth", "safe", "discovery", "brute", "malware"];
  const sortedCats = Array.from(new Set([...priorityCats, ...nseCategories]));

  sortedCats.forEach(cat => {
    const count = allNSEScripts.filter(s => s.categories.includes(cat)).length;
    if (count === 0) return;

    const btn = document.createElement("button");
    btn.className = `nse-cat-btn ${activeNSECategory === cat ? "active" : ""}`;
    btn.textContent = `${cat} (${count})`;
    btn.onclick = () => {
      activeNSECategory = cat;
      document.querySelectorAll(".nse-cat-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderNSEGrid();
    };
    container.appendChild(btn);
  });
}

function renderNSEGrid() {
  const grid = document.getElementById("nse-grid");
  if (!grid) return;
  grid.innerHTML = "";

  const searchTerm = (document.getElementById("nse-search-input")?.value || "").toLowerCase().trim();

  let filtered = allNSEScripts;
  if (activeNSECategory !== "all") {
    filtered = filtered.filter(s => s.categories.includes(activeNSECategory));
  }
  if (searchTerm) {
    filtered = filtered.filter(s => 
      s.name.toLowerCase().includes(searchTerm) || 
      s.categories.some(c => c.toLowerCase().includes(searchTerm))
    );
  }

  if (filtered.length === 0) {
    grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">No NSE scripts match your search criteria.</div>`;
    return;
  }

  // Cap rendering at first 120 items for high performance on low-end machines
  const toDisplay = filtered.slice(0, 120);

  toDisplay.forEach(script => {
    const isSelected = selectedNSEScripts.has(script.name);
    const card = document.createElement("div");
    card.className = `nse-card ${isSelected ? "selected" : ""}`;
    card.onclick = () => toggleNSEScript(script.name);

    const header = document.createElement("div");
    header.className = "nse-card-header";
    header.innerHTML = `
      <span class="nse-card-title">${script.name}</span>
      <input type="checkbox" ${isSelected ? "checked" : ""} style="accent-color: var(--accent-cyan); pointer-events: none;">
    `;
    card.appendChild(header);

    const catsRow = document.createElement("div");
    catsRow.className = "nse-card-cats";
    script.categories.forEach(c => {
      const tag = document.createElement("span");
      tag.className = `nse-cat-tag ${c}`;
      tag.textContent = c;
      catsRow.appendChild(tag);
    });
    card.appendChild(catsRow);

    grid.appendChild(card);
  });
}

function filterNSEScripts() {
  renderNSEGrid();
}

function toggleNSEScript(scriptName) {
  if (selectedNSEScripts.has(scriptName)) {
    selectedNSEScripts.delete(scriptName);
  } else {
    selectedNSEScripts.add(scriptName);
  }

  updateNSEFlagInCommand();
  renderNSEGrid();
}

function clearSelectedNSEScripts() {
  selectedNSEScripts.clear();
  updateNSEFlagInCommand();
  renderNSEGrid();
}

function updateNSEFlagInCommand() {
  // Remove existing --script= flags from selectedCustomFlags
  const toRemove = [];
  selectedCustomFlags.forEach(f => {
    if (f.startsWith("--script=")) toRemove.push(f);
  });
  toRemove.forEach(f => selectedCustomFlags.delete(f));

  const label = document.getElementById("nse-active-label");

  if (selectedNSEScripts.size > 0) {
    const scriptList = Array.from(selectedNSEScripts).join(",");
    const scriptFlag = `--script=${scriptList}`;
    selectedCustomFlags.add(scriptFlag);

    if (label) {
      label.textContent = `Selected: ${selectedNSEScripts.size} script(s) [${scriptList}]`;
    }
  } else {
    if (label) label.textContent = "No custom scripts selected";
  }

  updateCommandPreview();
}

// 5. Scan Execution
async function startScan() {
  if (isScanning || !window.pywebview) return;

  const target = document.getElementById("target-input").value.trim();
  if (!target) {
    alert("Please enter a target host or IP address.");
    return;
  }

  const flags = Array.from(selectedCustomFlags);

  isScanning = true;
  document.getElementById("btn-scan").style.display = "none";
  document.getElementById("btn-cancel").style.display = "inline-flex";

  const terminal = document.getElementById("terminal-output");
  let introMsg = `[+] Target: ${target}\n`;
  if (currentEngineMode === "turbo") {
    introMsg += `[+] Mode: 🚀 Turbo Recon (RustScan-Style async port sweep -> Nmap deep audit)\n\n`;
  } else if (currentEngineMode === "subnet") {
    introMsg += `[+] Mode: 🌐 Subnet Sweeper (Angry IP-Style concurrent host discovery)\n\n`;
  } else {
    introMsg += `[+] Command: nmap ${flags.join(" ")} ${target}\n\n`;
  }

  terminal.textContent = introMsg;
  switchResultTab("console");

  try {
    const res = await window.pywebview.api.start_scan(target, flags, currentEngineMode);
    if (!res.success) {
      terminal.textContent += `[-] Error: ${res.error}\n`;
      onScanFinished(-1, null);
    }
  } catch (e) {
    terminal.textContent += `[-] System exception: ${e}\n`;
    onScanFinished(-1, null);
  }
}

async function cancelScan() {
  if (!isScanning || !window.pywebview) return;
  await window.pywebview.api.cancel_scan();
  document.getElementById("terminal-output").textContent += "\n[!] Scan cancelled by operator.\n";
  onScanFinished(-1, null);
}

// Stream callbacks invoked by Python backend
window.onStreamLine = function(line) {
  const terminal = document.getElementById("terminal-output");
  terminal.textContent += line;
  terminal.scrollTop = terminal.scrollHeight;
};

window.onScanComplete = function(returnCode, parsedData) {
  onScanFinished(returnCode, parsedData);
};

function onScanFinished(returnCode, parsedData) {
  isScanning = false;
  document.getElementById("btn-scan").style.display = "inline-flex";
  document.getElementById("btn-cancel").style.display = "none";

  if (parsedData && parsedData.summary) {
    renderStructuredView(parsedData);
  }
}

function renderStructuredView(data) {
  document.getElementById("metric-total").textContent = data.summary.total_hosts || 0;
  document.getElementById("metric-open").textContent = data.summary.open_ports || 0;
  document.getElementById("metric-time").textContent = data.scan_info.start_str || "Completed";

  const container = document.getElementById("hosts-container");
  container.innerHTML = "";

  if (!data.hosts || data.hosts.length === 0) {
    container.innerHTML = `<div style="color: var(--text-muted); font-size: 12.5px; text-align: center; padding: 40px;">No open ports or responsive hosts recorded.</div>`;
    return;
  }

  data.hosts.forEach(host => {
    const card = document.createElement("div");
    card.className = "host-card";

    const header = document.createElement("div");
    header.className = "host-bar";
    const hostTitle = host.hostnames.length > 0 ? `${host.ip} (${host.hostnames.join(", ")})` : host.ip;
    header.innerHTML = `
      <div class="host-title">${hostTitle}</div>
      <div style="font-size: 11px; color: var(--text-muted);">State: <span style="color: var(--accent-emerald); font-weight: bold;">${host.state.toUpperCase()}</span></div>
    `;
    card.appendChild(header);

    if (host.ports && host.ports.length > 0) {
      const table = document.createElement("table");
      table.className = "ports-table";
      table.innerHTML = `
        <thead>
          <tr>
            <th>PORT</th>
            <th>STATE</th>
            <th>SERVICE</th>
            <th>VERSION</th>
            <th>REASON</th>
          </tr>
        </thead>
        <tbody>
          ${host.ports.map(p => `
            <tr>
              <td style="font-weight: 600;">${p.port}/${p.protocol.toUpperCase()}</td>
              <td><span class="port-open-tag">${p.state.toUpperCase()}</span></td>
              <td>${p.service || "-"}</td>
              <td style="color: #94a3b8;">${[p.product, p.version, p.extra_info].filter(Boolean).join(" ") || "-"}</td>
              <td style="color: var(--text-muted); font-size: 11px;">${p.reason || "-"}</td>
            </tr>
          `).join("")}
        </tbody>
      `;
      card.appendChild(table);
    } else {
      const empty = document.createElement("div");
      empty.style.padding = "12px 14px";
      empty.style.fontSize = "11.5px";
      empty.style.color = "var(--text-muted)";
      empty.textContent = "No open ports reported on this host.";
      card.appendChild(empty);
    }

    container.appendChild(card);
  });
}
