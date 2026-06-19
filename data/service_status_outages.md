# Service Status, Outages, and Incident History

## Checking Current System Status

Real-time system status, including any ongoing incidents or degraded
performance, is published at status.example.com. This page is updated
independently of our main application, so it remains accessible even during
a full platform outage.

## Subscribing to Status Updates

You can subscribe to incident notifications via email, SMS, or webhook from
the status page. We recommend subscribing if your team relies on our API
for critical workflows, since this is the fastest way to be notified of
degraded performance before it impacts your integration.

## What Counts as a "Major Incident"

A major incident is declared when:
- Core functionality (login, dashboard, API) is unavailable for more than
  5 minutes, or
- Data processing delays exceed 30 minutes, or
- A security-relevant event requires immediate customer notification.

Minor performance blips (a single failed request, a few seconds of latency)
do not trigger a status page incident and are considered normal transient
network variance.

## Service Level Agreement (SLA) and Credits

Enterprise plan customers with a signed SLA are eligible for service credits
if uptime falls below the guaranteed 99.9% in a given calendar month.
Credit requests must be submitted within 30 days of the end of the affected
month via your account manager - service credits are not issued
automatically and require manual review of the incident timeline against
your specific SLA terms.

## Scheduled Maintenance

Planned maintenance windows are announced at least 72 hours in advance via
the status page and email to account administrators. Scheduled maintenance
typically occurs during low-traffic windows and is designed to complete
within 15 minutes with no user-facing downtime, though some real-time
features (live sync, webhooks) may be briefly paused during the window.

## Post-Incident Reports

For major incidents, a public post-incident report (root cause, timeline,
remediation steps) is published on the status page within 5 business days
of resolution.
