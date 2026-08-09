# USOP Product Design Standards

**Version:** 1.0  
**Status:** Approved  
**Audience:** Product Owners, Architects, Engineers, UX Designers, Contributors

Every design decision in USOP should improve Rapid Situational Awareness by reducing the time between recognizing a security problem and confidently taking action.
---

## Purpose

This document defines the product design philosophy of the Unified Security Operations Platform (USOP).

Architectural Decision Records (ADRs) explain **why the platform is engineered the way it is**.

This document explains **how the platform should feel to the people who use it**.

Every future feature, page, workflow, and module should be evaluated against these standards before implementation.

---

## Product Mission

USOP exists to give cybersecurity professionals their time back.

The platform does this by transforming operational truth into clear, actionable investigations that reduce cognitive load and improve decision quality.

USOP is not designed to present more information.

USOP is designed to present the **right information at the right time**.

---

## Rapid Situational Awareness

### Purpose

Every major page in USOP should provide enough operational context for an experienced cybersecurity professional to understand the current situation within **10–20 seconds**.

The platform should reduce the time required to identify:

- what requires attention,
- why it matters,
- what should happen next.

This principle exists to minimize cognitive load before detailed investigation begins.

---

### The 10–20 Second Rule

Within 10–20 seconds of opening any major page, an experienced analyst should be able to answer that page's primary operational question.

The goal is not to display the greatest amount of information.

The goal is to display the **most important information first**.

Supporting information should remain immediately available through progressive disclosure without competing for attention.

---

### Application

#### Executive Dashboard

Within 10–20 seconds the user should understand:

- Overall organizational health.
- Immediate operational priorities.
- Which investigation should begin next.

---

#### Analyst Workspace

Within 10–20 seconds the user should understand:

- Why this investigation exists.
- The mission.
- The highest-priority issue.
- The expected decision.

---

#### Platform Administration

Within 10–20 seconds the user should understand:

- Platform health.
- Connector status.
- Whether administrator action is required.

---

### Design Implications

Rapid situational awareness should influence every product decision.

Information should be ordered by operational value rather than technical category.

Mission should appear before evidence.

Evidence should appear before history.

History should appear before reference material.

---

### Product Principle

If an analyst spends their first minute learning the interface instead of understanding the investigation, the interface has failed.

Every design decision should move the user from uncertainty to confident action as quickly as possible.

## Product Vision

Security professionals should spend their time making security decisions.

They should not spend their time searching multiple systems to collect information before making those decisions.

USOP provides operational context, organizational knowledge, and decision intelligence in one investigation workflow.

---

## Core Design Principles

### 1. One Question Per Page

Every page exists to answer exactly one primary question.

| Page | Primary Question |
| --- | --- |
| Executive Dashboard | How healthy is my organization? |
| Analyst Workspace | How do I solve this investigation? |
| Platform Administration | How is USOP configured? |

If a page answers multiple unrelated questions, the design should be reconsidered.

### 2. Investigation Before Information

USOP does not present collections of widgets.

USOP guides investigations.

Information should appear in the order an experienced security professional naturally thinks.

### 3. Progressive Disclosure

Only information necessary for the next decision should be immediately visible.

Supporting information should remain available without competing for attention.

Examples include Operational Pulse, Synchronization Details, timeline expansion, and historical organizational decisions.

### 4. Operational Truth

The frontend never invents intelligence.

It projects existing truth.

Business logic belongs in the backend.

Presentation belongs in the frontend.

### 5. Reduce Cognitive Load

Every feature should reduce analyst effort.

Removing unnecessary complexity is more valuable than adding additional functionality.

---

## Investigation Workflow

Every investigation should naturally follow this sequence:

```text
Mission
  ↓
Understand
  ↓
Review
  ↓
Decide
  ↓
Verify
```

Every future intelligence domain should integrate naturally into this sequence.

---

## Information Hierarchy

Information should appear in this order whenever practical:

1. Mission
2. Decision
3. Evidence
4. Operational Context
5. Organizational Knowledge
6. Recommended Actions
7. Verification

Historical information should never compete with immediate operational priorities.

---

## Product Vocabulary

USOP uses consistent terminology throughout the platform.

### Preferred Terms

- Investigation
- Mission Brief
- Operational Pulse
- Organizational Decision
- Recommendation
- Identity
- Exposure
- Organization

### Avoid

- Workspace, when **Investigation** is intended
- Overview, when **Mission Brief** is intended
- Task, when **Recommendation** is intended
- Analyst Response, when **Organizational Decision** is intended

The vocabulary of the product is part of the user experience.

---

## Visual Language

Severity colors are reserved.

| Severity | Color |
| --- | --- |
| Critical | Red |
| High | Orange |
| Medium | Blue |
| Low | Green |

These meanings never change.

Primary actions should be visually dominant.

Secondary actions should remain available without competing with the primary action.

Dark-theme surfaces must maintain explicit readable foreground contrast.

---

## User Experience Rules

1. Every component has one responsibility.
2. Every page answers one primary question.
3. Information should never compete for attention.
4. The analyst should always know what to do next.
5. Features should never be added at the expense of clarity.
6. Prefer progressive disclosure over permanently visible detail.
7. Historical context must not outrank current operational priorities.
8. Never present synthetic or unsupported operational status as fact.

---

## Product Quality Standard

A feature is not complete until it satisfies all of the following:

- Answers one clear question.
- Uses approved terminology.
- Fits naturally into the investigation workflow.
- Reduces cognitive load.
- Uses the established visual language.
- Preserves operational truth.
- Would be understandable to an experienced security analyst without explanation.

---

## Future Growth

Every future module inherits these standards, including Microsoft Entra ID, AWS, Google Cloud, Okta, CIAM, Threat Intelligence, Vulnerability Management, SaaS Governance, Compliance, Asset Intelligence, and future operational intelligence domains.

Consistency is a product feature.

---

## Product Philosophy

USOP is not a dashboard.

USOP is not another security tool.

USOP is an operational decision platform.

Every design decision should move the analyst from uncertainty to confident action with the least possible cognitive effort.

When uncertainty exists, simplicity should win.

When multiple solutions are possible, choose the one that allows an analyst to understand the investigation faster.

The best interface is one the analyst stops noticing because they are focused entirely on solving the security problem.

That is the standard every future contribution should strive to achieve.

---

## Guiding Principle

> Prior planning prevents piss poor performance.
