---
title: Severity Scoring and Escalation Matrix
category: Governance
id: SOC-GOV-SEV-001
---

# Severity Scoring and Escalation Matrix

## Scoring inputs
Impact (data, operations, safety), scope (one host vs domain), attacker control (blocked vs executing vs privileged), and confidence.

## Escalation
| Condition | Escalate to |
|---|---|
| Confirmed domain admin, DC, or backup control | Incident commander + AD owners |
| Ransomware encryption underway | IR lead, infrastructure, comms |
| Likely regulated data exfil | Legal / privacy |
| VIP compromise | Executive protection / comms |
| Public-facing exploit mass scanning with success | Vuln management + platform owners |

## Communication cadence
Critical: 15 minutes. High: 60 minutes. Medium: end of shift summary. Never post IOCs in public channels.

## Closure
Document root cause, remaining risk, detection gaps, and owners for corrective actions. Tune noisy alerts only after confirming they would not have hidden this case.
