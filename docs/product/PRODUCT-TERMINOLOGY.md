# USOP Product Terminology

**Version:** 1.0  
**Status:** Approved  
**Audience:** Product Owners, Architects, Engineers, UX Designers, Technical Writers, Contributors

---

## Purpose

Language is part of the user experience.

Inconsistent terminology increases cognitive load, creates confusion, and makes software feel fragmented.

This document establishes the official vocabulary of the Unified Security Operations Platform (USOP).

Future user interfaces, documentation, demonstrations, training material, marketing content, and code comments should use the preferred terminology defined here.

The goal is simple:

> Users should never need to learn multiple words for the same concept.

---

## Product Philosophy

Words shape expectations.

The language used throughout USOP should reinforce the platform's purpose:

- Guide investigations.
- Reduce cognitive load.
- Support operational decision making.
- Build organizational knowledge.

Every preferred term exists because it better reflects the way cybersecurity professionals think and work.

---

## Core Terminology

### Investigation

**Preferred:** Investigation

**Definition:** The complete operational process of understanding, analyzing, deciding, documenting, and resolving a security condition.

**Why We Use It:** USOP guides analysts through investigations. An investigation has a beginning, evidence collection, analysis, decision making, documentation, and completion. The word "workspace" describes a location. The word "investigation" describes the analyst's activity. USOP centers on the analyst's activity.

**Avoid:** Workspace, Case, Review, unless those words literally describe those concepts.

**Examples:** Open Investigation, Continue Investigation, Investigation Complete.

---

### Mission Brief

**Preferred:** Mission Brief

**Definition:** The initial operational orientation presented before evidence review begins.

**Why We Use It:** Investigations should begin with purpose. Mission Brief establishes why the analyst is here, what matters most, the primary objective, operational confidence, and expected outcome before presenting detailed evidence.

**Avoid:** Overview, Summary, Dashboard.

---

### Operational Pulse

**Preferred:** Operational Pulse

**Definition:** Current synchronization and operational readiness.

**Why We Use It:** Operational Pulse communicates readiness rather than simply reporting status. It answers: "Can I trust this investigation?"

**Avoid:** Status, Status Panel, Sync Status.

---

### Organizational Decision

**Preferred:** Organizational Decision

**Definition:** The recorded operational decision made by an analyst on behalf of the organization.

**Why We Use It:** USOP preserves organizational knowledge. The decision belongs to the organization, not the individual analyst.

**Avoid:** Analyst Response, User Decision, Analyst Action.

---

### Recommendation

**Preferred:** Recommendation

**Definition:** An evidence-based proposed action.

**Why We Use It:** Recommendations support analyst judgment. Tasks imply mandatory execution. USOP assists decision making rather than replacing it.

**Avoid:** Task, Ticket, Work Item, Required Action, unless those concepts genuinely exist.

---

### Organization

**Preferred:** Organization

**Definition:** The customer environment being analyzed.

**Why We Use It:** Customers think in organizations. Platform architecture may use tenants internally. The user interface should always use Organization.

**Avoid:** Tenant, except in architectural documentation.

---

### Identity

**Preferred:** Identity

**Definition:** The human or non-human principal under investigation.

**Why We Use It:** Identity is the operational focus of USOP Core.

---

### Exposure

**Preferred:** Exposure

**Definition:** Operational risk resulting from identity posture, authorization, configuration, or related intelligence.

**Why We Use It:** Exposure better communicates operational risk than isolated vulnerability language.

---

### Decision Intelligence

**Preferred:** Decision Intelligence

**Definition:** Evidence-backed intelligence presented to help an analyst understand and resolve an investigation.

**Why We Use It:** The term emphasizes that intelligence exists to support a decision, not merely to display information.

**Avoid:** Decision Summary, Recommendation Engine, AI Decision.

---

### Organizational Experience

**Preferred:** Organizational Experience

**Definition:** Relevant historical decisions, patterns, and operational knowledge that help inform the current investigation.

**Why We Use It:** The organization learns over time. This term communicates accumulated experience without implying that past decisions automatically dictate current outcomes.

**Avoid:** Historical Decisions, Memory Panel, Prior Cases, unless specifically describing those narrower concepts.

---

### Operational Context

**Preferred:** Operational Context

**Definition:** The surrounding technical and organizational facts required to understand why an investigation matters.

**Why We Use It:** Context explains the environment around a decision without competing with the decision itself.

**Avoid:** Extra Information, Metadata, Additional Details.

---

### Analyst Workspace

**Preferred Use:** Analyst Workspace is acceptable as the technical page or route name.

**Customer-Facing Preference:** Investigation.

**Why We Use It:** The page is a workspace in implementation, but the user's activity is an investigation. Customer-facing actions should therefore favor Investigation terminology.

---

### Executive Dashboard

**Preferred:** Executive Dashboard

**Definition:** The operational summary that answers how healthy the organization is and what requires leadership attention.

**Why We Use It:** The term is intentionally reserved for the leadership-oriented entry page.

---

## Standard Button Labels

Use these labels consistently throughout the product.

| Purpose | Standard |
| --- | --- |
| Begin investigation | Open Investigation |
| Resume investigation | Continue Investigation |
| Record decision | Save Organizational Decision |
| Return home | Return to Dashboard |
| View supporting information | View Details |
| Expand supporting information | Show Details |
| Collapse supporting information | Hide Details |

Avoid creating alternative wording without strong justification.

---

## Severity Vocabulary

Severity terminology is reserved.

Always use:

- Critical
- High
- Medium
- Low

Never substitute:

- Major
- Minor
- Severe
- Warning
- Important

Consistency improves recognition.

---

## Workflow Vocabulary

The official investigation vocabulary follows this sequence:

```text
Executive Dashboard
  ↓
Investigation
  ↓
Mission Brief
  ↓
Decision Intelligence
  ↓
Operational Context
  ↓
Organizational Experience
  ↓
Organizational Decision
  ↓
Operational Pulse
  ↓
Investigation Complete
```

---

## Reserved Terms

Certain terms are reserved for architectural discussions and should generally not appear in customer-facing interfaces.

| Reserved | Preferred UI Term |
| --- | --- |
| Tenant | Organization |
| Projection Layer | Intelligence |
| Synchronization Result | Operational Pulse |
| Entity | Identity, when appropriate |
| Workspace | Investigation, when describing user activity |

---

## Future Naming Standard

Future modules should follow the same naming convention.

Examples:

- AWS Intelligence
- Google Cloud Intelligence
- Threat Intelligence
- Asset Intelligence
- Vulnerability Intelligence
- Compliance Intelligence
- SaaS Intelligence

Consistency allows future capabilities to integrate naturally into the existing product language.

---

## Naming Rules

When introducing new terminology, ask:

1. Does this reduce cognitive load?
2. Does it accurately describe analyst activity?
3. Is another approved word already available?
4. Will this still make sense five years from now?

If any answer is "No", reconsider the term.

---

## Product Principle

> Users should never need to learn multiple words for the same concept.

Consistent language is a product feature.

---

## Relationship to Other Product Documents

This document complements:

- PRODUCT-DESIGN-STANDARDS.md
- VISUAL-LANGUAGE.md
- PRODUCT-QUALITY-CHECKLIST.md

Together these documents define how USOP should look, behave, communicate, and evolve.

---

## Guiding Principle

> Prior planning prevents piss poor performance.

Carefully chosen language reduces ambiguity, strengthens consistency, and allows USOP to evolve without losing its identity.
