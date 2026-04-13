<p align="center">
  <img src="assets/banner.svg" alt="Execution Operating System" width="900"/>
</p>

---

## What is this

A lightweight framework for engineering teams that want to stop building plausible things that aren't the customer thing.

The core idea: **make intent testable before you build**, so rework becomes the exception.

---

## The problem: avoidable churn

Teams build features where the interface or contract intent was ambiguous:

- Dashboard that exposed raw data, but users needed actionable insights
- Powerful API with 20 endpoints, but the UI only needed 3 operations
- Feature X implemented, but customer actually needed Feature Y

Not pervasive, but completely avoidable. The cost is engineering time spent building the right thing twice.

---

## The model: contract-first

> Contract-first = UX flow and API contract reviewed together before build starts.

<p align="center">
  <img src="assets/flow-model.svg" alt="Intent → Design → Execution → Release" width="800"/>
</p>

Four layers. Nothing novel. The key constraint: UI must not drive API design in isolation. They're designed as a unit.

<p align="center">
  <img src="assets/example-chain.svg" alt="Ticket → UX mock + API contract → Build and review → Outcome" width="820"/>
</p>

If the mock or contract is missing, you build plausible outcomes that aren't the customer outcome. This chain prevents that.

---

## What's in this repo

| Folder | What it is | Start here if... |
|:-------|:-----------|:-----------------|
| **[`templates/`](templates/)** | Fill-in-the-blank artifacts for your next feature | You want to use the framework today |
| **[`case-studies/`](case-studies/)** | Walkthrough of the process applied to a real feature | You want to see what good looks like |
| **[`automation/`](automation/)** | Blueprint for ticket system gatekeeping | You want to build enforcement tooling |
| **[`decisions/`](decisions/)** | Decision template for adopting the framework | You're leading adoption for your team |

### Templates

| Template | Purpose | When to use |
|:---------|:--------|:------------|
| [PRD-lite](templates/prd-lite.md) | One-page problem/solution/criteria | Before design starts |
| [Design note](templates/design-note.md) | Technical approach, API impacts, data model, security | Before coding starts |
| [UX mock](templates/ux-mock.md) | Screen layout + user journey + API surface | Before coding starts |

Each template includes a filled-in example so you can see what good looks like.

---

## Tooling

This framework defines **what** to do. [**PRDEngine**](https://github.com/krti-commits/PRDEngine) automates the hardest part: generating the right-sized requirements artifact from a feature description.

| Template | PRDEngine tier | Output |
|:---------|:---------------|:-------|
| [PRD-lite](templates/prd-lite.md) | Lightweight | ~1 page scope with problem, criteria, and non-goals |
| [Design note](templates/design-note.md) | Standard | ~3-5 pages with API design, data model, security |
| [UX mock](templates/ux-mock.md) | Comprehensive+ | ~8-15 pages with user personas, cross-service impact |

The [ticket gatekeeping bot](automation/ticket-gatekeeping.md) can invoke PRDEngine to auto-generate these stubs when work starts -- enforcement and artifact creation in one step.

---

## How to get started

**If you're an engineer:** Copy a [template](templates/) for your next feature. Start with the [PRD-lite](templates/prd-lite.md) if requirements feel ambiguous, or the [design note](templates/design-note.md) if you're about to write code.

**If you're a tech lead:** Read the [case study](case-studies/applying-contract-first.md) to see contract-first applied end-to-end. Then review the [decision template](decisions/001-execution-operating-system.md) with your team.

**If you're building tooling:** The [ticket gatekeeping blueprint](automation/ticket-gatekeeping.md) is the highest-leverage automation target. It enforces this framework at the ticket system level.

---
