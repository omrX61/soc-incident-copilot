---
title: Phishing and Business Email Compromise Playbook
category: Playbook
id: SOC-PB-PHISH-001
---

# Phishing and Business Email Compromise Playbook

## Scope
Covers credential harvest, AiTM/session cookie theft, malicious attachments, and BEC/invoice fraud. Pair with local PDFs on phishing guidance when more detail is required.

## First 30 minutes
1. Pull the message headers, recipient list, URL rewrite logs, and attachment hashes.
2. Search the tenant for the same subject, sender, URL, and hash.
3. If any recipient clicked or opened:
   - Revoke sessions / refresh tokens for those identities.
   - Check inbox rules, forwarding, hidden folders, and OAuth grants.
   - Check MFA registration changes.
4. Quarantine the campaign at the mail gateway.
5. Open a case with severity High if a privileged, finance, or VIP mailbox is involved.

## AiTM specific
- Treat successful sign-in from an anonymous IP or hosting ASN immediately after a click as probable session theft even if MFA succeeded.
- Revoke tokens, disable stay-signed-in, and require re-authentication.
- Hunt for mailbox rules created within the session window.

## BEC / payment diversion
- Contact treasury/finance by a known-good channel, not by replying to the thread.
- Freeze the payment if still pending.
- Preserve the full conversation, including display-name spoof vs lookalike domain.

## Evidence
- Original .eml
- URL detonation report
- Sign-in logs for clickers
- Inbox rule export
- Endpoint process tree if an attachment executed

## Close criteria
Campaign quarantined, compromised sessions revoked, rules removed, users notified, and residual hunt complete for ±7 days of related indicators.
