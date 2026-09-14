---
title: Command and Control Hunt Notes
category: Detection Engineering
id: SOC-DE-C2-001
---

# Command and Control Hunt Notes

## Beacon characteristics
Look for periodic connections with low jitter, rare destinations, newly registered domains, unsigned processes making HTTPS, and DNS queries that do not match business software.

## Host-side
- New services or scheduled tasks created near first beacon
- Named pipes or mutexes associated with commodity RATs
- Living-off-the-land binaries as parents of network activity
- Persistence in Run keys, WMI subscriptions, or Startup folders

## Network-side
- Proxy logs: first seen domain, category uncategorized, long-lived POST
- Firewall: allow to unusual ports from workstations
- DNS: high NXDOMAIN or labeled entropy

## Response
Isolate the host with EDR containment rather than pulling the cable if memory capture is planned. Block domain and IP. Hash the implant. Hunt the hash, mutex, and C2 across the estate. Assume credentials on that host are exposed if the implant ran as the user or SYSTEM.
