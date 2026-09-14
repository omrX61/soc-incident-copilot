---
title: SOC Incident Handling Standard Operating Procedure
category: Incident Response
id: SOC-SOP-001
---

# SOC Incident Handling Standard Operating Procedure

## Purpose
This SOP aligns local SOC practice with NIST SP 800-61 style incident handling: preparation, detection and analysis, containment/eradication/recovery, and post-incident activity. It is written for Tier 1 and Tier 2 analysts working from the local copilot.

## Severity model
| Severity | Examples | Response clock |
|---|---|---|
| Critical | Active ransomware, domain admin compromise, confirmed data exfil of regulated data | Immediate incident commander, 15-minute updates |
| High | Confirmed account takeover, C2 on a server, public-facing exploit in use | 1 hour containment target |
| Medium | Malware blocked after execution attempt, phishing with limited clicks | Same shift hunt |
| Low / Info | Policy violation, noisy IDS without corroboration | Queue, correlate |

## Detection and analysis
1. Confirm the alert is not a known false positive (tuning list, change ticket, scanner).
2. Build a timeline: first seen, last seen, affected identities and hosts, related tickets.
3. Classify likely MITRE tactic using telemetry, not guesswork.
4. Record IOCs only from observed evidence. Mark unconfirmed indicators separately.
5. If impact is unclear, raise severity rather than closing as noise.

## Containment principles
- Prefer network isolation and identity session revoke over destructive cleanup while evidence is incomplete.
- Preserve volatile evidence (memory, live network connections) when C2 or ransomware is suspected.
- Do not reboot, wipe, or reimage until the incident commander agrees, except for confirmed commodity PUAs with no lateral movement.
- Communicate in the incident channel; do not email samples.

## Evidence minimum set
- EDR process tree and detections
- Identity sign-in logs covering ±24 hours
- Mailbox audit if phishing or BEC is in scope
- Proxy/DNS for the host
- Relevant Windows Security or syslog around the timestamp

## Hand-off
Promote to IR/forensics when there is confirmed C2, credential dumping, domain privilege escalation, ransomware encryption, or likely exfiltration. Attach this copilot's source citations and the incident card.
