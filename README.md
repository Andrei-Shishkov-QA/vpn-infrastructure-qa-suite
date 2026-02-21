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
* **Infrastructure as Code Testing:** Automated audits of server configuration using `Testinfra`.
* **Disaster Recovery:** Automated backup validation and restoring strategies.
* **Network Analysis:** Latency and throughput monitoring (iperf3, MTR).
* **Security Compliance:** Hardening checks (Fail2ban, UFW, SSH Config).


## 🏗️ Architecture
The system operates on a **Shared-Nothing Architecture** across 4 geographical zones (NL, AT, RU, DE) to eliminate Single Points of Failure (SPOF).
* *See full details in [Network Topology](docs/NETWORK_TOPOLOGY.md).*


## 🛠️ Tech Stack
* **Language:** Python 3.10+ (Automation), Bash (Maintenance).
* **Testing Frameworks:** Pytest, Testinfra.
* **Network Tools:** iperf3, curl, MTR, nmap.
* **Protocols:** VLESS (Reality), Shadowsocks, XTLS.


## 📂 Repository Structure
```text
/docs           # Technical Documentation (Migration Report, Strategy, Topology)
/tests          # Automated Tests (Security, API, Infrastructure)
/scripts        # Maintenance & Utility Scripts (Backup, Benchmark)
/manual_tests   # Checklists for Client-Side UAT
```

## 📊 CI/CD & Allure Reporting

[![Tests & Security Audit](https://github.com/Andrei-Shishkov-QA/vpn-infrastructure-qa-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/Andrei-Shishkov-QA/vpn-infrastructure-qa-suite/actions)
[![Allure Report](https://img.shields.io/badge/Allure%20Report-Live%20Status-blue?logo=allure)](https://Andrei-Shishkov-QA.github.io/vpn-infrastructure-qa-suite/)
The project features a fully automated CI/CD pipeline via **GitHub Actions** with daily health checks and an interactive **Allure Report** hosted on GitHub Pages.

**🛡️ DevSecOps & Report Highlights:**
* **Zero-Leak Architecture:** Two-tier security sanitization (`conftest.py` hook + `jq` pipeline filter) automatically masks sensitive credentials (passwords, IPs) in the public Allure report.
* **Self-Healing Infrastructure:** Tests not only detect missing components (e.g., `fail2ban`) but automatically resolve dependencies and restart services on the fly.
* **Environment-Aware:** Tests automatically adapt to the execution environment (e.g., ICMP ping tests are gracefully `skipped` in GitHub Actions to comply with Azure firewall policies).
* **Expected Failures (`xfail`):** Tests verifying the disabling of root SSH access are marked as grey (`xfail`). This explicitly documents existing architectural constraints while keeping the pipeline green.

### 📈 Scaling: How to Add a New Server

The framework is designed to be easily scalable. To add a new VPN node to the continuous audit pipeline, follow these 3 steps:

**1. Add GitHub Secrets**
Go to your repository `Settings -> Secrets and variables -> Actions` and add the new credentials:
* `NODE_X_IP`
* `NODE_X_USER`
* `NODE_X_PASS`

**2. Update CI/CD Pipeline (`.github/workflows/ci.yml`)**
Map the new secrets to the environment variables in the `Create .env file from Secrets` step:
```yaml
echo "NODE_X_NAME=New-Location" >> .env
echo "NODE_X_IP=${{ secrets.NODE_X_IP }}" >> .env
echo "NODE_X_USER=${{ secrets.NODE_X_USER }}" >> .env
echo "NODE_X_PASS=${{ secrets.NODE_X_PASS }}" >> .env
```

### ⏱️ Automated Monitoring & Alerting

The CI/CD pipeline is configured for continuous infrastructure monitoring:
* **Scheduled Runs:** The test suite automatically executes daily at 03:00 AM (UTC) via GitHub Actions cron jobs to detect configuration drifts.
* **On-Push Execution:** Tests run automatically on every code push to ensure infrastructure integrity.
* **Instant Notifications:** If any test fails (e.g., server downtime or missing security packages), a Telegram bot instantly sends an alert with a direct link to the Allure report.

### 💻 Local Development & Reporting

To run tests and view the interactive graphs locally, Java and Allure CLI are required.

**Prerequisites (Windows):**
1. Install Java (OpenJDK 17): `winget install Microsoft.OpenJDK.17`
2. Install Node.js (via the official website).
3. Install Allure CLI: `npm install -g allure-commandline`

**Running the Suite:**
```bash
# Execute tests and save raw data to the temp_results directory
pytest --alluredir=temp_results

# Generate and launch the interactive HTML report in your default browser
allure serve temp_results
```

## 💻 System Requirements

### Control Node (Where you run tests)
* **OS:** Windows, macOS, or Linux
* **Python:** 3.10 or higher
* **Network:** Access to target servers via SSH (Port 22)

### Target Nodes (VPN Servers)
The automation scripts assume the following environment on the servers:
* **OS:** Ubuntu 20.04+ OR Debian 11+
* **Access:** SSH access with Sudo/Root privileges
* **Package Manager:** `apt` (checking for `ufw`, `fail2ban`, `iperf3`)
* **Init System:** `systemd`

### Network Performance (REQ-005)
*Corresponds to Test Case: NET-01*
Checks Latency (Ping) and Bandwidth (Download Speed from Global CDN).
```bash
pytest tests/test_network_perf.py -s
#Flag -s allows seeing real-time speed results in Mbps
```

## 📊 Infrastructure Status Monitor

### Infrastructure Monitoring (REQ-009)

The project includes a custom Python script for deep health checks of all connected nodes. Unlike simple ping tools, it logs into servers via SSH to inspect internal state.

**Capabilities:**
* **Smart Service Detection:** Automatically identifies if a node runs Docker (Outline/Remnawave) or Systemd (X-UI) and checks the corresponding process.
* **Resource Guard:** Warns on Low Disk (<15%) or High RAM (>90%).
* **Cross-Platform:** Works on Windows, Linux, and macOS.

**How to run:**
```bash
python scripts/monitor.py
```
Sample Output:
🖥️  NL-AMS [80.85.x.x]
  ├── ✅ PING            : Latency < 1s
  ├── ✅ PORT 443        : Open (HTTPS)
  ├── ❌ DISK            : 93% Used (CRITICAL)
  ├── ✅ DOCKER: OUTLINE : Active / Running

## 📦 Backup System (Disaster Recovery)

The project includes a tool to backup VPN configurations (3x-ui databases, Outline keys, Docker volumes) and send them to Telegram.

### 1. Setup Telegram Bot
1. Create a bot via **@BotFather** in Telegram -> Get `Bot Token`.
2. Find your Chat ID via **@userinfobot** -> Get `Chat ID`.
3. Add them to `.env`:
   ```ini
   TG_BOT_TOKEN=123456:ABC-DEF...
   TG_CHAT_ID=123456789
   ```
### 2. Configure Backup Paths
   Define which folders to backup for each server in .env.
   (Note: Use comma to separate multiple paths).
   ```ini
   NODE_1_BACKUP_PATHS=/etc/x-ui,/opt/outline/persisted-state
   NODE_4_BACKUP_PATHS=/var/lib/docker/volumes/remnawave_db_data/_data
   ```
### 3. Run Backup
```bash
python scripts/backup.py
```
Result: Archives will be saved in backups/ folder and sent to your Telegram chat.

## 🚀 Quick Start (Installation)

**1. Clone the repository:**
```bash
git clone https://github.com/Andrei-Shishkov-QA/vpn-infrastructure-qa-suite.git
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure Environment:**
Create a .env file with your node credentials (see .env.example).
Fill in your Real IP and Passwords in .env.


## 🛠️ How to Run Tests (Test Menu)
**4. Run Security Audit (Smoke Tests):**
```bash
pytest -m "smoke"
```

1. Security Audit & Smoke Tests (REQ-001...REQ-004)
Checks SSH availability, OS version, Firewall status, and Root login restrictions.

**5. Run Manual Validation (UAT):**
For UI/UX and client-side connectivity checks (REQ-007, REQ-008), follow the standardized checklist:
* 📄 **File:** [MOBILE_CLIENT_CHECKLIST.md](manual_tests/MOBILE_CLIENT_CHECKLIST.md)
* **Scope:** IP Leak tests, DPI bypass verification, and battery optimization checks for Android/iOS.

## 📈 Documentation Links
[Test Strategy](docs/TEST_STRATEGY.md) & RTM - What and how we test.
[Migration Report](docs/MIGRATION_REPORT.md) - Evolution from Single-Node to HA.
[Mobile Client](manual_tests/MOBILE_CLIENT_CHECKLIST.md) Checklist - User Acceptance Testing..
📄 **[Sample Test Case: Privacy Leak](manual_tests/TC-MAN-003_Privacy_Leak.md)** — Example of a detailed manual test artifact (Steps & Expected Results).