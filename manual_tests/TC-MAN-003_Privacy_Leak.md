# Test Case: Real IP and DNS Leak

| | |
|:--|:--|
| **ID** | TC-MAN-003 |
| **Title** | Real IP and DNS servers are hidden when the VPN is on |
| **Priority** | Critical (P1) |
| **Type** | Security / Privacy |
| **Preconditions** | 1. Phone (iOS or Android) with V2Box or v2rayNG.<br>2. A valid key is imported.<br>3. Internet works (Wi-Fi or mobile). |
| **Test data** | URL: `https://ipleak.net`<br>Expected country: Netherlands (NL-AMS) |

## Steps

| # | Action | Expected result | Actual result |
|:--|:--|:--|:--|
| 1 | Open the VPN app | The main screen opens | |
| 2 | Select the **NL-AMS** server | The server is selected | |
| 3 | Tap **Connect** | 1. The switch turns green<br>2. The VPN icon is in the status bar<br>3. Status is "Connected" | |
| 4 | Open a browser (Chrome or Safari) in incognito mode | The browser opens | |
| 5 | Go to `https://ipleak.net` | The page loads | |
| 6 | Find the **"Your IP info"** section | The IP matches the VPN server. The IP from the local internet provider is **not** shown | |
| 7 | Find the **"DNS Addresses"** section | 1. No DNS servers of the local provider (for example, Ucom or Beeline)<br>2. DNS servers are in the Netherlands | |

## After the test

- Turn off the VPN.
- Close the browser.

## Run history

- **Date:** 2026-02-17
- **Tester:** Andrei Shishkov
- **Status:** ✅ PASS
- **Comment:** IP is hidden, no WebRTC leaks found.
