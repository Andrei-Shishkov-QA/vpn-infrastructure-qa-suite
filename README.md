# Network Infrastructure QA Suite

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Pytest](https://img.shields.io/badge/Testing-Pytest-orange?style=flat-square&logo=pytest)
![Platform](https://img.shields.io/badge/Platform-Linux-green?style=flat-square&logo=linux)
![Status](https://img.shields.io/badge/Status-Archived-lightgrey?style=flat-square)

> **Status: archived.** The servers were shut down in 2026, so the tests no longer run. The repository stays as a reference.

## About

A QA suite for my personal VPN service, used by friends and acquaintances (50+ users at its peak). The service ran on 4 Linux servers from 2023 to 2026.

The goal was simple: notice problems before users do — a stopped service, a closed port, a full disk, a broken backup.

## How it was built

The code was written with an AI coding assistant.

My part:
- idea and requirements: what to check and why;
- test design: checks, expected results, test strategy, traceability matrix;
- reviewing and testing the result on real servers;
- manual testing of mobile clients (Android, iOS);
- running the repository on GitHub: commits, CI setup, documentation.

## What is checked

| Area | How |
|---|---|
| Server settings | pytest + Testinfra: firewall is on, fail2ban is running, SSH settings, OS version |
| Auto-fix | if fail2ban is missing, the test installs and starts it |
| Network | speed (iperf3) and latency |
| Backups | server settings are archived and sent to Telegram; local copies older than 7 days are deleted |
| Health monitor | script checks disk, RAM, services and port 443 |
| Mobile clients | manual checklist and a test case for IP and DNS leaks |

Known limitation: root login over SSH stayed enabled on some servers. The test for it is marked `xfail`, so the problem is visible in every report instead of being hidden.

## CI and reports

- GitHub Actions ran the tests on every push and every night.
- Results went to an Allure report on GitHub Pages. Passwords and IP addresses were masked before publishing.
- If a test failed, a Telegram bot sent an alert with a link to the report.
- CI is disabled now, since the servers are shut down.

## Tech stack

Python · pytest · Testinfra · Paramiko · GitHub Actions · Allure · Telegram Bot API · Docker · systemd · UFW · fail2ban · iperf3 · Ubuntu / Debian

## Repository structure

```text
├── .github/workflows/   # CI: on push and nightly
├── docs/                # test strategy, migration report, network topology
├── manual_tests/        # mobile client checklist, sample test case
├── scripts/             # monitor.py (health check), backup.py (backups)
├── tests/               # pytest suite and fixtures (conftest.py)
└── inventory.py         # one list of servers, loaded from .env
```

## Documentation

- [Test Strategy](docs/TEST_STRATEGY.md) — what was tested, how, and the traceability matrix
- [Migration Report](docs/MIGRATION_REPORT.md) — from 1 server to 4
- [Network Topology](docs/NETWORK_TOPOLOGY.md) — servers and their roles
- [Mobile Client Checklist](manual_tests/MOBILE_CLIENT_CHECKLIST.md)
- [Sample Test Case: IP and DNS Leak](manual_tests/TC-MAN-003_Privacy_Leak.md)

## How to run (for reference)

```bash
git clone https://github.com/Andrei-Shishkov-QA/vpn-infrastructure-qa-suite.git
cd vpn-infrastructure-qa-suite
pip install -r requirements.txt
cp .env.example .env   # fill in your own servers and Telegram bot
pytest -m smoke        # quick availability check
pytest                 # full suite
```
