---
title: Lateral Movement Triage Playbook
category: Playbook
id: SOC-PB-LM-001
---

# Lateral Movement Triage Playbook

## Common paths
RDP (T1021.001), SMB/admin shares, WinRM/PowerShell remoting, PsExec-like services, and cloud console hop from a stolen session.

## Analyst workflow
1. Identify the source logon: user, source IP, logon type, workstation.
2. Identify the destination and whether it is a jump host, file server, or domain controller.
3. Check for new local admins, services, and scheduled tasks on the destination during the session.
4. Assume credential exposure if LSASS access or debug privilege was observed on the source.
5. Expand the hunt one hop in each direction before containment of only the first host.

## High-signal events
- 4624 type 10 from a workstation that is not a VDI pool
- 7045 new service with a temp path
- 4698 scheduled task
- Successful admin share access followed by file encrypt or credential dump

## Containment
Disable the moving identity, isolate source and destination, reset local admin passwords on touched servers if LSA dump is plausible, and review Kerberos ticket lifetime.
