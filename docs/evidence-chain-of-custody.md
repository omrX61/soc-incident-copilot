---
title: Evidence Collection and Chain of Custody
category: Forensics
id: SOC-FOR-001
---

# Evidence Collection and Chain of Custody

## Order of volatility
Memory and live network state, then disk, then remote logs. Do not run untrusted cleaners on a host that will be imaged.

## Minimum labeling
Case ID, collector, UTC timestamp, hostname, hash of the artifact, source path, and storage location. Store hashes in the ticket.

## What Tier 1 may collect
- EDR packages and timeline exports
- .eml and gateway reports
- IdP CSV/JSON exports
- Screenshots of consoles with UTC visible

## What requires IR/forensics
- Full memory
- Disk image
- Domain controller artifacts
- Cloud activity trails spanning multiple accounts

## Handling malware
Do not open samples on an analyst workstation. Use the detonation environment. Transfer via the designated malware share, not email or chat.
