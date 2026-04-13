# Ticket Gatekeeping Automation

*Blueprint: enforce requirements before work starts.*

## Problem

Interface and contract work frequently starts without testable intent defined upfront. Engineers move tickets to "In Progress" without acceptance criteria, design documentation, or linked UX/API contracts. The result is technically sound builds that miss customer intent and require rework after implementation is complete.

**Cost of late discovery:**
- Wasted engineering time building the wrong thing
- Design rework after implementation
- Customer frustration with missed expectations
- Extended delivery timelines

## Solution: State Transition Enforcement

Enforce required fields and artifacts before allowing issue state transitions. When a ticket is moved to "In Progress" AND it meets trigger criteria (see Scope below), the automation enforces required fields before allowing the transition.

### Required Fields

**Core requirements:**
- Definition of Done (DoD)
- Acceptance Criteria
- Required links: UX mock OR API contract (can be a link to a file, design tool, or inline description)

**Teams should customize based on their needs. Additional examples:**
- Test strategy or test plan link
- Architecture decision record (ADR) reference
- Security/privacy review status
- Performance requirements
- Accessibility requirements

### Bot Behavior

**When fields are missing:**
- Block the state transition
- Post a comment explaining what's needed
- Provide template links or examples
- Optionally notify in team chat (Slack, Teams, Discord)

**When fields are present:**
- Allow transition to "In Progress"
- Auto-create helpful scaffolding (see Auto-Stub section below)

## Scope: What Triggers the Gate

The gatekeeping applies ONLY to tickets with specific labels/tags. This keeps friction targeted and avoids slowing down non-interface development work.

### Example Trigger Labels

**Reference implementation (adapt to your team):**
- `interface` - User-facing changes
- `contract` - API/service contract changes
- `ux-facing` - Frontend/UI work
- `breaking-change` - Backward-incompatible changes
- `architecture` - Significant architectural decisions

**Explicitly excluded from gating:**
- Bug fixes (unless they change interfaces)
- Chores and maintenance work
- Internal-only technical work
- Documentation updates
- Dependency updates

**Customization guidance:**
- Start with 2-3 trigger labels to avoid over-gating
- Review quarterly: which work types cause most rework?
- Consider severity tiers (strict for breaking changes, lighter for enhancements)

## Auto-Stub Behavior

When the bot allows transition to "In Progress", it can optionally auto-generate helpful scaffolding to reduce setup friction.

### Example Scaffolding Actions

1. **Feature branch creation** (if not already automated)
   - Create branch with consistent naming: `feature/{ticket-slug}` or `{team-prefix}/{ticket-id}`
   - Base branch: typically `main`, `develop`, or custom per team

2. **Documentation folder scaffolding**
   - Create directory: `docs/features/{ticket-slug}/` or similar structure
   - Copy templates from canonical location (e.g., `docs/templates/`)
   - Pre-fill ticket metadata: title, description, acceptance criteria
   - Generate stubs: `design-note.md`, `prd-lite.md`, `test-plan.md`, etc.

3. **Draft pull request creation**
   - Create draft PR linking back to issue
   - Pre-fill PR description with ticket context
   - Add checklist derived from acceptance criteria
   - Link to scaffolded documentation

**Auto-generating requirements with [PRDEngine](https://github.com/kbot-ships/PRDEngine):** Instead of copying blank templates, the scaffolding step can invoke PRDEngine to generate a first-draft artifact from the ticket's title, description, and acceptance criteria. PRDEngine assesses complexity and routes to the right tier:
- **Lightweight** -- simple features (~1 page)
- **Standard** -- typical work (~3-5 pages, adds API design and data model)
- **Comprehensive** -- cross-cutting changes (~8-15 pages)

**Important:** Scaffolding should feel like helpful automation, not bureaucratic overhead. If engineers find it burdensome, simplify or make it opt-in.

## Implementation Approach

### Architecture Options

**Option 1: Webhook listener service (recommended for most teams)**
- Lightweight service (Node.js, Python, Go) hosted on your infrastructure
- Listen for issue tracker webhooks (e.g., Linear "issue.update", Jira "issue_updated")
- Validate state transitions and enforce requirements
- Pros: Full control, easy to customize, works offline
- Cons: Requires hosting and maintenance

**Option 2: GitHub Actions (for GitHub-centric teams)**
- Trigger on issue tracker webhook → GitHub Actions workflow
- Use Actions to validate and scaffold
- Pros: No separate hosting, integrates with existing CI/CD
- Cons: Limited to GitHub ecosystem, slower execution

**Option 3: Serverless functions (AWS Lambda, Vercel, Cloudflare Workers)**
- Webhook → serverless function → validation and scaffolding
- Pros: Minimal infrastructure, scales automatically
- Cons: Cold start latency, vendor lock-in

### Reference Implementation: Linear Webhooks

This example uses Linear as the issue tracker, but the pattern adapts to Jira, Shortcut, GitHub Issues, GitLab Issues, or custom trackers.

**Webhook payload structure (Linear example):**
```json
{
  "action": "update",
  "data": {
    "id": "issue-123",
    "title": "Add user profile editing",
    "state": {
      "name": "In Progress"
    },
    "labels": [
      {"name": "interface"}
    ],
    "description": "...",
    "customFields": {
      "definition_of_done": "...",
      "acceptance_criteria": "..."
    }
  },
  "updatedFrom": {
    "state": {
      "name": "Todo"
    }
  }
}
```

**Adapting to other trackers:**
- **Jira:** Use "issue_updated" webhook, check `changelog` for status transition
- **GitHub Issues:** Use "issues" webhook with "edited" or "labeled" action
- **GitLab Issues:** Use "Issue Hook" webhook
- **Shortcut:** Use "story-update" webhook

### Phased Rollout

**Phase 1: Validation + Comment (enforce gate)**
- Listen for issue state change webhooks → "In Progress"
- Check for trigger labels (e.g., `interface`, `contract`)
- Validate required fields and links
- If validation fails:
  - Use API to revert status to previous state
  - Post explanatory comment with template links and examples
  - Optionally notify in team chat channel
- If validation succeeds:
  - Allow transition (no action needed)

**Phase 2: Auto-Scaffolding (reduce friction)**
- On successful validation, trigger scaffolding automation
- Create feature branch (if not already automated)
- Scaffold documentation directory structure
- Copy and customize templates with ticket metadata
- Create draft PR via API with ticket link in description
- Post success comment with links to scaffolded resources

**Phase 3: Completion Gate (close the loop)**
- Bot checks if acceptance criteria are met before allowing transition to "Done"
- Validates that PR exists and is linked to ticket
- Confirms design documentation is present (if required)
- Optional: Check that PR has passing CI, code review approval, etc.

## Success Criteria

1. **Zero gated tickets reach "In Progress" without required fields**
   - Measure: Audit issue transitions weekly
   - Target: 100% compliance after 2-week adoption period

2. **Engineers report net positive experience**
   - Measure: Survey after 1 month
   - Target: >70% report scaffolding saves time

3. **Measurable reduction in rework due to missing requirements**
   - Measure: Track PR rewrite rate (substantive changes after initial implementation)
   - Target: 30% reduction in rework PRs after 2 months

4. **Reduced time from "requirements unclear" to "clarified"**
   - Measure: Time between "In Progress" and first meaningful commit
   - Target: Decrease by 25% (faster clarification at gate)

5. **Consistent documentation presence**
   - Measure: % of completed interface/contract work with design documentation
   - Target: >90% compliance

## Flow Diagram

```
Ticket → State Change to "In Progress"
    │
    ├── Has trigger label? (e.g., interface, contract, ux-facing)
    │       │
    │       ├── NO → Allow transition (no gate)
    │       │
    │       └── YES → Validate required fields
    │               │
    │               ├── Fields MISSING → Block + comment with guidance
    │               │                    Revert status to previous state
    │               │                    Notify in team chat (optional)
    │               │
    │               └── Fields PRESENT → Allow + auto-scaffold (Phase 2)
    │                       │
    │                       ├── Create feature branch (if not automated)
    │                       │
    │                       ├── Scaffold documentation directory
    │                       │   ├── design-note.md (from template)
    │                       │   ├── prd-lite.md (from template)
    │                       │   ├── test-plan.md (from template)
    │                       │   └── acceptance-criteria.md (from ticket)
    │                       │
    │                       └── Create draft PR
    │                           ├── Link to issue
    │                           ├── Pre-filled description
    │                           └── Checklist from acceptance criteria
```

## Open Questions for Your Team

1. **Field configuration:** What exact fields should you require? (Custom fields vs description sections)
2. **Label taxonomy:** What labels trigger the gate? (Start narrow, expand based on data)
3. **Notification channels:** Should the bot post in chat (Slack/Teams/Discord) as well as issue comments?
4. **Owner assignment:** Who builds and maintains this automation? (DevOps, platform team, infrastructure?)
5. **Template location:** Where do you store canonical templates? (In repo, wiki, separate docs repo?)
6. **Completion gate:** Should Phase 3 block "Done" transitions or just warn? (Block for higher quality, warn for flexibility)
7. **Exemption mechanism:** How do engineers request exemption for edge cases? (Override label, manual approval, time-based bypass?)
8. **Rollout strategy:** Pilot with one team first? Gradual label expansion? Hard cutover?

## Getting Started

1. Choose your issue tracker (Linear, Jira, GitHub Issues, GitLab)
2. Define 2-3 trigger labels (start narrow)
3. Identify required fields (start with DoD + acceptance criteria)
4. Fork the [reference implementation](reference-implementation/) and wire in your tracker's API
5. Pilot with one team for 2 weeks
6. Gather feedback, iterate, then roll out
