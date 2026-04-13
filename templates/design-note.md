# Design Note: [Feature Name]

<!--
PURPOSE: Document the technical approach BEFORE coding starts.
AUDIENCE: Engineers, architects, security reviewers.
GOAL: Answer "how will we build this?" in 1-2 pages. Focus on impacts and decisions.
AUTO-GENERATE: PRDEngine (https://github.com/kbot-ships/PRDEngine) can generate this
from a feature description. Its "Standard" tier includes API design, data model, and
security sections that map to this template's structure.
-->

## Approach Summary
<!--
Describe the technical approach in 1-2 paragraphs.
- What's the high-level architecture?
- What components are involved?
- Why this approach over alternatives?

Example (see bottom for full example):
We'll add a new POST /team/invites endpoint that accepts multiple email addresses,
validates them against existing users and pending invites, generates unique invite
tokens, and returns shareable links. The UI calls this endpoint when the admin submits
the bulk invite form.
-->


## API / Interface Impacts

### New Endpoints
<!-- List new endpoints. Format: METHOD /path - purpose -->

### Changed Endpoints
<!-- List modified endpoints. What's changing and why? -->

### Breaking Changes
<!-- Any breaking changes to existing APIs? How will we handle backward compatibility? -->


## Data Model Impacts

### New Entities
<!-- Any new database tables or schemas? -->

### Modified Entities
<!-- Changes to existing tables? New fields, constraints, indexes? -->

### Migration Story
<!--
How will we migrate existing data?
- Alembic migration script needed?
- Default values for new fields?
- Data backfill required?
-->


## Security Implications

### Authorization Touchpoints
<!--
What operations require auth checks?
- Which roles can access new endpoints?
- Any row-level security (e.g., user can only see their own team)?
-->

### Audit Fields
<!--
What gets logged?
- User actions to audit log?
- Sensitive data handling?
- PII or confidential classification concerns?
-->

### Other Security Considerations
<!--
- Input validation requirements?
- Rate limiting needed?
- Secrets/credentials handling?
-->


## Rollout Plan

### Feature Flags
<!-- Will this use a feature flag? What's the flag name and default state? -->

### Migrations
<!-- Database migrations? Service restart required? Order of operations? -->

### Backward Compatibility
<!--
How do we ensure old clients still work?
- Graceful degradation?
- Version negotiation?
- Deprecation timeline?
-->

### Testing Strategy
<!--
- Unit tests for core logic?
- Integration tests for API endpoints?
- Manual testing scenarios?
-->


---

<!--
EXAMPLE (delete before filling in):

# Design Note: Bulk Team Member Invitation

## Approach Summary
We'll add a new service method `create_bulk_invites()` in the Team service that
validates email addresses, checks for duplicates against existing users and pending
invites, generates unique cryptographically secure invite tokens (32 bytes), and stores
them in a new `team_invites` table. This logic is exposed via POST /api/v1/team/invites.
The frontend calls this endpoint when the admin submits the bulk invite form and displays
shareable links for each invitation.

We're avoiding email-only invites because they're unreliable (spam filters, expiration).
Shareable links allow admins to distribute invites via any channel. We're not using
background jobs because invite creation should be fast (<1s for 10 invites) and we
want immediate feedback.

## API / Interface Impacts

### New Endpoints
- POST /api/v1/team/invites - Create bulk invitations
  - Request: `{"emails": ["alice@example.com", "bob@example.com"], "role": "member"}`
  - Response: `{"invites": [{"email": "alice@example.com", "link": "https://app.example.com/accept/abc123", "status": "sent"}]}`
  - Auth: Requires admin role

### Changed Endpoints
- GET /api/v1/team/members - Add `pending_invites` array to response
  - Backward compatible: new field only
  - Shows pending invites with email, role, invited_by, invited_at

### Breaking Changes
None. All changes are additive.

## Data Model Impacts

### New Entities
**team_invites table:**
- `id` (UUID, primary key)
- `email` (string, indexed)
- `role` (string: "member", "admin", "viewer")
- `token` (string, unique, indexed) - 32-byte random hex
- `invited_by` (UUID, foreign key to users.id)
- `team_id` (UUID, foreign key to teams.id)
- `created_at` (timestamp)
- `expires_at` (timestamp, nullable) - null = never expires
- `used_at` (timestamp, nullable) - null = not used yet

### Modified Entities
**users table:**
- Add `invited_by` (UUID, nullable, foreign key to users.id) - tracks who invited this user
- Add index on `invited_by` for analytics queries

### Migration Story
Alembic migration creates new `team_invites` table and adds `invited_by` column to `users`
table with default NULL. No data backfill needed since this is a new feature. Existing
users remain with NULL `invited_by`.

## Security Implications

### Authorization Touchpoints
- POST /api/v1/team/invites: Requires admin role, user must be member of target team
- GET /api/v1/team/members: No change (already requires team member)
- GET /accept/:token: Public endpoint (no auth), validates token and creates user session

### Audit Fields
- Log to audit trail when invites are created: `{"action": "team.invites.created", "emails": [...], "invited_by": "...", "team_id": "..."}`
- Log when invite is accepted: `{"action": "team.invites.accepted", "email": "...", "user_id": "...", "team_id": "..."}`
- Log failed invite attempts (invalid token, expired, already used)

### Other Security Considerations
- Input validation: Email format validation, max 50 emails per request
- Rate limiting: 10 requests per minute per admin (prevent abuse)
- Token generation: Use `secrets.token_urlsafe(32)` for cryptographically secure tokens
- Token validation: Single-use tokens (mark `used_at` on first use)
- Email verification: Require email confirmation on first login even with valid invite

## Rollout Plan

### Feature Flags
Feature flag: `bulk_team_invites_enabled` (default: false)
- When disabled: "Invite Members" button hidden in UI, endpoint returns 404
- When enabled: Full feature available

### Migrations
1. Deploy backend with new endpoint (feature flag off)
2. Run Alembic migration to create `team_invites` table and add `invited_by` column
3. Deploy frontend with bulk invite UI (feature flag off)
4. Enable feature flag for internal testing (1 week)
5. Enable feature flag for all organizations after testing

### Backward Compatibility
Fully backward compatible:
- Old UI works (uses existing single-invite endpoint)
- New endpoint is additive
- Database changes are additive with safe defaults (NULL values)
- Old invite links (if any) continue to work

### Testing Strategy
**Unit tests:**
- Test `create_bulk_invites()` logic with valid emails
- Test duplicate detection (existing users, pending invites)
- Test token generation (uniqueness, cryptographic strength)
- Test email validation (malformed, invalid domains)

**Integration tests:**
- Test POST /api/v1/team/invites endpoint
- Test GET /accept/:token flow (create user, add to team)
- Test feature flag behavior (enabled vs disabled)
- Test authorization (admin-only access)

**Manual testing:**
- Bulk invite flow end-to-end with real emails
- Test edge cases: duplicate emails, invalid formats, expired tokens
- Test accept flow from different browsers/devices
- Test with organization domain allowlist enabled

-->
