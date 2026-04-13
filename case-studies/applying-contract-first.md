# How to Apply Contract-First Engineering

A practical walkthrough: applying the 4-layer model to a real feature.

---

## The Scenario

Your team needs to build a "Team Dashboard" feature. The request comes in as a Slack message: "We need a dashboard where managers can see their team's recent activity and metrics."

Sounds simple. But there are a dozen ways to interpret "recent activity" and "metrics." Do you just start coding? Or do you apply the contract-first approach?

This guide walks through the latter.

## The 4-Layer Process

### Layer 1: Intent (Discovery Conversations)

**Don't start with a ticket. Start with conversations.**

Run 2-3 short discovery sessions with stakeholders to understand what the dashboard actually needs to do. Not one big kickoff meeting. Not a requirements document dropped over the wall. Multiple iterative conversations that progressively clarify intent.

**Example questions:**
- What decisions will managers make using this dashboard?
- What does "recent" mean? Last 7 days? 30 days? Configurable?
- What metrics matter most? Task completion? Time spent? Code reviews?
- Who else will use this besides managers? Team members themselves?

**Key insight**: The first conversation reveals what people *think* they want. The second and third conversations reveal what they *actually* need.

**Output**: Shared understanding of the problem space and user needs.

### Layer 2: Design (Value Streams → Milestones)

**Translate intent into structured delivery.**

Take the output from discovery and decompose it into value streams. Then break those value streams into milestones that represent incremental value delivery.

**Example value streams:**
1. Managers can view their team roster
2. Managers can see individual activity summaries
3. Managers can track team-wide metrics
4. Managers can filter by time range

**Example milestones (in Linear):**
- M1: Backend API for team roster data
- M2: UI component for team list view
- M3: Backend API for activity aggregation
- M4: UI component for activity timeline
- M5: Backend API for metrics calculation
- M6: UI component for metrics dashboard

**Key insight**: Having milestones before coding starts changes the engineering conversation. Engineers can see the shape of the work and identify sequencing issues early.

**Output**: Structured breakdown of *what value gets delivered when*.

### Layer 3: Contract (Milestones → Requirements → PRD)

**Map milestones to specific requirements, then to acceptance criteria.**

This is the contract -- testable intent that engineers can build against. The PRD doesn't have to be 50 pages. It just has to be explicit about:
- What success looks like (acceptance criteria)
- What the feature does NOT do (non-goals)
- How the pieces fit together (traceability)

**Example PRD sections:**

**Acceptance Criteria:**
- Backend API returns team roster with member names, roles, last active timestamp
- UI displays team members in sortable table format
- Activity timeline shows commits, PRs, reviews from last 30 days by default
- Metrics dashboard calculates: avg PR review time, task completion rate, active days per week
- Time range filter supports: 7d, 30d, 90d options

**Non-Goals:**
- Custom metric definitions (future phase)
- Export to PDF/CSV (not requested)
- Real-time updates (daily refresh is sufficient)
- Cross-team comparisons (single team view only)

**API Contracts:**
```
GET /api/teams/{team_id}/roster
GET /api/teams/{team_id}/activity?days=30
GET /api/teams/{team_id}/metrics?days=30
```

**Key insight**: The PRD forces clarity on edge cases and non-goals that would have otherwise surfaced during code review as "wait, should this also handle X?"

**Output**: Lightweight but explicit contract that engineers can build against.

### Layer 4: Delivery (Engineers Build to Contract)

**Engineers receive a PRD with clear acceptance criteria, not an ambiguous ticket.**

They build to the contract. Code review confirms alignment with acceptance criteria. No surprises. No "I thought we were building Y but you built Z."

**Example ticket:**
```
Title: Implement Team Dashboard API - Activity Endpoint

Milestone: M3 - Backend API for activity aggregation
PRD: [link to PRD]

Acceptance Criteria:
- Returns last N days of activity (default 30, max 90)
- Includes: commits, PRs opened, PRs reviewed, comments made
- Groups by date and member
- Returns 200 with data array, 404 if team not found

API Contract:
GET /api/teams/{team_id}/activity?days=30

Non-Goals:
- Real-time streaming (daily batch is fine)
- Cross-team aggregation (single team only)
```

**Key insight**: The engineer knows exactly what to build, what counts as done, and what's explicitly out of scope.

**Output**: Code that aligns with contract on first iteration.

## What the Process Catches

Real examples from applying this model:

### 1. Assumption Surfacing

**Without contract-first:**
- PM assumes "recent activity" means last 7 days
- Engineer assumes it means "since last login"
- Designer assumes it's user-configurable

**With contract-first:**
- Discovery conversations surface the conflict early
- Team agrees on 30-day default with filter options
- Everyone builds to the same definition

### 2. Dependency Discovery

**Without contract-first:**
- Frontend engineer starts building UI
- Integration reveals backend API doesn't exist yet
- Backend work becomes "blocker" mid-sprint

**With contract-first:**
- Milestone decomposition exposes API dependency upfront
- M1 (Backend API) explicitly comes before M2 (UI)
- Team sequences work correctly from the start

### 3. Scope Control

**Without contract-first:**
- Mid-implementation: "Could we also show code coverage metrics?"
- Mid-implementation: "What about exporting to PDF?"
- Mid-implementation: "Can we compare multiple teams?"

**With contract-first:**
- PRD's non-goals section catches these early
- Response: "Not in scope for this phase, let's discuss for next iteration"
- Three potential scope creeps prevented during implementation

## Before vs After

### Before (No Contract)

1. Ticket: "Build Team Dashboard"
2. Engineer interprets based on limited context
3. Engineer builds plausible implementation
4. Code review reveals misalignment with PM's mental model
5. Rework cycle
6. Repeat until convergence

**Result**: Working feature, but 2-3 rework cycles and accumulated frustration.

**Common failure modes:**
- "I thought you meant X, not Y"
- "Why didn't you also build Z?"
- "This works but it's not what we asked for"

### After (Contract-First)

1. Discovery conversations surface intent and assumptions
2. Value streams decomposed into milestones
3. PRD defines acceptance criteria and non-goals
4. Engineer builds to contract
5. Code review confirms alignment with acceptance criteria
6. Stakeholder validation against PRD

**Result**: Working feature, first iteration aligned, team confidence high.

**What changed:**
- Shared understanding exists before coding
- Engineers build to explicit contract, not interpretation
- Scope is protected by documented non-goals

## Practical Lessons

### What Works

**Multiple small conversations beat one big meeting**
- Discovery is iterative, not one-shot
- 3 x 30-minute sessions > 1 x 90-minute session
- Each conversation clarifies what the previous one missed

**Milestones before code**
- Having the structure visible changes how engineers approach work
- Sequencing issues surface during planning, not integration
- Engineers can parallelize based on dependencies

**Lightweight PRDs work**
- The PRD doesn't have to be heavy. It just has to be explicit.
- 2-3 pages with clear acceptance criteria beats 20-page spec
- Non-goals section is as important as goals

**Non-goals prevent scope creep**
- Saying what you're NOT building protects the contract
- "Not in this phase" is easier to defend with written non-goals
- Future phases can revisit non-goals explicitly

### What to Avoid

**Don't skip discovery**
- Starting with milestones before understanding intent leads to wrong decomposition
- You can't design the right contract without understanding the problem

**Don't make PRDs heavyweight**
- The goal is clarity, not documentation theater
- If the PRD takes longer to write than the feature takes to build, it's too heavy

**Don't let contract become unchangeable**
- Discovery during implementation is fine
- The contract should evolve if assumptions prove wrong
- But changes should be explicit and documented

## How to Get Started

### On your next feature:

**Week 1:**
1. Schedule 2-3 discovery conversations
2. Ask clarifying questions about intent
3. Document assumptions and open questions

**Week 2:**
1. Decompose into value streams
2. Create milestones in your project tracker
3. Identify dependencies and sequencing

**Week 3:**
1. Write lightweight PRD with acceptance criteria and non-goals
2. Review with stakeholders for alignment
3. Link milestones to PRD

**Week 4+:**
1. Create tickets from milestones with clear contracts
2. Engineers build to acceptance criteria
3. Code review validates against contract

### Start small

You don't need to apply this to every bug fix. Use it for:
- Features with UI and backend components
- Work that involves multiple stakeholders
- Anything where "requirements" feel ambiguous
- Projects that will take >1 week to implement

### Make it yours

This framework is a starting point. Adapt it to your team's workflow:
- Use whatever tools you already have (Linear, Jira, GitHub issues)
- Adjust the level of formality to match your team size
- Keep what works, drop what doesn't

## The Real Shift

Contract-first isn't about process overhead. It's about **front-loading clarity**.

The time spent in discovery and planning doesn't add time to the project. It prevents rework cycles that would have taken longer.

**The shift in mindset:**
- From "start coding and figure it out" → "understand first, then build"
- From "build what I think they want" → "build to explicit contract"
- From "fix during review" → "align before implementation"

**The result:**
- Fewer surprises during code review
- Less rework after "done"
- Higher confidence that you're building the right thing

---

**Bottom line**: This is a proven operating model. You can apply it to your next feature starting today.
