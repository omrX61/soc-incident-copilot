---
title: SOC Log Source Coverage Notes
category: Detection Engineering
id: SOC-DE-LOG-001
---

# SOC Log Source Coverage Notes

Use this when the copilot or an analyst needs to know where evidence should live.

| Scenario | Primary sources | Secondary |
|---|---|---|
| Phishing click | Mail gateway, URL rewrite, IdP | Endpoint browser history, proxy |
| Malicious macro | EDR process tree, email | Sysmon 1/3/11, AMSI |
| Password spray | IdP / AD FS / VPN | Firewall source ASN |
| Ransomware | EDR, file server audit, backup | Windows 4658/4663, VSS |
| C2 | Proxy, DNS, EDR network | Firewall, TLS telemetry |
| Privileged abuse | IdP audit, PIM, 4672 | GPO change, DC logs |

If a required source is missing, state the gap in the case notes instead of inferring what the log would have shown.
