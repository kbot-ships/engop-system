"""
Ticket gatekeeping webhook listener -- Phase 1 (validate + block).

Minimal reference implementation. Listens for issue state-change webhooks,
validates required fields on gated tickets, and reverts the transition if
fields are missing.

Adapt to your issue tracker:
  - Linear:  action == "update", data.state.name
  - Jira:    webhookEvent == "jira:issue_updated", changelog
  - GitHub:  action == "edited", issue.state

Usage:
  python gate.py                        # runs on :8090 (stdlib only, no deps)
  TRACKER=jira python gate.py           # switch tracker adapter
  GATE_PORT=9000 python gate.py         # custom port
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
GATE_PORT = int(os.getenv("GATE_PORT", "8090"))
TRACKER = os.getenv("TRACKER", "linear")  # linear | jira | github

TRIGGER_LABELS = {"interface", "contract", "ux-facing", "breaking-change"}
TARGET_STATE = "In Progress"

REQUIRED_FIELDS = [
    "definition_of_done",
    "acceptance_criteria",
]

# At least one of these links must be present.
REQUIRED_LINKS = [
    "ux_mock_link",
    "api_contract_link",
]


# ---------------------------------------------------------------------------
# Tracker adapters -- normalize webhooks into a common shape
# ---------------------------------------------------------------------------

@dataclass
class TicketEvent:
    ticket_id: str
    title: str
    new_state: str
    old_state: str
    labels: list[str]
    fields: dict[str, str]


def parse_linear(payload: dict) -> TicketEvent | None:
    """Parse a Linear issue.update webhook."""
    if payload.get("action") != "update":
        return None
    data = payload.get("data", {})
    updated_from = payload.get("updatedFrom", {})
    return TicketEvent(
        ticket_id=data.get("id", ""),
        title=data.get("title", ""),
        new_state=data.get("state", {}).get("name", ""),
        old_state=updated_from.get("state", {}).get("name", ""),
        labels=[l.get("name", "") for l in data.get("labels", [])],
        fields=data.get("customFields", {}),
    )


def parse_jira(payload: dict) -> TicketEvent | None:
    """Parse a Jira issue_updated webhook."""
    issue = payload.get("issue", {})
    changelog = payload.get("changelog", {})
    status_change = None
    for item in changelog.get("items", []):
        if item.get("field") == "status":
            status_change = item
            break
    if not status_change:
        return None
    fields = issue.get("fields", {})
    return TicketEvent(
        ticket_id=issue.get("key", ""),
        title=fields.get("summary", ""),
        new_state=status_change.get("toString", ""),
        old_state=status_change.get("fromString", ""),
        labels=fields.get("labels", []),
        fields={
            "definition_of_done": fields.get("customfield_10100", ""),
            "acceptance_criteria": fields.get("customfield_10101", ""),
            "ux_mock_link": fields.get("customfield_10102", ""),
            "api_contract_link": fields.get("customfield_10103", ""),
        },
    )


def parse_github(payload: dict) -> TicketEvent | None:
    """Parse a GitHub Issues webhook (project board column move)."""
    issue = payload.get("issue", {})
    if payload.get("action") not in ("edited", "labeled", "transferred"):
        return None
    return TicketEvent(
        ticket_id=str(issue.get("number", "")),
        title=issue.get("title", ""),
        new_state=issue.get("state", ""),
        old_state="",
        labels=[l.get("name", "") for l in issue.get("labels", [])],
        fields={},  # GitHub Issues: parse from body
    )


PARSERS = {
    "linear": parse_linear,
    "jira": parse_jira,
    "github": parse_github,
}


# ---------------------------------------------------------------------------
# Gate logic
# ---------------------------------------------------------------------------

def check_gate(event: TicketEvent) -> list[str]:
    """Return a list of missing-field messages. Empty list = gate passes."""
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        value = event.fields.get(field, "").strip()
        if not value:
            errors.append(f"Missing required field: **{field.replace('_', ' ').title()}**")

    has_link = any(
        event.fields.get(link, "").strip()
        for link in REQUIRED_LINKS
    )
    if not has_link:
        links_display = " or ".join(
            f"**{l.replace('_', ' ').title()}**" for l in REQUIRED_LINKS
        )
        errors.append(f"At least one required: {links_display}")

    return errors


def build_comment(event: TicketEvent, errors: list[str]) -> str:
    """Build the bot comment explaining what's missing."""
    lines = [
        f"**Gate check failed** for _{event.title}_\n",
        "The following are required before moving to In Progress:\n",
    ]
    for err in errors:
        lines.append(f"- {err}")
    lines.append(
        "\nAdd the missing fields and move the ticket back to In Progress."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

class GateHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Verify signature if secret is configured
        if WEBHOOK_SECRET:
            sig_header = self.headers.get("X-Signature", "")
            expected = hmac.new(
                WEBHOOK_SECRET.encode(), body, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(sig_header, f"sha256={expected}"):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Invalid signature")
                return

        payload = json.loads(body)
        parser = PARSERS.get(TRACKER)
        if not parser:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Unknown tracker: {TRACKER}".encode())
            return

        event = parser(payload)
        if not event:
            self._ok({"action": "ignored", "reason": "not a state change"})
            return

        # Only gate transitions to the target state
        if event.new_state != TARGET_STATE:
            self._ok({"action": "ignored", "reason": f"state is {event.new_state}"})
            return

        # Only gate tickets with trigger labels
        if not TRIGGER_LABELS.intersection(set(event.labels)):
            self._ok({"action": "allowed", "reason": "no trigger labels"})
            return

        errors = check_gate(event)
        if errors:
            comment = build_comment(event, errors)
            # In production: call tracker API to revert state + post comment.
            # This reference implementation logs the action.
            print(f"[BLOCKED] {event.ticket_id}: {event.title}")
            for err in errors:
                print(f"  - {err}")
            self._ok({
                "action": "blocked",
                "ticket": event.ticket_id,
                "errors": errors,
                "comment": comment,
            })
        else:
            print(f"[ALLOWED] {event.ticket_id}: {event.title}")
            self._ok({"action": "allowed", "ticket": event.ticket_id})

    def _ok(self, data: dict):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, format, *args):
        # Quieter request logging
        pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", GATE_PORT), GateHandler)
    print(f"Gate listener running on :{GATE_PORT} (tracker={TRACKER})")
    print(f"Trigger labels: {', '.join(sorted(TRIGGER_LABELS))}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()
