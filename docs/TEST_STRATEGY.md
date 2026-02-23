# Test Strategy: Distributed VPN Infrastructure

## 1. Introduction
Objective: The primary goal of this project is to guarantee High Availability (HA), security compliance, and disaster recovery for a commercial VPN network serving 50+ clients.

This document defines the Quality Assurance strategy for a distributed VPN network consisting of 4 nodes:
* **NL-AMS (Prod):** 3x-ui + Outline (Primary)
* **AT-VIE (Prod):** 3x-ui (Failover)
* **RU-MOW (Prod):** 3x-ui (Transit/Entry)
* **DE-DUS (Staging):** Remnawave (Experimental)


## 2. Scope of Testing
We follow a Hybrid QA Strategy:
* **Automated Testing:** Used for Server Infrastructure (Linux, Network, Security) to ensure stability.
* **Manual Testing:** Used for Client-Side UX/UI (Mobile Apps) where automation is impractical.

| ISO Category         | Target Module         | Test Type               | Tools                         | Priority |
|:---------------------|:----------------------|:------------------------|:------------------------------|:---------|
| **Functional**       | Client Apps (UX)      | User Acceptance (UAT)   | **Manual Checklist**          | High     |
| **Functional**       | IP Masking Logic      | Public IP Check         | Web Tools (whoer.net)         | Critical |
| **Security**         | OS Hardening (Linux)  | Security Audit          | Python + Testinfra            | Critical |
| **Performance**      | Bandwidth Capacity    | Load / Throughput Test  | Python + iperf3               | High     |
| **Reliability**      | Data Storage          | Disaster Recovery       | Python + Telegram API         | Critical |
| **Compatibility**    | External APIs         | Contract Testing        | Pytest                        | Medium   |

## 3. Test Layers (The Pyramid)
We combine automated infrastructure checks with manual client validation:
* **Manual Layer (UAT):** End-user validation of mobile apps (Android/iOS connectivity, UX) and functional IP masking logic.
* **L3 (E2E & Operations):** Disaster Recovery drills (Full cycle: Backup creation -> Telegram API Upload -> Local Retention).
* **L2 (Integration & Network):** External API contracts (Telegram) + Cross-node network performance (`iperf3` and latency checks).
* **L1 (System):** Internal node configuration audit (`Testinfra` security checks) and service health states (Docker/Systemd).


## 4. Requirements Traceability Matrix (RTM)
Linking business requirements to technical implementations.

| ID          | Requirement                                     | Implementation (Test / Tool)                                   |
|:------------|:------------------------------------------------|:---------------------------------------------------------------|
| **REQ-000** | Infrastructure Availability (Smoke)             | `tests/test_security_audit.py::test_server_connectivity`       |
| **REQ-001** | SSH Root login must be disabled                 | `tests/test_audit_rules.py::test_ssh_root_login_disabled`      |
| **REQ-002** | Firewall (UFW) must be active                   | `tests/test_audit_rules.py::test_firewall_status`              |
| **REQ-003** | Fail2Ban must protect port 22                   | `tests/test_audit_rules.py::test_fail2ban_status`              |
| **REQ-004** | OS Standardization (Ubuntu/Debian)              | `tests/test_audit_rules.py::test_os_version`                   |
| **REQ-005** | Network Performance (Latency, Loss, Bandwidth)  | `tests/test_network_perf.py` (`iperf3`)                        |
| **REQ-006** | Disaster Recovery (Backup)                      | `scripts/backup.py` (Automated Script)                         |
| **REQ-007** | Privacy (Hide Real IP)                          | `/manual_tests/MOBILE_CLIENT_CHECKLIST.md` (Manual)            |
| **REQ-008** | Mobile Connectivity                             | `/manual_tests/MOBILE_CLIENT_CHECKLIST.md` (Manual)            |
| **REQ-009** | Infrastructure Health Check (Console Monitor)   | `scripts/monitor.py` (Automated Script)                        |


## 5. Execution Strategy (CI/CD & Monitoring)
We categorize tests by frequency to balance feedback speed with resource consumption.

| Frequency       | Trigger / Pipeline          | Test Scope                                                          | Goal                                                                                              |
|:----------------|:----------------------------|:--------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------|
| **Continuous**  | GitHub Actions (Push / PR)  | **L1 (System)**: Linting, Config Syntax Check, `Testinfra` (Fast)   | **"Fail Fast":** Block bad code from merging. Instant feedback (< 2 min).                         |
| **Scheduled**   | GitHub Actions (Cron 03:00) | **L2 (Network) + L3 (E2E)**: `iperf3` bandwidth, `backup.py` drill  | **"Deep Check":** Run resource-heavy tests when user load is low. Avoid ISP bans.                 |
| **On-Demand**   | Pre-Release / Manual        | **Manual UAT**: Mobile Client Checklist                             | **"Quality Gate":** Final human verification before giving access to users.                       |
| **Monitoring**  | Cron (Every 5-15 mins)      | **Heartbeat**: `scripts/monitor.py` (Disk, RAM, Services, Port 443) | **"Observability":** Detect outages immediately and build historical stats (Peak hours analysis). |


## 6. Risk Analysis

* **Risk: Telegram API downtime or Rate Limits.**
    * **Context:** The disaster recovery alert system relies on a 3rd-party service (Telegram).
    * **Impact:** Critical backup failures might go unnoticed if the API is unreachable (Silent Failure).
    * **Mitigation:** Scripts implement retry logic for HTTP 429/5xx errors and fallback to local log retention in the `/backups` directory.

* **Risk: False Positives in Security Audit due to OS version diffs.**
    * **Context:** Infrastructure nodes may run different versions of Linux (e.g., Ubuntu 22.04 vs 24.04, or Debian 11).
    * **Impact:** Security tests might fail incorrectly (False Positive) if they rely on version-specific bash config syntax.
    * **Mitigation:** Tests utilize abstraction layers (`Testinfra` modules) rather than raw text parsing to verify system states.

* **Risk: Geographic environment discrepancy.**
    * **Context:** QA testing is performed in a censorship-free region (Armenia), while end-users are in a restricted region (Russia).
    * **Impact:** "Connectivity" tests pass in QA pipelines but might fail in Prod due to ISP-level protocol blocking (DPI).
    * **Mitigation:** We rely on "Canary Testing" (feedback from a focused group of beta-testers in the restricted region) for protocol obfuscation checks.

* **Risk: Network Performance Degradation during Testing.**
    * **Context:** Bandwidth capacity tests (`iperf3`) fully saturate the network link to measure maximum throughput.
    * **Impact:** Running these tests during peak hours will cause severe lag for connected VPN users.
    * **Mitigation:** Bandwidth tests are strictly scheduled for nightly CI runs (Cron 03:00) or executed manually with prior warning.

## Appendix A: Test Case Catalog (Detailed Logic)

### SMK-01: Server Connectivity (Smoke Test)
* **Linked Requirement:** REQ-000
* **Goal:** Verify that the server is alive and reachable via SSH before running expensive security audits.
* **Why this is not just a "ping":**
    1.  **Network Layer:** Validates IP reachability.
    2.  **Transport Layer:** Validates that Port 22 is open and accepting TCP connections.
    3.  **Application Layer (SSH):** Validates that the SSH Daemon is running and accepts the handshake.
    4.  **Auth Layer:** Validates that credentials (`root` + password/key) are correct.
    5.  **Execution:** Validates that the OS can fork a process (`hostname`) and return `stdout`.
* **Execution Command:** `pytest -m "smoke"`

### SEC-01: Deep Security Audit
* **Linked Requirements:** REQ-001, REQ-002, REQ-003, REQ-004
* **Goal:** Enforce security best practices across all infrastructure nodes.
* **Checks Performed:**
    1.  **OS Consistency (REQ-004):** Ensures nodes run supported OS versions (Ubuntu/Debian) to prevent "configuration drift".
    2.  **Firewall Status (REQ-002):**
        * *Ubuntu:* Verifies `ufw` is active.
        * *Debian:* Verifies `ufw` status is active (command-based check).
    3.  **Intrusion Prevention & Self-Healing (REQ-003):** Verifies `fail2ban` service is running to block brute-force attacks. If missing, the framework attempts to automatically install and start it.
    4.  **Root Login (REQ-001):** Checks `/etc/ssh/sshd_config` to ensure `PermitRootLogin` is set to `no`. (Currently tracked as an expected architectural failure via `@pytest.mark.xfail`).
* **Execution Command:** `pytest tests/test_audit_rules.py`

### NET-01: Network Quality Assessment (Performance)
* **Linked Requirement:** REQ-005
* **Goal:** Verify maximum server bandwidth capacity to ensure acceptable streaming quality (4K video) for concurrent users.
* **Checks Performed:**
    1.  **Bandwidth (`iperf3`):** The framework performs a TCP throughput test against public speedtest servers to measure real-world network capacity.
        * *Why iperf3?* It provides highly accurate socket-level metrics compared to simple HTTP file downloads (curl), bypassing CDN caching anomalies.
        * *Thresholds:* > 30 Mbps per node (Guarantees stable multi-user 4K streaming).
    2.  **Privilege Handling:** The test automatically detects if `sudo` is required (Smart Host Logic) to support both Root and Non-Root server environments dynamically.
* **Execution Command:** `pytest tests/test_network_perf.py -s`

### OPS-01: Disaster Recovery (Backup System)
* **Linked Requirement:** REQ-006
* **Goal:** Prevent data loss by automatically archiving critical server configurations, keys, and databases.
* **Mechanism:**
    1.  **Discovery:** Script dynamically reads `inventory.py` to find target paths per node (supports 3x-ui, Outline, Docker Volumes).
    2.  **Archiving:** Connects via SSH and creates a `.tar.gz` archive. Implements strict filtering (e.g., `--exclude='*/prometheus'`) to omit non-essential metrics and save space.
    3.  **Extraction:** Downloads the archive locally to the `/backups` directory and transmits it securely to the Admin via the Telegram API.
    4.  **Retention Policy:** Automatically purges local backup files older than **7 days** to prevent local disk overflow.
* **Implementation & Execution:** `python scripts/backup.py`

### MAN-01: Client Privacy & Connectivity (Manual)
* **Linked Requirements:** REQ-007, REQ-008
* **Goal:** Verify the "Last Mile" delivery — ensuring the end-user actually receives the security and connectivity promised by the infrastructure.
* **Why Manual?** Automated scripts can verify the server is *sending* packets, but cannot verify if a specific ISP in a restricted region is *dropping* them via DPI (Deep Packet Inspection), or if the mobile OS is killing the VPN background process to save battery.
* **Checks Performed:**
    1.  **Leak Protection (REQ-007):**
        * *Detailed Steps:* See `manual_tests/TC-MAN-003_Privacy_Leak.md`
        * *DNS Leak:* Verifies that DNS requests are resolved by the VPN server, not the local ISP.
        * *WebRTC Leak:* Ensures the browser doesn't reveal the real local IP via STUN requests.
        * *Tools:* whoer.net, browserleaks.com.
    2.  **Resilience (REQ-008):**
        * *Network Switch:* Verifies session persistence when switching from Wi-Fi to 4G/LTE (Handover).
        * *Kill Switch:* Verifies internet traffic is blocked if the VPN connection drops unexpectedly.
* **Execution Reference:** See `manual_tests/MOBILE_CLIENT_CHECKLIST.md`

### MON-01: Infrastructure Health Check (Console Monitor)
* **Linked Requirement:** REQ-009
* **Goal:** Provide a deep, instant snapshot of server health to detect internal issues (Disk/RAM) before they cause outages.
* **Why this script?** Standard uptime checkers (like UptimeRobot) only check external Ping. They miss internal "Soft Failures" like full disks or zombie Docker containers that have stopped routing traffic.
* **Logic (Console Dashboard):**
    1.  **Connectivity:** Verifies ICMP Ping + TCP Port 443 (HTTPS) reachability.
    2.  **Resources (Thresholds):**
        * *Disk:* Flags status as **CRITICAL** if free space < 15%.
        * *RAM:* Flags status as **WARNING** if usage > 90%.
    3.  **Service Awareness:**
        * Dynamically scans `inventory.py` to identify required services per node.
        * *Outline Nodes:* Verifies Docker container `shadowbox` is running.
        * *X-UI Nodes:* Verifies Systemd service `x-ui` is active.
        * *Remnawave Nodes:* Verifies Docker container `remnawave` is running.
* **Execution:** `python scripts/monitor.py` (Manual run by Admin or via CI pipeline).