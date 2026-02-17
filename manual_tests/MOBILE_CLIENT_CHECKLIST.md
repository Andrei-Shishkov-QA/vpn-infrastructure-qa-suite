# 📱 Manual Test Checklist: Mobile Client & Privacy

**Target Requirements:** REQ-007 (Privacy), REQ-008 (Mobile Connectivity)
**Device:** Android 13 / iOS 17
**Client App:** V2Box (iOS) / v2rayNG (Android)
**Tester:** Shishkov Andrei
**Last Run Date:** 2026-02-17

## Test Scenarios & Results

| ID         | Title                           | Pre-Conditions            | Steps to Reproduce                                                                    | Expected Result                                                                      | Status      |
|:-----------|:--------------------------------|:--------------------------|:--------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|:------------|
| **MAN-01** | **Import Config**               | App installed, Key copied | 1. Open App<br>2. Click "+"<br>3. Select "Import from Clipboard"                      | Config appears in the list with correct server name (e.g., NL-AMS).                  | ✅ PASS      |
| **MAN-02** | **Connect VPN**                 | Config imported           | 1. Select Server<br>2. Click "Connect" button<br>3. Wait 3 sec                        | Status changes to "Connected", VPN icon appears in status bar.                       | ✅ PASS      |
| **MAN-03** | **Privacy Leak Test (REQ-007)** | VPN Connected (NL-AMS)    | 1. Open Browser<br>2. Go to `ipleak.net`                                              | **IP Location:** Netherlands.<br>**DNS Address:** Matches VPN (NOT your local ISP).  | ✅ PASS      |
| **MAN-04** | **YouTube 4K Test**             | VPN Connected             | 1. Open YouTube app<br>2. Play 4K video                                               | Video plays immediately without buffering > 10 sec.                                  | ⚠️ UNSTABLE |
| **MAN-05** | **Stability (Airplane Mode)**   | VPN Connected             | 1. Turn ON Airplane Mode (Loss of network)<br>2. Wait 5s<br>3. Turn OFF Airplane Mode | VPN app automatically reconnects within 10 sec after network is back.                | ⏳ TODO      |
| **MAN-06** | **Geo-Blocking Test (RU)**      | Connected to **RU-MOW**   | 1. Open Instagram or LinkedIn app                                                     | App fails to load content (Confirmed routing via Russia).                            | ✅ PASS      |