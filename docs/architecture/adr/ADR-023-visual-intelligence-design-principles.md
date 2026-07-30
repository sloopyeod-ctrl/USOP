# ADR-023: Visual Intelligence Design Principles

- **Status:** Accepted
- **Date:** 2026-07-30
- **Decision Makers:** USOP Architecture
- **Supersedes:** None
- **Superseded By:** None

---

# Context

USOP exists to reduce analyst effort while improving the quality, consistency, explainability, and auditability of security decisions.

Enterprise security analysts routinely process large volumes of information across identities, accounts, permissions, recommendations, policies, and audit records.

The primary challenge is not the availability of data.

The primary challenge is reducing the cognitive effort required to understand that data and make a defensible organizational decision.

The user experience therefore becomes part of the platform architecture.

Visual presentation must support operational decision making rather than simply displaying information.

---

# Problem

Traditional security products frequently present excessive information simultaneously.

Common consequences include:

- Dashboard fatigue
- Alert fatigue
- Excessive scrolling
- Hidden priorities
- Inconsistent visual language
- Increased analyst cognitive load

Although these interfaces may expose significant amounts of data, they often increase the amount of time required to reach an operational decision.

USOP requires a consistent design philosophy that prioritizes understanding over information density.

---

# Decision

USOP adopts Visual Intelligence as a core architectural principle.

Every screen shall be designed to reduce cognitive load while increasing decision quality.

Visual presentation becomes part of the platform architecture rather than a cosmetic concern.

---

# Design Principles

## Principle 1

### Eyes Before Mouse

Users should understand the current operational situation before interacting with the interface.

The first screen should immediately communicate:

- What am I looking at?
- Is action required?
- What should I do next?

---

## Principle 2

### Read Less. Understand More.

Visual hierarchy exists to reduce reading.

Typography, spacing, color, grouping, and layout should communicate priority before detailed reading begins.

Users should recognize important information through scanning rather than searching.

---

## Principle 3

### Progressive Disclosure

Present only the information required for the current decision.

Additional technical detail remains available without overwhelming the primary workflow.

Operational decisions should never require unnecessary navigation.

---

## Principle 4

### Explainability by Design

Every recommendation, draft, and organizational decision must remain traceable to authoritative evidence.

Visual presentation should reinforce explainability rather than obscure it.

Confidence indicators, evidence references, organizational guidance, and historical decisions remain visible throughout the decision process.

---

## Principle 5

### Human Accountability

USOP prepares information.

Analysts make decisions.

The interface shall clearly distinguish between:

- System-generated intelligence
- Analyst-authored documentation
- Organizational decisions

The platform never obscures human responsibility.

---

## Principle 6

### Consistent Intelligence Language

Equivalent concepts must always appear consistently throughout the platform.

Examples include:

- Confidence
- Intelligence Sources
- Organizational Guidance
- Decision Preparation
- Recommendations
- Organizational Memory

Users should never need to relearn terminology between workspaces.

---

## Principle 7

### Action-Oriented Interfaces

Every page must naturally guide the user toward the next operational action.

Interfaces should support workflows rather than collections of unrelated screens.

Users should understand what to do next without searching the interface.

---

## Principle 8

### Organizational Memory Visibility

Historical organizational knowledge should appear naturally during operational workflows.

Users should not perform separate searches to discover previous decisions or organizational guidance.

Organizational memory exists to support the current decision.

---

## Principle 9

### Trust but Verify

Operational decisions represent analyst intent.

Organizational risk changes only after synchronization verifies remediation.

The interface shall clearly distinguish between:

- Decision Recorded
- Pending Verification
- Verified Remediation

This distinction preserves trust in platform intelligence.

---

## Principle 10

### Scale Without Changing Experience

The user experience shall remain consistent regardless of organizational size.

A deployment supporting ten employees and one supporting two hundred thousand employees should provide the same workflow.

Infrastructure scales.

The experience does not.

---

# Implementation Guidance

Visual consistency shall be achieved through reusable interface patterns.

Examples include:

- Intelligence Headers
- Confidence Indicators
- Intelligence Source Cards
- Status Indicators
- Timeline Components
- Empty States
- Loading States

Reusable components shall be extracted only after multiple production implementations demonstrate common patterns.

USOP intentionally follows the principle:

> Build two. Extract one.

to avoid premature abstraction.

---

# Benefits

This architecture provides:

- Reduced analyst cognitive load
- Faster operational decisions
- Improved onboarding
- Improved consistency
- Better auditability
- Lower training requirements
- Stronger product identity
- Improved long-term maintainability

---

# Consequences

Positive

- Every workspace follows a common philosophy.
- New contributors understand the intended user experience.
- Product growth remains consistent.
- Interfaces scale without becoming visually fragmented.

Trade-offs

- Additional design discipline is required.
- New features may require review against these principles before implementation.
- Short-term development speed may decrease slightly in exchange for long-term product consistency.

---

# Decision Summary

USOP adopts Visual Intelligence as a core architectural principle.

Every interface exists to reduce cognitive load, improve explainability, preserve organizational knowledge, and accelerate high-quality security decisions.

Visual presentation is therefore considered part of the platform architecture rather than a separate user-interface concern.