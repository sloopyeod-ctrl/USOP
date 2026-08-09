# USOP Core v1.0 - User Guide

**Document:** 04-User-Guide  
**Release Track:** USOP Core v1.0 Release Candidate  
**Status:** Release Candidate Draft  
**Audience:** Security Analysts, IAM Analysts, Security Engineers, Design Partners

## Purpose

This guide introduces the operational investigation workflow used throughout USOP Core v1.0.

Its goal is to help an analyst understand how to move from organizational posture to a focused investigation, review decision intelligence and organizational experience, record an organizational decision, and verify the resulting operational state.

This guide assumes USOP has already been installed, configured, and connected to the supported identity provider.

## Expected Outcome

At the end of this guide, an analyst should understand:

- how to read the Executive Dashboard;
- how to identify what needs attention;
- how to open and navigate an investigation;
- how to use Mission Brief;
- how to review Decision Intelligence;
- how Operational Context supports a decision;
- how Organizational Experience preserves prior learning;
- how to record an Organizational Decision;
- how Operational Pulse communicates current readiness;
- how the investigation workflow remains stable as USOP expands.

## Product Principle

USOP is designed around Rapid Situational Awareness.

An experienced cybersecurity professional should be able to understand:

- what matters;
- why it matters;
- what should happen next

within approximately 10-20 seconds of opening a major USOP page.

The interface should reduce the time between recognizing a security problem and confidently taking action.

## Getting Started

After authentication and successful provider synchronization, USOP opens into the operational experience.

The normal workflow is:

```text
Executive Dashboard
        |
        v
Open Investigation
        |
        v
Mission Brief
        |
        v
Decision Intelligence
        |
        v
Operational Context
        |
        v
Organizational Experience
        |
        v
Organizational Decision
        |
        v
Operational Pulse
        |
        v
Verification
```

USOP is not designed as a collection of unrelated dashboards.

It is designed to guide an investigation.

## Executive Dashboard

### Primary Question

> **How healthy is my organization, and what needs attention first?**

The Executive Dashboard provides the highest-level operational view.

Use it to identify:

- critical and high-priority exposure;
- the most exposed identities;
- security posture trends;
- current operational activity;
- connector or synchronization health where supported.

The dashboard should allow a user to determine where to begin without opening multiple tools.

### What To Look For

Prioritize:

1. Critical exposure.
2. High exposure.
3. Identities with the greatest operational risk.
4. New or materially changed conditions.
5. Any platform or connector issue that may affect trust in the displayed intelligence.

### Screenshot

<!-- Add final repository screenshot path before RC1 freeze. -->

**Screenshot target:** Executive Dashboard

**Question answered by screenshot:** What requires attention first?

## Opening an Investigation

An investigation begins when the analyst selects an identity or operational condition that requires review.

The investigation is the analyst's work.

The page may be implemented as a workspace, but customer-facing terminology should remain investigation-oriented.

The analyst should not need to manually reconstruct the context from multiple systems before beginning.

## Mission Brief

### Primary Question

> **Why am I here?**

Mission Brief provides immediate orientation.

It should establish:

- the investigation subject;
- the primary objective;
- priority or severity;
- confidence;
- expected operational impact;
- the recommended direction, where available.

Mission Brief is intentionally placed before detailed evidence.

The analyst should understand the purpose of the investigation before reviewing supporting information.

### Screenshot

<!-- Add final repository screenshot path before RC1 freeze. -->

**Screenshot target:** Mission Brief

**Question answered by screenshot:** Why does this investigation matter?

## Decision Intelligence

### Primary Question

> **What evidence supports the recommendation?**

Decision Intelligence presents the reasoning and evidence that support the current recommendation.

Depending on the investigation, this may include:

- exposure conditions;
- authorization changes;
- risk factors;
- graph relationships;
- attack-path information;
- recommendation confidence;
- evidence contributing to the recommendation.

USOP should support analyst judgment rather than hide it behind unexplained automation.

### Analyst Guidance

Before recording a decision:

- review the recommendation;
- review the supporting evidence;
- confirm that the current operational state is trustworthy;
- compare the recommendation with relevant Organizational Experience;
- consider whether the condition represents a new material change.

### Screenshot

<!-- Add final repository screenshot path before RC1 freeze. -->

**Screenshot target:** Decision Intelligence

**Question answered by screenshot:** Why is USOP recommending this action?

## Operational Context

### Primary Question

> **What surrounding information matters to this decision?**

Operational Context provides the technical and organizational facts surrounding the investigation.

Depending on the supported release, context may include:

- identity details;
- role or group relationships;
- authorization state;
- relationship graph;
- exposure metrics;
- attack paths;
- timeline events;
- synchronization information.

Context supports the decision.

It should not compete with the decision itself.

## Identity and Relationship Graphs

Where graph intelligence is available, use it to understand relationships that are difficult to interpret from flat lists.

Graphs may help explain:

- direct and indirect relationships;
- privilege paths;
- attack paths;
- role or group associations;
- changes to effective exposure.

Graph visualizations should be treated as evidence, not as decoration.

## Timeline

The timeline helps reconstruct sequence and change over time.

Use it to understand:

- when material changes occurred;
- whether a condition is new;
- whether prior decisions remain relevant;
- whether a review interval has been superseded by a new authorization delta.

Historical information supports current operational priorities.

It should not outrank them.

## Organizational Experience

### Primary Question

> **What has my organization learned before?**

Organizational Experience presents relevant historical knowledge that may help inform the current investigation.

This may include:

- related organizational decisions;
- prior outcomes;
- review history;
- knowledge assets;
- previous exceptions;
- similar operational conditions.

Organizational Experience is advisory context.

A previous decision must not silently suppress a new material security change.

### Important Rule

If a new material authorization delta occurs, the analyst must receive a new decision opportunity even when a prior decision, exception, temporary assignment, or review window already exists.

The organization may learn from history.

History does not replace current judgment.

### Screenshot

<!-- Add final repository screenshot path before RC1 freeze. -->

**Screenshot target:** Organizational Experience

**Question answered by screenshot:** What has the organization learned that may help this decision?

## Recommendations

A Recommendation is an evidence-based proposed action.

It is not automatically a mandatory task.

USOP is intended to improve analyst judgment by presenting:

- the recommended direction;
- why the recommendation exists;
- the supporting evidence;
- the relevant organizational context;
- expected impact where available.

The analyst remains responsible for recording the organizational decision.

## Recording an Organizational Decision

### Primary Question

> **What is the organization's decision?**

An Organizational Decision records the outcome of the investigation on behalf of the organization.

Depending on the supported workflow, a decision may represent:

- acceptance;
- rejection;
- exception;
- deferred review;
- another governed disposition.

The exact available actions in RC1 must match the frozen application interface.

### Decision Quality

Before saving a decision, confirm:

- the recommendation was reviewed;
- supporting evidence was understood;
- material changes were considered;
- relevant Organizational Experience was reviewed;
- the selected disposition accurately reflects the organization's intent;
- any required future review is scheduled.

### Organizational Memory

Once recorded, the decision becomes part of the organization's operational knowledge.

Future investigations may use that history as context.

The goal is not simply to close an item.

The goal is to preserve why the organization made the decision.

## Review Scheduling

Where review scheduling is supported, accepted decisions and governed exceptions may be scheduled for periodic reassessment according to organizational policy.

A scheduled review window must never suppress a new material authorization delta.

New material changes require immediate analyst attention even when the prior decision has not yet reached its scheduled review date.

## Operational Pulse

### Primary Question

> **Can I trust the current operational state?**

Operational Pulse summarizes current synchronization and readiness information.

The compact view should communicate the operational state quickly.

Supporting synchronization details should remain available through progressive disclosure.

Operational Pulse may communicate:

- workspace readiness;
- latest refresh time;
- refresh duration;
- synchronization details;
- failures requiring attention.

### Screenshot

<!-- Add final repository screenshot path before RC1 freeze. -->

**Screenshot target:** Operational Pulse

**Question answered by screenshot:** Is the investigation operating on a trustworthy current state?

## Progressive Disclosure

USOP intentionally keeps secondary detail out of the primary eye-scan path.

Examples may include:

- synchronization details;
- historical decisions;
- timelines;
- supporting evidence.

Expand these details when needed.

Do not interpret a collapsed section as missing information.

## Investigation Complete

An investigation is complete when the required decision has been recorded and the analyst has verified the resulting operational state.

Completion should leave the organization with:

- a recorded decision;
- supporting evidence;
- decision history;
- review information where applicable;
- reusable organizational knowledge.

The investigation ends.

The organizational learning remains.

## Daily Analyst Workflow

A normal operating rhythm should be simple:

```text
1. Open USOP.
2. Eye-scan the Executive Dashboard.
3. Select the highest-priority investigation.
4. Read Mission Brief.
5. Review Decision Intelligence.
6. Review Operational Context as needed.
7. Review Organizational Experience.
8. Record the Organizational Decision.
9. Verify Operational Pulse.
10. Continue to the next investigation.
```

USOP is designed to reduce time spent gathering information so more time remains for security improvement, hardening, engineering, reporting, and other high-value work.

## Common Tasks

### Open an Investigation

From the Executive Dashboard or supported identity view, select the relevant investigation entry.

### Review a Recommendation

Open the investigation and review Decision Intelligence before taking action.

### Review Prior Decisions

Use Organizational Experience or the available decision-history view.

### Review Relationships

Open the relationship or identity graph where supported.

### Review Historical Sequence

Use the timeline where supported.

### Record a Decision

Use the Organizational Decision controls in the investigation.

### Verify Current Readiness

Review Operational Pulse.

## What To Do When Data Looks Wrong

Do not make an organizational decision based on intelligence you do not trust.

If data appears stale, incomplete, or inconsistent:

1. Review Operational Pulse.
2. Expand synchronization details.
3. Confirm the expected organization is active.
4. Confirm provider synchronization succeeded.
5. Check whether the issue is documented in Known Limitations.
6. Escalate using sanitized diagnostic information if required.

Do not attempt to correct source-of-truth data directly inside USOP unless the product explicitly provides a supported workflow for that action.

## When No Data Is Available

An empty state should explain why data is unavailable.

Possible causes include:

- provider not configured;
- synchronization not yet completed;
- provider access failure;
- no supported objects in the connected environment;
- feature not available in the current release.

USOP should not fabricate sample customer data to make an operational screen appear populated.

## When an Error Occurs

Use the error message and Operational Pulse to determine the failing area.

For deployment, network, secrets, or provider failures, consult:

- `01-Installation-Guide.md`
- `02-Secrets-Configuration-Guide.md`
- `03-Security-Deployment-Guide.md`
- `08-Known-Limitations.md`

Do not send credentials, tokens, private keys, or complete `.env` files during troubleshooting.

## Understanding Severity

USOP uses a consistent severity vocabulary:

- Critical
- High
- Medium
- Low

Severity colors and terminology should remain consistent throughout the product.

Color should not be the only signal used to communicate meaning.

## Understanding Product Growth

USOP Core v1.0 establishes the permanent investigation model.

Future releases may add:

- additional identity providers;
- cloud providers;
- vulnerability intelligence;
- threat intelligence;
- compliance intelligence;
- CIAM;
- SaaS governance;
- additional operational intelligence domains.

The goal is to expand intelligence without forcing existing users to relearn the core workflow.

> **Organizations that learn USOP Core should immediately feel at home in future versions of USOP.**

## First Investigation Checklist

Before considering the first investigation complete:

- [ ] I understand why the investigation exists.
- [ ] I reviewed Mission Brief.
- [ ] I reviewed the recommendation.
- [ ] I reviewed supporting evidence.
- [ ] I reviewed relevant Operational Context.
- [ ] I reviewed relevant Organizational Experience.
- [ ] I understand the selected organizational disposition.
- [ ] I recorded the Organizational Decision.
- [ ] I reviewed any required future review schedule.
- [ ] I verified Operational Pulse.
- [ ] I understand what happens next.

## Screenshot Freeze Requirements

Before RC1 is distributed, replace all screenshot placeholders in this guide with images from the exact frozen customer release.

Required screenshots:

- Executive Dashboard;
- Mission Brief;
- Decision Intelligence;
- Organizational Experience;
- Operational Pulse.

Screenshots must:

- contain no real customer secrets;
- contain no sensitive customer identifiers unless explicitly approved;
- match the frozen RC1 interface;
- use customer-facing terminology;
- show realistic but controlled demonstration data where appropriate;
- remain readable in rendered Markdown.

Do not use screenshots from an outdated development build.

## Relationship to Other Customer Documents

Read this guide with:

- `01-Installation-Guide.md`
- `02-Secrets-Configuration-Guide.md`
- `03-Security-Deployment-Guide.md`
- `05-Design-Partner-Guide.md`
- `08-Known-Limitations.md`

The first three guides establish deployment and security.

This guide explains the analyst workflow.

The Design Partner Guide explains what the customer should evaluate.

## User Success Criteria

> **An analyst should be able to understand what matters, why it matters, and what to do next within 10-20 seconds of opening a major USOP page, then complete the investigation without needing to reconstruct the operating picture across multiple disconnected tools.**

If the analyst must learn the interface before understanding the investigation, the release experience is not ready.
