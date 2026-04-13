# PRD-lite: [Feature Name]

<!--
PURPOSE: Define the "why" and "what" in ONE PAGE before UX and design work starts.
GOAL: Clarity, not completeness. If you can't fit it on one page, it's too big.
EXAMPLE: See bottom for a filled-in example.
AUTO-GENERATE: PRDEngine (https://github.com/kbot-ships/PRDEngine) can generate this
from a feature description. Its "Lightweight" tier maps directly to this template.
-->

## Problem Statement
<!-- What user pain or business need does this address? 1-2 sentences. -->


## Target User / Persona
<!-- Who specifically is this for? Team admin? End user? API consumer? Developer? -->


## Current Workflow vs Proposed Workflow

**Current:**
<!-- Describe how users accomplish this today (or why they can't). 3-5 bullet points. -->

**Proposed:**
<!-- Describe the new workflow. 3-5 bullet points. Focus on user actions, not implementation. -->


## Success Criteria (Measurable)
<!-- How will we know this works? Must be measurable. Examples: "Setup time < 2 minutes", "95% of users complete flow without support ticket", "API response time < 200ms" -->


## Non-Goals (Explicit Scope Boundaries)
<!-- What are we explicitly NOT doing in this iteration? This prevents scope creep. -->


## Risks and Open Questions
<!-- What could go wrong? What don't we know yet? What needs research or decision? -->


---

<!--
EXAMPLE (delete before filling in):

# PRD-lite: Team Member Invitation Flow

## Problem Statement
Team admins spend 5-10 minutes per user invitation due to multi-step forms and email confusion. 60% of invites require support intervention because users can't find the invite email or it expires.

## Target User / Persona
- Team administrator who needs to onboard new team members
- Has permission to manage team settings
- Invites 3-10 people per month on average

## Current Workflow vs Proposed Workflow

**Current:**
- Navigate to Team Settings page
- Click "Add Member" button
- Fill out 5-field form (email, role, department, access level, expiration)
- Click "Send Invite"
- Wait for email to send (no confirmation shown)
- User checks email, may miss invite or have it expire (48 hours)

**Proposed:**
- Navigate to Team Settings page
- Click "Invite Members" button
- Paste one or more email addresses (comma-separated)
- Select role from dropdown (defaults to "Member")
- Click "Send Invites"
- See immediate confirmation with shareable invite links
- Invites never expire until used or manually revoked

## Success Criteria (Measurable)
- Invite action completes in < 3 clicks (vs 8+ today)
- 80% of invited users successfully join within 24 hours (vs 40% today)
- Support tickets related to invites reduced by 70%
- Bulk invite of 10 users takes < 30 seconds

## Non-Goals (Explicit Scope Boundaries)
- NOT handling guest user invitations (team members only)
- NOT supporting custom email templates in first version
- NOT implementing SSO/SAML provisioning (separate feature)

## Risks and Open Questions
- Risk: Shareable links could be forwarded to wrong people
  - Mitigation: Add "This invite is for [email]" message in UI, require email verification on first login
- Open: Should we allow setting individual roles in bulk invite?
  - Decision needed: UX review (may complicate the "quick" aspect)
- Open: What happens if email domain is not on organization allowlist?
  - Should we block? Warn? Needs security review.

-->
