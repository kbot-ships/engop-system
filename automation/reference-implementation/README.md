# Reference Implementation: Ticket Gatekeeping

Minimal webhook listener that enforces required fields before tickets move to "In Progress."

## What it does

1. Receives a webhook when a ticket state changes
2. Checks if the ticket has a trigger label (`interface`, `contract`, etc.)
3. Validates required fields (Definition of Done, Acceptance Criteria, UX/API link)
4. If fields are missing: returns a structured response with what's needed
5. If fields are present: allows the transition

This implements **Phase 1** from the [gatekeeping blueprint](../ticket-gatekeeping.md). It validates and reports -- your tracker integration adds the revert + comment step.

## Quick start

```bash
python gate.py                        # no dependencies beyond stdlib
```

## Configuration

| Env var | Default | Purpose |
|:--------|:--------|:--------|
| `TRACKER` | `linear` | Tracker adapter (`linear`, `jira`, `github`) |
| `GATE_PORT` | `8090` | Listen port |
| `WEBHOOK_SECRET` | _(empty)_ | HMAC secret for signature verification |

## Adapting to your tracker

The script uses Python's built-in `http.server` (no external dependencies). It includes parsers for Linear, Jira, and GitHub Issues, each normalizing the webhook payload into a common `TicketEvent` shape. To add your own tracker:

1. Write a `parse_yourtracker(payload) -> TicketEvent | None` function
2. Add it to the `PARSERS` dict
3. Set `TRACKER=yourtracker`

## What's not included (intentionally)

- **State revert API calls** -- these are tracker-specific and need auth tokens
- **Comment posting** -- same reason; the response body contains the comment text to post
- **Phase 2 scaffolding** -- branch creation, doc stubs, draft PRs
- **PRDEngine integration** -- invoke PRDEngine to auto-generate stubs (see [blueprint](../ticket-gatekeeping.md))

This is a starting point, not a production service. Fork it and wire in your tracker's API.
