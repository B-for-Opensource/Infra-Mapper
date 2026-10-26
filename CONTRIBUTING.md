# Contributing to Nmap Studio

Thank you for your interest in contributing to **Nmap Studio**! We welcome contributions from developers, security researchers, penetration testers, and network engineers.

---

## Code of Conduct

Please be respectful, constructive, and adhere to standard open-source community standards.

---

## Development Setup

1. **Fork and Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/nmap-studio.git
   cd nmap-studio
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Environment**:
   ```bash
   python main.py --check-env
   ```

5. **Launch Application in Debug Mode**:
   ```bash
   python main.py --debug
   ```

---

## Architecture Guidelines

1. **Non-Blocking UI**:
   Never perform synchronous disk I/O, heavy subprocess calls, or `psutil` blocking waits inside the main UI thread. Use background worker threads and asynchronous streams.

2. **Transparent CLI**:
   Nmap Studio is a transparent wrapper. New scanning flags or presets must always generate and expose the exact CLI command to the user.

3. **Cross-Platform Compatibility**:
   Ensure any OS-specific logic (paths, drivers, elevation) is abstracted within `platform_adapters/` (`windows.py`, `posix.py`).

---

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-new-feature`
2. Commit your changes with clear messages.
3. Test locally on your OS with `python main.py --check-env`.
4. Open a Pull Request with a clear description and screenshot/GIF of UI changes.
