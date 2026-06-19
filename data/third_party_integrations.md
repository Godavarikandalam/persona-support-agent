# Third-Party Integrations Guide

## Slack Integration

To connect Slack, go to Dashboard > Integrations > Slack > Connect, and
authorize the OAuth request in the popup window. Once connected, you can
configure which channels receive notifications under Integrations > Slack >
Channel Settings.

**Common issue: "Slack integration disconnected" banner.** This appears when
the OAuth token expires (typically after 90 days of inactivity) or when a
Slack workspace admin revokes third-party app access. Reconnect via
Dashboard > Integrations > Slack > Reconnect.

## Zapier Integration

Our Zapier integration supports both Triggers (new ticket created, status
changed) and Actions (create ticket, update ticket). You'll need a Zapier
account and your API key (Dashboard > API Keys) to set up the connection on
Zapier's side.

**Common issue: Zap runs but nothing happens.** Check the Zap's task history
in Zapier for the actual API response - this usually reveals a missing
required field (most often the `priority` field, which is required on ticket
creation but not marked as such in older versions of our Zapier app).

## Webhooks (Custom Integrations)

For custom integrations, use our webhook system rather than polling our API
repeatedly. Configure webhook endpoints under Dashboard > Webhooks > Add
Endpoint. We support these event types: `ticket.created`, `ticket.updated`,
`ticket.resolved`, `customer.created`.

Webhook payloads are signed with HMAC-SHA256 - see the API Troubleshooting
guide for signature verification details. Webhook deliveries are retried up
to 5 times with exponential backoff if your endpoint returns a non-2xx
status code or times out.

## Microsoft Teams Integration

Teams integration is currently in beta and supports notification forwarding
only (no two-way sync like Slack). Enable it under Dashboard > Integrations
> Microsoft Teams > Connect, which requires a Teams admin to approve the app
in your organization's Teams Admin Center.

## Salesforce Sync

Salesforce sync is available on Enterprise plans only. It performs a one-way
sync (our platform -> Salesforce) of customer records every 4 hours. Real-time
sync is on our roadmap but not currently available. Field mapping is
configured under Dashboard > Integrations > Salesforce > Field Mapping, and
mismatched field types (e.g. mapping a text field to a Salesforce number
field) are the most common cause of sync failures.
