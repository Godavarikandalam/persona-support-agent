# API Troubleshooting Guide

## 401 Unauthorized Errors

A `401 Unauthorized` response means the API request did not include valid
authentication credentials. Common causes:

1. **Missing Authorization header.** Every request must include:
   `Authorization: Bearer <your_api_key>`
2. **Expired API key.** Keys rotate every 90 days by default. Check the
   "Created" and "Expires" dates in Dashboard > API Keys.
3. **Wrong environment key.** Test-mode keys (prefixed `sk_test_`) will not
   authenticate against production endpoints, and vice versa.
4. **Key revoked.** If a key was manually revoked or regenerated, the old
   key stops working immediately with no grace period.

### Resolution Steps
- Confirm the header is exactly `Authorization: Bearer sk_live_xxxxx` with no
  extra whitespace or quotes.
- Regenerate a new key from Dashboard > API Keys > Generate New Key if the
  old one is expired or revoked.
- Check that you are hitting the correct base URL: `https://api.example.com/v1/`
  for production, `https://api-sandbox.example.com/v1/` for testing.

## 429 Rate Limit Errors

Our API enforces a rate limit of 100 requests per minute per API key on the
Professional plan, and 20 requests per minute on the Starter plan. If you
receive a `429 Too Many Requests` response, the `Retry-After` header
indicates how many seconds to wait before retrying. We recommend implementing
exponential backoff with jitter rather than retrying immediately.

## Database Integration / Internal Server Errors (500)

`500 Internal Server Error` responses from our webhook or integration
endpoints are most commonly caused by:
- Malformed JSON payloads (trailing commas, unescaped quotes).
- Webhook timeouts if your endpoint takes longer than 10 seconds to respond.
- Schema mismatches after an API version upgrade — check the `API-Version`
  header you are sending against our current supported versions (v1, v2).

If errors persist after verifying the above, capture the `X-Request-ID`
header from the failed response and include it when contacting support, as
it allows our engineering team to look up the exact server-side stack trace.

## Webhook Signature Verification Failures

Webhook payloads are signed using HMAC-SHA256 with your webhook signing
secret (found in Dashboard > Webhooks > Signing Secret). Verification
failures are almost always caused by computing the signature over a
re-serialized JSON body instead of the raw request bytes. Always verify
against the raw, unparsed request body.
