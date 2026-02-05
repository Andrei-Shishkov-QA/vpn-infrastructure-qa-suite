# Manual Test Checklist: Mobile Client Connectivity
**Device:** Android 13 / iOS 17
**Client App:** v2rayNG / Streisand
**Tester:** [Your Name]

## Test Scenarios
| ID          | Title                             | Pre-Conditions            | Steps to Reproduce                                                      | Expected Result                                               | Status |
|:------------|:----------------------------------|:--------------------------|:------------------------------------------------------------------------|:--------------------------------------------------------------|:-------|
| **MAN-001** | **Import Config via Clipboard**   | App installed, Key copied | 1. Open App<br>2. Click "+" button<br>3. Select "Import from Clipboard" | Config appears in the list with correct server name           | ✅ PASS |
| **MAN-002** | **Connect to VPN**                | Config imported           | 1. Select Server<br>2. Click "Connect" (Big Button)<br>3. Wait 3 sec    | Status changes to "Connected", VPN icon appears in status bar | ✅ PASS |
| **MAN-003** | **Verify IP Change**              | VPN Connected             | 1. Open Browser<br>2. Go to `ipleak.net`                                | IP Country matches the Server location (e.g., Netherlands)    | ✅ PASS |
| **MAN-004** | **YouTube 4K Playback**           | VPN Connected             | 1. Open YouTube<br>2. Play 4K video                                     | Video plays without buffering > 10 sec                        | ❌ FAIL |
| **MAN-005** | **Reconnect after Airplane Mode** | VPN Connected             | 1. Turn ON Airplane Mode<br>2. Wait 5 sec<br>3. Turn OFF Airplane Mode  | VPN automatically reconnects within 10 sec                    | ⏳ TODO |