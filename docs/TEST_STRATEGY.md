# Test Strategy

> The project is archived: the servers were shut down in 2026. This document describes how the service was tested before that.

## 1. Goal

Keep a personal VPN service for friends and acquaintances (50+ users) available, secure and backed up — and find problems before users do.

The service ran on 4 servers:
- **NL-AMS** — main server (3x-ui + Outline);
- **AT-VIE** — backup server (3x-ui);
- **RU-MOW** — entry server (3x-ui);
- **DE-DUS** — test server for new settings (Remnawave).

## 2. What is tested and how

Two parts:
- **Automated** — servers: settings, security, network, backups.
- **Manual** — mobile apps, where automation is not practical.

| Type | What | How | Priority |
|:--|:--|:--|:--|
| Functional | Mobile apps: import, connect, reconnect | Manual checklist | High |
| Functional | Real IP is hidden | Manual check on ipleak.net | Critical |
| Security | Server settings: firewall, fail2ban, SSH | pytest + Testinfra | Critical |
| Performance | Network speed and latency | pytest + iperf3 | High |
| Reliability | Backups | backup script + Telegram | Critical |
| Integration | Telegram bot is reachable | pytest | Medium |

## 3. Test levels

- **Manual:** mobile apps on Android and iOS, IP and DNS leak check.
- **End-to-end:** full backup cycle: create an archive → send it to Telegram → keep a local copy.
- **Integration and network:** Telegram bot, network speed and latency.
- **System:** settings and services on each server.

## 4. Traceability matrix

| ID | Requirement | Where it is checked |
|:--|:--|:--|
| REQ-000 | Server is reachable over SSH (smoke) | `tests/test_security_audit.py::test_server_connectivity` |
| REQ-001 | Root login over SSH is disabled | `tests/test_audit_rules.py::test_ssh_root_login_disabled` |
| REQ-002 | Firewall (UFW) is on | `tests/test_audit_rules.py::test_firewall_status` |
| REQ-003 | fail2ban protects port 22 | `tests/test_audit_rules.py::test_fail2ban_status` |
| REQ-004 | Supported OS (Ubuntu / Debian) | `tests/test_audit_rules.py::test_os_version` |
| REQ-005 | Network speed and latency | `tests/test_network_perf.py` |
| REQ-006 | Backups | `scripts/backup.py` |
| REQ-007 | Real IP is hidden | `manual_tests/MOBILE_CLIENT_CHECKLIST.md`, `manual_tests/TC-MAN-003_Privacy_Leak.md` |
| REQ-008 | Mobile apps connect and reconnect | `manual_tests/MOBILE_CLIENT_CHECKLIST.md` |
| REQ-009 | Server health: disk, memory, services | `scripts/monitor.py` |
| REQ-010 | Telegram bot is reachable | `tests/test_telegram_api.py::test_telegram_connection` |

## 5. When tests run

| When | Trigger | What runs | Why |
|:--|:--|:--|:--|
| On every change | GitHub Actions: push or pull request | server settings checks | quick answer: did the change break anything |
| Every night | GitHub Actions at 06:00 (Yerevan time) | full suite + backups | heavy tests when users are not active |
| Before giving access to new users | manually | mobile app checklist | final check by a person |
| Any time | manually | `scripts/monitor.py` | quick look at server health |

## 6. Risks

**Telegram is unavailable.**
Alerts and backups go through Telegram. If it is down, a failed backup can go unnoticed.
→ The script retries the request, and backups are also kept locally in `/backups`.

**Different OS versions give false failures.**
Servers ran different versions of Ubuntu and Debian, so a check written for one version could fail on another.
→ Checks use Testinfra modules instead of reading config files as plain text.

**Tests from one place do not show the whole picture.**
Connection quality depends on the user's network, so a check that passes from my location can fail for a user.
→ A few users gave feedback after changes.

**Speed tests slow down the service.**
iperf3 fully loads the channel while it measures.
→ Speed tests run only at night or manually with a warning.

## Appendix: test cases

### SMK-01. Server is reachable (smoke)
- **Requirement:** REQ-000
- **Goal:** make sure the server is alive before running the longer checks.
- **More than a ping.** One check confirms five things:
  1. the server answers on the network;
  2. port 22 is open;
  3. the SSH service accepts connections;
  4. the login and password are correct;
  5. the server can run a command (`hostname`) and return the result.
- **Run:** `pytest -m smoke`

### SEC-01. Server security settings
- **Requirements:** REQ-001 – REQ-004
- **Checks:**
  1. OS is Ubuntu or Debian of a supported version.
  2. Firewall (UFW) is on.
  3. fail2ban is running. If it is missing, the test installs and starts it.
  4. Root login over SSH is disabled. Marked `xfail`: root login was still needed for CI, so the known problem stays visible in every report.
- **Run:** `pytest tests/test_audit_rules.py`

### NET-01. Network speed
- **Requirement:** REQ-005
- **Goal:** make sure the server is fast enough for several users watching video at the same time.
- **Checks:**
  1. speed with iperf3 against public test servers; threshold — more than 30 Mbit/s per server;
  2. latency (skipped in GitHub Actions, where ping is blocked).
- **Run:** `pytest tests/test_network_perf.py -s`

### OPS-01. Backups
- **Requirement:** REQ-006
- **Steps:**
  1. Take the list of folders for each server from `inventory.py`.
  2. Connect over SSH and pack them into a `.tar.gz` archive. Large folders that are not needed (for example, metrics) are skipped.
  3. Download the archive to `/backups` and send it to Telegram.
  4. Delete local copies older than 7 days.
- **Run:** `python scripts/backup.py`

### MAN-01. Mobile apps and IP leaks (manual)
- **Requirements:** REQ-007, REQ-008
- **Why manual:** a script can check that the server works, but not what happens on a real phone — for example, the phone killing the VPN app in the background to save battery.
- **Checks:**
  1. Real IP and DNS are hidden (ipleak.net, browserleaks.com). Steps — in `manual_tests/TC-MAN-003_Privacy_Leak.md`.
  2. Connection survives switching from Wi-Fi to mobile internet.
  3. If the VPN drops, traffic does not go around it.
- **Checklist:** `manual_tests/MOBILE_CLIENT_CHECKLIST.md`

### MON-01. Server health
- **Requirement:** REQ-009
- **Why this script:** simple uptime services only check that the server answers. They miss a full disk or a stopped container.
- **Checks:**
  1. the server answers, port 443 is open;
  2. disk: CRITICAL if less than 15% is free;
  3. memory: WARNING if more than 90% is used;
  4. the right services run on each server: Outline, x-ui or Remnawave.
- **Run:** `python scripts/monitor.py`
