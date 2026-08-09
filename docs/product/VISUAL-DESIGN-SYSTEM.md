# USOP Visual Design System

**Version:** 1.0
**Status:** Approved
**Audience:** Product Owners, Architects, Engineers, UX Designers, Contributors

## Purpose

The USOP Visual Design System defines the visual principles that govern every user-facing experience across the platform.

It exists to ensure that every page, module, workflow, and future capability feels like part of one coherent product.

The objective is not visual consistency alone. The objective is **operational consistency**.

Users should spend their attention understanding investigations, not learning the interface.

## Design Philosophy

Visual design exists to accelerate understanding.

Every visual element should contribute to Rapid Situational Awareness, reduced cognitive load, increased operational confidence, or faster decision making.

If a visual element does not improve one of these outcomes, it should be reconsidered.

## Rapid Situational Awareness

Every major page should communicate its primary operational message within **10–20 seconds**.

An experienced security professional should quickly understand what requires attention, why it matters, and what should happen next.

Visual hierarchy always takes precedence over visual complexity.

## Recognition Before Reading

Users should recognize severity, urgency, readiness, and the primary action before reading labels.

Recognition is faster than reading.

The design should take advantage of that without relying on color alone.

## Information Density

The objective is not to display less information.

The objective is to display the **most useful information first**.

Every visible element should justify its presence by helping the analyst understand the situation or reach a better decision.

Supporting information should remain immediately available through progressive disclosure.

## Information Hierarchy

Information should appear in this order whenever practical:

1. Mission
2. Decision
3. Evidence
4. Operational Context
5. Organizational Experience
6. Actions
7. Verification

Historical information supports operational decisions and should never compete with current operational priorities.

## Design Tokens

### Color

Color communicates operational meaning, never decoration.

| Meaning | Color | Purpose |
| --- | --- | --- |
| Critical | Red | Immediate operational attention |
| High | Orange | High analyst priority |
| Medium | Blue | Analyst review |
| Low | Green | Healthy or acceptable state |
| Informational | Cyan | Platform guidance |
| Neutral | Gray | Supporting metadata |

These meanings remain consistent throughout the product.

### Typography

| Level | Purpose |
| --- | --- |
| H4 | Page title |
| H5 | Major section title |
| Subtitle2 | Panel title |
| Body1 | Primary reading |
| Body2 | Supporting reading |
| Caption | Metadata |

### Spacing

Whitespace creates hierarchy. Consistent spacing reduces cognitive effort and communicates relationships between information.

### Elevation

Elevation communicates grouping and importance rather than decoration.

### Borders

Borders communicate grouping, selection, and operational state.

## Components

### Cards

Cards answer one question. Every card should have one responsibility, one purpose, and one operational objective.

### Buttons

Primary buttons are contained and advance the investigation.

Examples:
- Open Investigation
- Continue Investigation
- Save Organizational Decision

Secondary buttons are outlined and support navigation or optional actions.

Danger styling is reserved for destructive operations only.

### Chips

Chips communicate operational state, never decoration.

Filled chips communicate primary state. Outlined chips communicate supporting state.

### Icons

Icons reinforce understanding and never exist purely for decoration.

| Concept | Preferred Meaning |
| --- | --- |
| Mission | Flag |
| Investigation | Search |
| Decision | Gavel |
| Organization | Business |
| Timeline | Schedule |
| Operational Pulse | Check Circle |
| Relationship Graph | Hub |
| Risk | Warning |

### Alerts

Alerts communicate operational significance and must align with the reserved severity system.

### Progress Indicators

Progress indicators should communicate real progress or platform activity and must never imply unsupported precision.

### Tables

Tables should be used when structured comparison matters more than narrative flow.

### Graphs

Graphs exist to explain relationships or trends that are difficult to understand in text. They should not be added simply because data exists.

### Timelines

Timelines explain sequence, causality, and historical progression. History must remain subordinate to current operational priorities.

## Interaction Patterns

Preferred patterns include Progressive Disclosure, Immediate Primary Actions, Contextual Expansion, Confirmation Before Destructive Actions, Predictable Navigation, and Stable Investigation Flow.

## Progressive Disclosure

Only information required for the next decision should remain immediately visible.

Reference implementations include Operational Pulse, Synchronization Details, Historical Decisions, and Timeline.

## Loading States

Loading should reassure users that the platform is actively working.

## Empty States

Every empty state should explain what happened, why, and what the user should do next.

## Error States

Errors should explain the problem, operational impact, and recommended next action.

Implementation details belong in logs, not the user interface.

## Animation

Animation communicates state, never decoration.

Transitions should reinforce understanding and never distract from investigations.

## Accessibility

USOP should ensure:
- color is never the only indicator;
- text maintains sufficient contrast;
- primary actions remain obvious;
- layouts remain readable across supported display sizes;
- interactive controls remain keyboard-usable where practical;
- status and severity remain understandable without visual styling alone.

## Things We Never Do

We never:
- use color without meaning;
- invent operational truth;
- duplicate operational information unnecessarily;
- hide the next logical action;
- prioritize aesthetics over understanding;
- introduce multiple names for the same concept;
- increase cognitive load without improving decision quality;
- force users to hunt for important information;
- display historical information before current operational priorities;
- add visual complexity without operational value.

## Product Principle

> **Visual consistency builds operational trust.**

The interface should disappear. The investigation should remain.

Every visual decision should help the analyst understand the situation faster, reach a confident decision sooner, and continue the investigation without distraction.

## Relationship to Other Product Documents

This document complements:
- PRODUCT-DESIGN-STANDARDS.md
- PRODUCT-TERMINOLOGY.md
- PRODUCT-QUALITY-CHECKLIST.md

Together these documents define how USOP should think, communicate, present information, and evaluate product quality.
