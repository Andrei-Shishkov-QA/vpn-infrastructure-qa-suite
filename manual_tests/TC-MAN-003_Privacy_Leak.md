# 🧪 Test Case: VPN Privacy & DNS Leak Verification

| **ID**            | **TC-MAN-003**                                                                                                                                                |
|:------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Title**         | Verification of Real IP masking and DNS Leak protection                                                                                                       |
| **Priority**      | **Critical (P1)**                                                                                                                                             |
| **Type**          | Security / Privacy                                                                                                                                            |
| **Prerequisites** | 1. Mobile Device (iOS/Android) with V2Box/v2rayNG installed.<br>2. Valid VLESS subscription key imported.<br>3. Internet connection is active (Wi-Fi or LTE). |
| **Test Data**     | **Target URL:** `https://ipleak.net`<br>**Expected Country:** Netherlands (NL-AMS)                                                                            |

## 📝 Test Steps

| #     | Action (Step)                                           | Expected Result                                                                                                      | Actual Result |
|:------|:--------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------|:--------------|
| **1** | Launch the VPN Client App.                              | App launches, main screen is visible.                                                                                |               |
| **2** | Select the **"NL-AMS"** server from the list.           | Server is selected.                                                                                                  |               |
| **3** | Tap the **"Connect"** toggle/button.                    | 1. Toggle turns Green/Active.<br>2. "VPN" icon appears in the Status Bar.<br>3. Status changes to "Connected".       |               |
| **4** | Open a web browser (Chrome/Safari) in "Incognito" mode. | Browser opens.                                                                                                       |               |
| **5** | Navigate to `https://ipleak.net`.                       | Website loads successfully.                                                                                          |               |
| **6** | Scroll to **"Your IP info"** section.                   | The displayed IP address matches the VPN Server IP (Start with `80.85...`). **It must NOT show your local ISP IP.**  |               |
| **7** | Scroll to **"DNS Addresses"** section.                  | 1. 0 servers found from your local ISP (e.g., Ucom/Beeline).<br>2. DNS Servers match the VPN location (Netherlands). |               |

## 🐛 Post-Conditions
* Disconnect VPN.
* Close the browser.

## 📊 Execution History
* **Date:** 2026-02-17
* **Tester:** Shishkov Andrei
* **Status:** ✅ **PASS**
* **Comments:** IP was masked successfully. No WebRTC leaks detected.