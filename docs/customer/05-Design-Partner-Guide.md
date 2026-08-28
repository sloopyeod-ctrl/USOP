# USOP Core v1.0 - Design Partner Guide

**Document:** 05-Design-Partner-Guide
**Release:** 0.14.0-dp2-final
**Status:** Frozen Design Partner Documentation
**Audience:** Design Partners, Security Leaders, Security Analysts, IAM Teams, Platform Teams

## Welcome

Thank you for participating in the USOP Core Design Partner Program.

You are one of the first organizations to evaluate the operational investigation model that future versions of USOP will inherit.

Your feedback helps validate not only the software, but also the workflow, deployment experience, documentation, decision quality, and operational value delivered by the platform.

## Purpose

The Design Partner Program exists to validate whether USOP Core improves the way security teams investigate, understand, and resolve security problems.

The primary question is:

> **Does USOP Core help your team understand what matters, why it matters, and what to do next more quickly and confidently than your current workflow?**

This is not a request to redesign the platform from scratch.

It is a structured validation of the permanent core investigation experience.

## Our Commitment

USOP will treat Design Partners as collaborators, not unpaid QA resources.

We commit to:

- responding professionally to documented issues;
- communicating known limitations;
- tracking reproducible defects;
- protecting sensitive customer information;
- never requesting production secrets, private keys, access tokens, or complete `.env` files;
- providing updated release artifacts when appropriate;
- preserving a stable investigation model unless customer evidence shows a material flaw;
- clearly distinguishing defects, usability issues, feature requests, and future roadmap ideas.

## Your Role

You are not being asked to test every possible technical edge case.

You are being asked to help validate whether the product works in a real security operating environment.

We want to understand whether USOP:

- reduces analyst effort;
- improves situational awareness;
- improves decision quality;
- preserves organizational knowledge;
- fits naturally into daily security operations;
- can be deployed and operated without undocumented developer assistance.

## What Success Looks Like

Success is not measured by the number of bugs found.

Success looks like:

- the deployment process is understandable;
- analysts identify what needs attention quickly;
- Mission Brief provides immediate orientation;
- Decision Intelligence is understandable and explainable;
- Organizational Experience improves confidence;
- Organizational Decisions preserve useful knowledge;
- Operational Pulse increases trust in the current state;
- the platform feels responsive and predictable;
- the team spends less time gathering information;
- the team would choose to continue using the workflow.

The strongest validation question is:

> **Would your team want to keep using USOP after the evaluation period ends?**

## What We Are Asking You To Evaluate

Please focus feedback on the current Core experience.

### Installation

Evaluate:

- clarity of the Installation Guide;
- deployment friction;
- configuration clarity;
- health verification;
- whether developer assistance was required.

### Security and Secrets

Evaluate:

- whether secret handling is understandable;
- whether security requirements are clearly documented;
- whether network requirements are reasonable;
- whether requested Entra permissions are understandable and justified;
- whether the deployment fits your organization's security expectations.

### Executive Dashboard

Evaluate:

- whether the current security posture is easy to understand;
- whether priorities are obvious;
- whether you know where to begin;
- whether the dashboard supports the 10-20 Second Rule.

### Mission Brief

Evaluate:

- whether the purpose of the investigation is clear;
- whether priority and objective are understandable;
- whether the brief reduces the time needed to orient yourself.

### Decision Intelligence

Evaluate:

- whether recommendations are understandable;
- whether the supporting evidence is sufficient;
- whether the reasoning is explainable;
- whether the information improves decision confidence.

### Operational Context

Evaluate:

- whether supporting identity, relationship, timeline, and exposure information is useful;
- whether context is available without overwhelming the primary decision.

### Organizational Experience

Evaluate:

- whether prior decisions and organizational knowledge are useful;
- whether historical information improves confidence;
- whether historical context remains subordinate to current material changes.

### Organizational Decisions

Evaluate:

- whether decision recording is understandable;
- whether the disposition reflects the organization's intent;
- whether future review behavior makes sense;
- whether the recorded decision feels reusable as organizational knowledge.

### Operational Pulse

Evaluate:

- whether current synchronization/readiness state is understandable;
- whether failures are obvious;
- whether supporting details are available without cluttering the main workflow;
- whether the panel increases trust in the investigation.

### Performance

Evaluate:

- page responsiveness;
- investigation load time;
- synchronization behavior;
- any delays that interrupt the analyst workflow.

### Documentation

Evaluate whether your team can:

- install USOP;
- configure secrets;
- review security requirements;
- use the investigation workflow;
- troubleshoot common issues

without requiring undocumented assistance.

## What We Are Not Asking You To Evaluate

Please do not treat the program as an invitation to redesign every aspect of USOP.

The Design Partner Program is not primarily asking:

- what product should replace the existing investigation model;
- what unrelated features should be added immediately;
- whether every future provider should be implemented now;
- whether the platform should become a replacement for existing authoritative security systems;
- whether every visual preference should become a product change.

Future ideas are welcome, but they should be identified separately from validation of the current Core experience.

## Suggested Evaluation Timeline

A five-day evaluation is recommended when practical.

### Day 1 - Deploy

- follow the Installation Guide;
- configure the supported secret path;
- complete security/network setup;
- verify health;
- complete first synchronization.

### Day 2 - Orient

- review the Executive Dashboard;
- identify priorities;
- open several investigations;
- review Mission Brief.

### Day 3 - Decide

- review Decision Intelligence;
- examine Operational Context;
- record Organizational Decisions.

### Day 4 - Learn

- review Organizational Experience;
- review prior decisions;
- review Operational Pulse;
- revisit previously handled investigations where appropriate.

### Day 5 - Operate

Use USOP as part of your normal security workflow.

At the end of the day, ask:

> **Did USOP reduce the time or effort required to reach confident decisions?**

The evaluation period may be extended where the environment does not generate enough representative activity within five days.

## Daily Evaluation Rhythm

USOP should be evaluated through real work rather than a feature tour alone.

A useful daily rhythm is:

```text
Open USOP
    |
    v
Eye-scan Executive Dashboard
    |
    v
Select Priority Investigation
    |
    v
Read Mission Brief
    |
    v
Review Decision Intelligence
    |
    v
Review Context and Experience
    |
    v
Record Organizational Decision
    |
    v
Verify Operational Pulse
    |
    v
Continue Normal Security Work
```

## Rapid Situational Awareness Evaluation

For each major page, consider:

- Did I understand what matters within 10-20 seconds?
- Did I understand why it matters?
- Did I know what to do next?
- Did the interface reduce or increase cognitive load?

If a page requires the analyst to first learn the interface before understanding the security problem, document that as a usability issue.

## Feedback Categories

Please classify feedback using one of these categories:

### Defect

The product behaves incorrectly or contradicts the documented release behavior.

### Security Concern

The behavior may create security, privacy, authorization, credential, network, or data-handling risk.

### Deployment Issue

The product cannot be installed, configured, upgraded, validated, or operated as documented.

### Documentation Issue

Instructions are missing, incorrect, ambiguous, outdated, or difficult to follow.

### Usability Issue

The workflow functions, but creates unnecessary confusion or cognitive effort.

### Performance Issue

The platform is too slow or resource-intensive for the expected workflow.

### Operational Value

Feedback about whether the capability improves security work.

### Feature Request

A new capability that is not required for the documented Core workflow to function.

### Future Roadmap Idea

A broader concept that may be useful in later provider or intelligence expansion.

## Feedback Format

Where possible, provide:

```text
Category:
Release Version:
Page / Workflow:
Description:
Expected Behavior:
Observed Behavior:
Operational Impact:
Reproduction Steps:
Suggested Improvement (optional):
Priority:
```

For screenshots or logs, remove sensitive information before sharing.

## Priority Guidance

Use this general scale:

### Critical

Prevents safe deployment, creates serious security risk, causes data integrity problems, or blocks the core investigation workflow.

### High

Materially interferes with normal use or significantly reduces trust in the product.

### Medium

Creates avoidable friction but has a reasonable workaround.

### Low

Minor issue, wording concern, polish item, or future improvement.

## Protecting Sensitive Information

Do not submit:

- client secrets;
- access tokens;
- refresh tokens;
- private keys;
- complete `.env` files;
- secret-provider credentials;
- sensitive customer records that are not necessary to reproduce the issue.

Sanitize screenshots and logs before sharing them.

If diagnostic information appears sensitive, ask before transmitting it.

## Known Boundaries

USOP Core v1.0 is intentionally focused.

The initial release centers on the permanent USOP investigation model and Microsoft Entra identity intelligence.

Future releases may expand into:

- additional identity providers;
- cloud providers;
- threat intelligence;
- vulnerability intelligence;
- compliance intelligence;
- asset intelligence;
- CIAM;
- SaaS governance;
- additional operational intelligence domains.

A planned capability should not be treated as operational until it appears in the applicable release documentation.

## Product Evolution Promise

USOP Core establishes the workflow future versions should inherit.

The goal is expansion without unnecessary relearning.

> **Organizations that learn USOP Core should immediately feel at home in future versions of USOP.**

Provider expansion and intelligence expansion should deepen the investigation rather than replace the user's mental model.

## What We Will Do With Your Feedback

Feedback will be reviewed and classified.

Possible outcomes include:

- defect correction;
- documentation correction;
- usability refinement;
- security remediation;
- performance improvement;
- deferred roadmap item;
- no change where the feedback conflicts with established product principles or would reduce overall product clarity.

Not every feature request will be implemented.

The objective is to preserve a coherent product while responding seriously to evidence from real users.

## Release Updates During Evaluation

If a release update is required during the Design Partner Program:

- the new release will receive a new version identifier;
- the change will be documented;
- the updated artifact will be validated before delivery;
- deployment or upgrade instructions will be provided;
- Design Partners should not patch the distributed USOP application independently unless explicitly coordinated.

The evaluated artifact should remain reproducible.

## Confidentiality and Redistribution

Design Partner materials may include pre-release software, documentation, workflows, screenshots, and roadmap information.

Unless otherwise agreed in writing:

- do not redistribute USOP release artifacts outside the participating organization;
- do not publish pre-release screenshots or documentation;
- do not share credentials or customer configuration with USOP;
- limit internal distribution to personnel participating in deployment, security review, evaluation, or leadership review.

Formal commercial, confidentiality, and licensing terms remain governed by the applicable agreement and release license.

## When To Stop Testing

Stop using the release and notify USOP if you identify:

- suspected credential exposure;
- unauthorized access;
- material data integrity issues;
- a critical security vulnerability;
- repeated application failure that may affect operational trust.

Do not continue testing a condition that may create unnecessary customer risk merely to collect additional evidence.

## Evaluation Completion Checklist

Before completing the Design Partner evaluation:

- [ ] Installation was evaluated.
- [ ] Secrets configuration was evaluated.
- [ ] Security/network documentation was reviewed.
- [ ] First synchronization was completed.
- [ ] Executive Dashboard was evaluated.
- [ ] Mission Brief was evaluated.
- [ ] Decision Intelligence was evaluated.
- [ ] Operational Context was evaluated.
- [ ] Organizational Experience was evaluated.
- [ ] Organizational Decision workflow was evaluated.
- [ ] Operational Pulse was evaluated.
- [ ] Performance was evaluated.
- [ ] Documentation was evaluated.
- [ ] At least one real or representative investigation was completed.
- [ ] Feedback Questionnaire was completed.
- [ ] Overall willingness to continue using USOP was assessed.

## Relationship to Other Customer Documents

Use this guide with:

- `01-Installation-Guide.md`
- `02-Secrets-Configuration-Guide.md`
- `03-Security-Deployment-Guide.md`
- `04-User-Guide.md`
- `06-Feedback-Questionnaire.md`
- `07-Release-Notes.md`
- `08-Known-Limitations.md`

The first four documents explain how to deploy and use USOP.

This guide explains what to evaluate.

The Feedback Questionnaire provides the structured evaluation record.

## Design Partner Success Criteria

> **A successful Design Partner evaluation demonstrates that USOP Core can be securely deployed, understood quickly, used during realistic security work, and trusted enough that the participating team would want to continue using the investigation workflow.**

The objective is not perfection on day one.

The objective is evidence that the permanent USOP Core model delivers meaningful operational value.

## Thank You

Thank you for helping validate USOP Core.

Your feedback helps shape future provider and intelligence expansion while protecting the stable operational experience that every future USOP customer should inherit.
