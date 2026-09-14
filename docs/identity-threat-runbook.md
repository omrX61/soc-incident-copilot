---
title: Identity Threat Detection and Response Runbook
category: Identity
id: SOC-RB-ITDR-001
---

# Identity Threat Detection and Response Runbook

## Priority identity events
- Impossible travel / unfamiliar properties after phishing
- Legacy authentication success
- Privileged role activation outside change windows
- Consent to an unverified OAuth application
- Password spray followed by a single success
- Golden/silver ticket suspicions (Kerberos anomalies)

## Response pattern
1. Confirm the identity, device, and application involved.
2. Revoke sessions and refresh tokens.
3. Disable the account if attacker control is likely; otherwise force password reset and MFA re-register.
4. Review group membership, app roles, and mailbox settings for ±24 hours.
5. Hunt lateral use: VPN, RDP, cloud consoles, Git, and privileged workstations.

## Service accounts
Service accounts without MFA are high-value. If one is sprayed or dumped, rotate the secret, review where it is hardcoded, and check token or Kerberos use after the suspected dump time.

## Evidence
- IdP sign-in and audit logs
- Conditional Access evaluation
- Privileged Identity Management activations
- Endpoint that performed the authentication
