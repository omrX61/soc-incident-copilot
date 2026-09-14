---
title: Ransomware Containment Playbook
category: Playbook
id: SOC-PB-RANSOM-001
---

# Ransomware Containment Playbook

## Decision triggers
Treat as ransomware when two or more are present: mass file encryption or extension change, ransom note, VSS/backup deletion, or simultaneous impact on multiple hosts/shares.

## Immediate containment
1. Isolate affected hosts and the subnet of the file server if encryption is ongoing.
2. Disable the account used for admin shares or backup if identified.
3. Block known C2 and payload hashes at EDR/proxy.
4. Pause outbound mail from impacted servers if notes are being mailed internally.
5. Protect backup infrastructure: take backup consoles off the production network if tampering is suspected.

## Do not
- Do not power off every host without capturing volatile evidence on a sample set.
- Do not start widespread restores until patient zero and persistence are understood.
- Do not negotiate payment from the SOC channel; escalate to legal/leadership.

## Evidence
- Ransom note and a small set of encrypted files
- EDR timeline for the first encrypting process
- 4624/4672 around the file server
- Backup job logs and VSS events
- Domain privileged group changes in the prior 72 hours

## Recovery outline
Identify clean restore points, rebuild rather than "decrypt and hope" for core servers, rotate all privileged credentials, and hunt for remaining backdoors (scheduled tasks, services, GPO, VPN accounts) before reconnecting restored systems.
