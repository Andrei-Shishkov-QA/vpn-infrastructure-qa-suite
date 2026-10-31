# Migration Report: From 1 Server to 4

> The project is archived: the servers were shut down in 2026. This report describes how the service worked before that.

## 1. Summary

The VPN service for friends and acquaintances started in 2023 on a single server. In January 2025 it moved to 4 independent servers, and automated checks were added. The number of users grew from about 15 to 50+.

## 2. Before: one server (mid 2023 – late 2024)

- One server in the Netherlands with Outline.
- Managed through the Outline Manager app and manual SSH commands.
- No testing: problems were found from user messages ("the internet is down").
- If the server went down, all users lost access at once.
- Server settings were never checked automatically.
- Only one person knew how everything was set up.

## 3. After: four servers (January 2025 – 2026)

- 4 servers: Netherlands, Austria, Russia, Germany. The German one was used for testing new settings.
- One list of servers in `inventory.py`; settings tracked in Git.
- Automated checks:
  - pytest + Testinfra — server settings and security;
  - iperf3 — network speed;
  - `backup.py` — backups sent to Telegram.
- Manual checks: a checklist for mobile apps and a test for IP and DNS leaks.
- Monitoring: `monitor.py` checked disk, memory and services; alerts went to Telegram.
- If one server failed, users were switched to another one manually.

Remaining risk: some networks block VPN connections. This was checked with feedback from users.

## 4. Result

| | Before | After |
|---|---|---|
| Servers | 1 | 4 |
| If a server fails | all users lose access | users switch to another server |
| Testing | none | automated checks + manual checklist |
| Problems found | from user messages | from alerts in Telegram |
| Users | ~15 | 50+ |

## 5. Lessons learned

- **A newer protocol is not always better.** Sometimes a newer connection protocol stopped working while an older one still worked. So several protocols were kept at the same time.
- **Testing from one place is not enough.** Connection quality depends on the user's network, so checks from my location did not show the whole picture. Feedback from a few users was needed.
- **Heavy tests need the right time.** Speed tests (iperf3) fully load the channel, so they ran only at night, when users were not active.

## 6. What was planned next

- Prometheus + Grafana for graphs and history of server metrics.
- SSH keys instead of passwords.
