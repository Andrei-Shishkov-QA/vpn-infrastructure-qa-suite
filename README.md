# Network Resilience & QA Suite

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Pytest](https://img.shields.io/badge/Testing-Pytest-orange?style=flat-square&logo=pytest)
![Platform](https://img.shields.io/badge/Platform-Linux%20(Ubuntu)-green?style=flat-square&logo=linux)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)
[![Tests & Security Audit](https://github.com/Andrei-Shishkov-QA/vpn-infrastructure-qa-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/Andrei-Shishkov-QA/vpn-infrastructure-qa-suite/actions)
[![Allure Report](https://img.shields.io/badge/Allure%20Report-Live%20Status-blue?logo=allure)](https://Andrei-Shishkov-QA.github.io/vpn-infrastructure-qa-suite/)

👉 **[Click here to view the Interactive Allure Report (with test results and graphs)](https://Andrei-Shishkov-QA.github.io/vpn-infrastructure-qa-suite/)**

An automated end-to-end testing, self-healing, and security audit framework for a distributed VPN server infrastructure.

## 📖 Project Overview
This repository contains the **Quality Assurance Framework** for a distributed high-availability network infrastructure serving 50+ active users. 

Unlike standard "setup scripts," this project focuses on **Stability, Security, and Performance Testing** of a live environment. It demonstrates the transition from manual administration to automated engineering practices.

**Key Features:**
* **Infrastructure as Code (IaC) Testing:** Automated audits of server configuration and system states using `Testinfra`.
* **Active Security & Self-Healing:** Hardening checks (UFW, SSH Config) with automatic dependency resolution and service restarts (e.g., recovering a stopped `fail2ban`).
* **DevSecOps & CI/CD:** Zero-leak reporting architecture that automatically masks sensitive credentials in Allure, fully integrated into GitHub Actions.
* **Network Performance Analysis:** Automated validation of latency constraints and CDN download speeds across different geographical zones.
* **Disaster Recovery & Monitoring:** Custom Python utilities for deep system health checks, backup validation, and instant Telegram alerting.

## 🏗️ Architecture
The system operates on a **Shared-Nothing Architecture** across 4 geographical zones (NL, AT, RU, DE) to eliminate Single Points of Failure (SPOF).
* *See full details in [Network Topology](docs/NETWORK_TOPOLOGY.md).*

## 🛠️ Tech Stack
* **Languages:** Python 3.10+ (Automation), Bash (Maintenance).
* **QA Frameworks:** Pytest, Pytest-Testinfra, Paramiko (SSH backend).
* **CI/CD & Reporting:** GitHub Actions, Allure Report, Telegram Bot API.
* **Infrastructure & Network:** Docker, Systemd, UFW, Fail2ban, iperf3, curl.
* **VPN Protocols:** VLESS (Reality), Shadowsocks, XTLS.

## 📂 Repository Structure
```text
├── .github/workflows/   # CI/CD pipelines (daily runs & on-push checks)
├── docs/                # Technical Docs (Migration Report, Strategy, Topology)
├── manual_tests/        # Checklists and test cases for Client-Side UAT
├── scripts/             # Python CLI tools (monitor.py, backup.py)
├── tests/               # Pytest suite (Security, Network, Backup validation)
├── conftest.py          # Pytest fixtures and Allure DevSecOps sanitization
└── inventory.py         # Dynamic SSOT (Single Source of Truth) for server nodes
```
---

## 🤖 CI/CD Automation Flow (Cheat Sheet)

This project utilizes GitHub Actions for continuous integration, testing, and disaster recovery. The pipeline behavior changes dynamically based on the trigger:

### 1. Code Push / Pull Request (Active Development)
* **Execution:** Runs the L1 Security & Connectivity test suite (`pytest`). Generates and publishes the Allure Report.
* **Alerting & Output:** Sends a silent "Canary" test file (`test_connection.txt`) to Telegram to verify API connectivity. 
* *Note: Server backups are NOT triggered during routine code pushes to avoid traffic overload.*

### 2. Scheduled Run (Nightly Cron - 06:00 AMT)
* **Execution:** Runs the full test suite + Triggers the Disaster Recovery script (`scripts/backup.py`). Generates the Allure Report.
* **Alerting & Output:** Silently delivers the `test_connection.txt` canary file AND the `.tar.gz` infrastructure backup archives directly to the Telegram bot. (Notifications are muted to prevent early morning disturbances).

### 3. CI/CD Failure (Incident Response)
* **Execution:** If any infrastructure test fails (e.g., server offline, firewall down), the pipeline fails but still forces the Allure Report generation (`if: always()`).
* **Alerting & Output:** Immediately sends a **CRITICAL loud alert (🚨)** to Telegram with a direct link to the generated Allure Report for rapid debugging.

---

## 🚀 Quick Start (Installation)

**1. Clone the repository:**
```bash
git clone https://github.com/Andrei-Shishkov-QA/vpn-infrastructure-qa-suite.git
cd vpn-infrastructure-qa-suite
```
**2. Install dependencies:**
```bash
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```
**3. Configure Environment:**
Create a .env file from the provided template:
```bash
cp .env.example .env
```
Open .env and fill in your real Server IPs, SSH Passwords, and Telegram Bot credentials. Note: You do not need to manually edit inventory.py; it dynamically loads your servers directly from the .env file.
**4. Run Automated Tests:**
```bash
# Run critical infrastructure checks (Smoke)
pytest -m smoke

# Run Network Performance with real-time CLI output in Mbps
pytest tests/test_network_perf.py -s

# Run the full suite and generate Allure raw data
pytest --alluredir=temp_results
```
**5. Run Utility Scripts:**
```bash
# Check live infrastructure health (Disk, RAM, Docker, VPN services)
python scripts/monitor.py

# Execute remote backups and send archives to Telegram
python scripts/backup.py
```
---

## 💻 System & Network Requirements

### Control Node (Execution Environment)
* **OS:** Windows, macOS, or Linux
* **Python:** 3.10 or higher
* **Network:** Access to target servers via SSH (Port 22)

### Target Nodes (VPN Servers)
* **OS:** Ubuntu 20.04+ OR Debian 11+
* **Access:** SSH access with Sudo/Root privileges
* **Init System:** `systemd`
* **Package Manager:** `apt` (required for the self-healing logic to automatically resolve missing dependencies like `fail2ban`).

### ⚠️ Network Resilience Constraints
The Testinfra framework relies on rapid SSH handshakes. To ensure reliable test execution, the executing network must meet the following criteria:

| Metric             | Optimal (Green) | Risky (Yellow) | Critical (Red) |
|:-------------------|:----------------|:---------------|:---------------|
| **Latency (Ping)** | < 150ms         | 150ms - 350ms  | > 400ms        |
| **Jitter**         | < 20ms          | 20ms - 100ms   | > 150ms        |
| **Packet Loss**    | 0%              | < 2%           | > 5%           |

> **Troubleshooting:** If tests randomly fail with `TimeoutError` during the SSH handshake, it indicates ISP throttling or high jitter on the executing network. This suite is optimized for stable CI/CD environments (like GitHub Actions). For local execution on unstable networks, use a Mobile Hotspot or adjust the connection parameters in `tests/conftest.py`.

---

## 📊 CI/CD & Allure Reporting

The project features a fully automated CI/CD pipeline via **GitHub Actions** with daily health checks and an interactive **Allure Report** hosted on GitHub Pages.

**🛡️ DevSecOps & Pipeline Highlights:**
* **Zero-Leak Architecture:** Two-tier security sanitization (`conftest.py` hook + `jq` pipeline filter) automatically masks sensitive credentials (passwords, IPs) in the public Allure report.
* **Self-Healing Infrastructure:** Tests not only detect missing components (e.g., `fail2ban`) but automatically resolve dependencies and restart services on the fly.
* **Environment-Aware:** Tests automatically adapt to the execution environment (e.g., ICMP ping tests are gracefully `skipped` in GitHub Actions to comply with Azure firewall policies).
* **Expected Failures (`xfail`):** Tests verifying the disabling of root SSH access are marked as grey (`xfail`). This explicitly documents existing architectural constraints while keeping the pipeline green.
* **Instant Alerting:** If any critical infrastructure test fails during the automated run, a Telegram bot instantly sends an alert with a direct link to the Allure report.

> **💡 Pro Tip for Contributors (`[skip ci]`):**
> If you are updating documentation or making non-code changes, append `[skip ci]` to your commit message (e.g., `docs: update README [skip ci]`). This tells GitHub Actions to skip the pipeline run, saving CI compute minutes.

### 📈 Scaling: How to Add a New Server
To add a new VPN node to the continuous audit pipeline:
1. Go to repository `Settings -> Secrets and variables -> Actions` and add credentials (`NODE_X_IP`, `NODE_X_USER`, `NODE_X_PASS`).
2. Update `.github/workflows/ci.yml` to map the new secrets to `.env`.
3. Add the node to `inventory.py`.

### 💻 Local Reporting
To view interactive graphs locally (requires Java and Node.js):
```bash
npm install -g allure-commandline
allure serve temp_results
```
---

## 🛠️ Core Infrastructure Tools

### 📊 Infrastructure Status Monitor (REQ-009)
The project includes a custom Python script for deep health checks. Unlike simple ping tools, it logs into servers via SSH to inspect internal state.

**Capabilities:**
* **Smart Service Detection:** Automatically identifies if a node runs Docker (Outline/Remnawave) or Systemd (X-UI).
* **Resource Guard:** Warns on Low Disk (<15%) or High RAM (>90%).

**Execution:**
```bash
python scripts/monitor.py
```
*Sample Output:*
```text
🖥️  NL-AMS [80.85.x.x]
  ├── ✅ PING            : Reachable
  ├── ✅ PORT 443        : Open (HTTPS/VPN)
  ├── ❌ DISK            : 93% Used (CRITICAL)
  ├── ✅ DOCKER: OUTLINE : Active
```
---
### 📦 Backup System (Disaster Recovery)

A utility to backup VPN configurations (x-ui databases, Outline keys, Docker volumes) directly to Telegram.

**Setup:**
1. Get Telegram Bot Token and Chat ID.
2. Add to `.env`: `TG_BOT_TOKEN=...` and `TG_CHAT_ID=...`
3. Define folders in `.env`: `NODE_1_BACKUP_PATHS=/etc/x-ui,/opt/outline`

**Execution:**
```bash
python scripts/backup.py
```
*Archives are saved locally in `/backups` and securely sent to Telegram.*

---
## 📈 Documentation & Manual Tests

While automated tests cover the infrastructure layer, client-side validation is documented in our manual test artifacts.

**Architecture & Strategy:**
* 📄 **[QA Test Strategy & RTM](docs/TEST_STRATEGY.md)** — What and how we test (Requirements Traceability Matrix).
* 📄 **[Migration Report](docs/MIGRATION_REPORT.md)** — Evolution from a Single-Node to an HA Architecture.
* 📄 **[Network Topology](docs/NETWORK_TOPOLOGY.md)** — Visual mapping of the Shared-Nothing setup.

**Manual UAT (User Acceptance Testing):**
* 📱 **[Mobile Client Checklist](manual_tests/MOBILE_CLIENT_CHECKLIST.md)** — Step-by-step checklist for IP Leak, DPI bypass, and battery optimization (Android/iOS).
* 🐛 **[Sample Test Case: Privacy Leak](manual_tests/TC-MAN-003_Privacy_Leak.md)** — Example of a detailed manual test artifact with Expected Results.