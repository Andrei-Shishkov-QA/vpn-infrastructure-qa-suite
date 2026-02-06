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
Automated Testing: Used for Server Infrastructure (Linux, Network, Security) to ensure stability.
Manual Testing: Used for Client-Side UX/UI (Mobile Apps) where automation is impractical.

| ISO Category        | Target Module         | Test Type               | Tools                      | Priority |
|:--------------------|:----------------------|:------------------------|:---------------------------|:---------|
| **Functional**      | Client Apps (UX)      | User Acceptance (UAT)   | **Manual Checklist**       | High     |
| **Functional**      | IP Masking Logic      | Public IP Check         | Bash (Curl + Proxy)        | Critical |
| **Security**        | OS Hardening (Linux)  | Security Audit          | Python + Testinfra         | Critical |
| **Performance**     | Bandwidth Capacity    | Load / Throughput Test  | Bash (Ping + MTR + iperf3) | High     |
| **Reliability**     | Data Storage          | Disaster Recovery       | Bash + Telegram API        | Critical |
| **Compatibility**   | External APIs         | Contract Testing        | Pytest                     | Medium   |


## 3. Test Layers (The Pyramid)
We combine automated infrastructure checks with manual client validation:
* **Manual Layer (UAT):** End-user validation of mobile apps (Android/iOS connectivity, UX).
* **L3 (E2E):** Disaster Recovery drills (Full cycle: Backup creation -> API Upload -> Restore validation).
* **L2 (Integration & Network):** External API contracts (Telegram) + Cross-node network performance (Ping, MTR, iperf3).
* **L1 (System):** Internal node configuration audit (`Testinfra` security checks) + Functional IP masking logic (`curl`).


## 4. Requirements Traceability Matrix (RTM)
Linking business requirements to technical implementations.

| ID          | Requirement                                       | Implementation (Test)                                     |
|:------------|:--------------------------------------------------|:----------------------------------------------------------|
| **REQ-000** | Infrastructure Availability (Smoke)               | `tests/test_security_audit.py::test_server_connectivity`  |
| **REQ-001** | SSH Root login must be disabled                   | `tests/test_audit_rules.py::test_ssh_root_login_disabled` |
| **REQ-002** | Firewall (UFW) must be active                     | `tests/test_audit_rules.py::test_firewall_status`         |
| **REQ-003** | Fail2Ban must protect port 22                     | `tests/test_audit_rules.py::test_fail2ban_status`         |
| **REQ-004** | OS Standardization (Ubuntu/Debian)                | `tests/test_audit_rules.py::test_os_version`              |
| **REQ-005** | Backup must be sent to off-site storage           | `backup_tg.sh` + JSON validation                          |
| **REQ-006** | Network Quality (Latency & Speed) monitored       | `latency_check.sh` + `iperf3`                             |
| **REQ-007** | User Real IP must be hidden (Privacy)             | `public_ip_check.sh` (curl)                               |
| **REQ-008** | Alert System (Telegram) must be reachable         | `test_api_contract.py`                                    |
| **REQ-009** | Mobile Clients must connect via vless/shadowsocks | `manual_tests/MOBILE_CLIENT_CHECKLIST.md`                 |


## 5. Execution Strategy (CI/CD & Monitoring)
We categorize tests by frequency to balance feedback speed with resource consumption.

| Frequency      | Trigger              | Test Scope                                                        | Goal                                                                                              |
|:---------------|:---------------------|:------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------|
| **Continuous** | Push / Pull Request  | **L1 (System)**: Linting, Config Syntax Check, `Testinfra` (Fast) | **"Fail Fast":** Block bad code from merging. Instant feedback (< 2 min).                         |
| **Scheduled**  | Nightly (Cron 03:00) | **L2 (Network) + L3 (E2E)**: `iperf3`, Disaster Recovery Drill    | **"Deep Check":** Run resource-heavy tests when load is low. Avoid ISP bans.                      |
| **On-Demand**  | Pre-Release / Manual | **Manual UAT**: Mobile Client Checklist                           | **"Quality Gate":** Final human verification before giving access to users.                       |
| **Monitoring** | Every 5-15 mins      | **Heartbeat**: Ping, HTTP Status, Latency Check                   | **"Observability":** Detect outages immediately and build historical stats (Peak hours analysis). |


## 6. Risk Analysis
* **Risk:** Telegram API downtime or Rate Limits.
    * **Context:** The disaster recovery alert system relies on a 3rd-party service (Telegram).
    * **Impact:** Critical backup failures might go unnoticed if the API is unreachable (Silent Failure).
    * **Mitigation:** Scripts implement retry logic for HTTP 429/5xx errors and fallback to local log retention.

* **Risk:** False Positives in Security Audit due to OS version diffs.
    * **Context:** Infrastructure nodes may run different versions of Linux (e.g., Ubuntu 22.04 vs 24.04).
    * **Impact:** Security tests might fail incorrectly (False Positive) if they rely on version-specific config syntax.
    * **Mitigation:** Tests utilize abstraction layers (Testinfra modules) rather than raw text parsing to verify configurations.

* **Risk:** Geographic environment discrepancy.
    * **Context:** QA testing is performed in a censorship-free region (Armenia), while end-users are in a restricted region (Russia).
    * **Impact:** "Connectivity" tests pass in QA but might fail in Prod due to ISP-level protocol blocking (DPI).
    * **Mitigation:** We rely on "Canary Testing" (feedback from a focused group of beta-testers in Russia) for protocol obfuscation checks.


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
    3.  **Intrusion Prevention (REQ-003):** Verifies `fail2ban` service is running to block brute-force attacks.
    4.  **Root Login (REQ-001):** Checks `/etc/ssh/sshd_config` to ensure `PermitRootLogin` is set to `no`.
* **Execution Command:** `pytest tests/test_audit_rules.py`