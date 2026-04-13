# Case Study: API Contract Without a UI

*How contract-first applies when there's no screen to mock.*

---

## The scenario

Your team needs to build a **webhook notification system**. When a model deployment completes, external systems get notified via HTTP callback. There is no user interface -- this is a pure API feature consumed by other services and third-party integrations.

The instinct: skip the UX mock, jump straight to code. The API is "obvious."

This case study shows why contract-first still matters and what it catches.

---

## Layer 1: Intent

### Discovery (1 session, 30 minutes)

The engineer talks to the product owner and two integration partners who will consume the webhooks.

**What the engineer assumed:**
- POST a JSON payload to a registered URL when deployment status changes
- Include the model ID and new status
- Done

**What discovery revealed:**
- Integration Partner A needs the payload signed (HMAC) so they can verify it came from us
- Integration Partner B needs retry logic -- their endpoint goes down for maintenance windows
- Product owner wants a webhook management UI eventually, but for V1 just needs CRUD via API
- Both partners need to filter events -- they don't want every status change, just `DEPLOYED` and `FAILED`
- Partner A asks: "What happens if we return a 500? Do you retry? How many times? Is there a dead letter queue?"

**One 30-minute conversation surfaced 5 requirements the engineer hadn't considered.** Without this conversation, the engineer would have built a simple POST-on-status-change that neither partner could actually use.

---

## Layer 2: Design

No UX mock needed. Instead, the contract artifact is an **API contract** that both integration partners review before code starts.

### API contract (reviewed before build)

```
POST   /api/v1/webhooks                  Register a webhook endpoint
GET    /api/v1/webhooks                  List registered webhooks
GET    /api/v1/webhooks/{id}             Get webhook details + delivery history
DELETE /api/v1/webhooks/{id}             Unregister a webhook
PATCH  /api/v1/webhooks/{id}             Update webhook (URL, events, active flag)
```

**Registration payload:**
```json
{
  "url": "https://partner.example.com/callbacks",
  "events": ["deployment.completed", "deployment.failed"],
  "secret": "shared-secret-for-hmac"
}
```

**Delivery payload:**
```json
{
  "event": "deployment.completed",
  "timestamp": "2026-03-15T14:30:00Z",
  "data": {
    "deployment_id": "uuid",
    "model_id": "uuid",
    "model_name": "llama-3-8b",
    "status": "DEPLOYED",
    "engine": "vllm"
  },
  "signature": "sha256=abcdef..."
}
```

**Retry policy (from discovery):**
- 3 retries with exponential backoff (10s, 60s, 300s)
- After 3 failures: mark delivery as `failed`, log to delivery history
- No dead letter queue in V1 (explicit non-goal)

**Non-goals (V1):**
- Webhook management UI
- Dead letter queue / manual retry
- Batched event delivery
- Custom payload templates

### What the contract review caught

Partner A reviewed the contract and flagged: "The signature should be over the raw body bytes, not a JSON re-serialization. We've been burned by this -- different JSON serializers produce different byte strings."

Partner B flagged: "We need the `X-Webhook-ID` header for idempotency. If you retry and we've already processed it, we need to deduplicate."

**Two integration-breaking issues caught before a line of code was written.**

---

## Layer 3: Traceability

The PRD-lite for this feature:

| Section | Content |
|:--------|:--------|
| **Problem** | External systems have no way to react to deployment events without polling. Polling wastes resources and introduces latency. |
| **Target user** | Integration partners consuming deployment lifecycle events programmatically |
| **Success criteria** | Webhook delivery within 5 seconds of event. 99.9% delivery rate (excluding partner downtime). Partners can register without support tickets. |
| **Non-goals** | UI, dead letter queue, batching, custom payloads |

Each acceptance criterion traces to a specific API endpoint or behavior in the contract.

---

## Layer 4: Execution

The engineer builds to the contract. No ambiguity about:
- Which endpoints to implement
- What the payloads look like
- How retries work
- What's in scope vs. out of scope

**Build time:** 3 days (vs. estimated 5 days without the upfront contract, accounting for the rework that discovery prevented).

---

## What contract-first caught (without a UI)

| Issue | When caught | Cost if missed |
|:------|:------------|:---------------|
| HMAC signing requirement | Discovery | Partner A can't use the feature at all |
| Event filtering | Discovery | Partners receive 10x the traffic they need |
| Retry policy questions | Discovery | Integration failures in production |
| Signature-over-raw-bytes | Contract review | Subtle verification bug in production |
| Idempotency header | Contract review | Duplicate processing on retries |

Five issues. Zero lines of code wasted.

---

## The lesson

Contract-first isn't "mock the UI first." It's **make the interface reviewable before you build.**

For API-only features, the contract *is* the mock:
- Endpoint list with methods and paths
- Request/response payloads as JSON examples
- Behavior specs (retries, errors, auth)
- Non-goals to prevent scope creep

If the consumers of your API can't review what they're getting before you build it, you're guessing. Contract-first eliminates the guess.

---

## Applying this to your team

1. **Identify who consumes the API** -- internal services, partners, frontend teams
2. **Write the contract first** -- endpoints, payloads, error codes, behavior specs
3. **Have consumers review it** -- before you write code, not after
4. **Document non-goals** -- what you're explicitly not building prevents scope creep
5. **Trace acceptance criteria to contract** -- every criterion maps to a specific behavior
