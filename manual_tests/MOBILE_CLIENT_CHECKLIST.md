# Manual Checklist: Mobile Client and Privacy

**Requirements:** REQ-007 (real IP is hidden), REQ-008 (mobile apps connect and reconnect)
**Devices:** Android 13 / iOS 17
**Apps:** V2Box (iOS) / v2rayNG (Android)
**Tester:** Andrei Shishkov
**Last run:** 2026-02-17

| ID | Check | Preconditions | Steps | Expected result | Status |
|:--|:--|:--|:--|:--|:--|
| **MAN-01** | Import settings | App installed, key copied | 1. Open the app<br>2. Tap "+"<br>3. Choose "Import from Clipboard" | The server appears in the list with the right name (for example, NL-AMS) | ✅ PASS |
| **MAN-02** | Connect | Settings imported | 1. Select the server<br>2. Tap "Connect"<br>3. Wait 3 seconds | Status is "Connected", the VPN icon is in the status bar | ✅ PASS |
| **MAN-03** | Real IP is hidden (REQ-007) | Connected to NL-AMS | 1. Open a browser<br>2. Go to `ipleak.net` | Location: Netherlands. DNS matches the server, not the local internet provider | ✅ PASS |
| **MAN-04** | Video in 4K | Connected | 1. Open YouTube<br>2. Play a 4K video | Video starts without buffering longer than 10 seconds | ⚠️ UNSTABLE |
| **MAN-05** | Reconnect after network loss | Connected | 1. Turn on Airplane mode<br>2. Wait 5 seconds<br>3. Turn it off | The app reconnects within 10 seconds | ⏳ TODO |
