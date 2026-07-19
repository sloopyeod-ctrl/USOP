# ADR-019: Organizational Memory and Evidence Architecture

**Status:** Accepted

**Date:** 2026-07-19

---

# Purpose

USOP exists to transform security operations from isolated technical activities
into cumulative organizational knowledge.

Traditional security platforms generate alerts, tickets, dashboards, and audit
logs, yet they rarely preserve the reasoning behind security decisions. As
experienced analysts leave an organization, years of practical knowledge often
leave with them. Future analysts are forced to rediscover previous decisions,
repeat investigations, and interpret historical actions without understanding
the evidence or rationale that originally justified them.

USOP rejects this model.

USOP is designed to ensure that security knowledge becomes a permanent
organizational asset rather than a temporary capability possessed by individual
employees.

Every meaningful security decision should leave the organization more
knowledgeable than it was before.

---

# Problem Statement

Modern cybersecurity platforms excel at collecting information.

Organizations routinely retain:

- Audit Logs
- Alerts
- Tickets
- Configuration History
- Vulnerability Findings
- Identity Data
- Cloud Telemetry
- Endpoint Events

These artifacts answer one important question:

**What happened?**

They rarely answer equally important questions.

- Why was this decision made?
- What evidence supported it?
- Which analyst approved it?
- What alternatives were considered?
- Which organizational policy influenced the outcome?
- Would we make the same decision today?
- What should future analysts learn from this event?

As experienced personnel leave an organization, these answers frequently
disappear with them.

The organization retains data while losing understanding.

This loss of institutional knowledge creates inconsistent security decisions,
duplicate investigations, increased operational cost, reduced audit
explainability, and unnecessary organizational risk.

USOP considers this loss of knowledge to be a security problem rather than
merely an operational inconvenience.

---

# Vision

USOP transforms individual security decisions into reusable organizational
knowledge through evidence, explainability, and human accountability.

Instead of treating each investigation as an isolated event, USOP preserves
the relationships among evidence, decisions, identities, accounts, knowledge,
policies, and outcomes so that future analysts begin where previous analysts
finished.

Institutional knowledge becomes cumulative rather than disposable.

The platform should become more valuable every day it is used because the
organization continually expands its understanding instead of repeatedly
relearning the same lessons.

---

# Mission

Transform security data into organizational knowledge through evidence,
explainable decisions, and human accountability.

---

# Core Philosophy

USOP does not exist to replace existing security products.

USOP connects them.

USOP explains them.

USOP preserves what the organization learns while using them.

Security tools already generate enormous amounts of information.

USOP provides the relationships, evidence, reasoning, and organizational memory
required to transform that information into actionable security intelligence.

USOP does not replace human judgment.

USOP strengthens it.

---

# Why USOP Exists

Every security analyst accumulates experience.

Every investigation teaches something.

Every difficult identity match reveals a pattern.

Every false positive exposes a weakness.

Every successful remediation improves organizational understanding.

Unfortunately, most organizations capture only the outcome while losing the
reasoning that produced it.

USOP exists to preserve that reasoning.

The platform ensures that every investigation, every security decision, and
every analyst contribution has the potential to become reusable organizational
knowledge.

The objective is not simply to close tickets.

The objective is to improve the organization's ability to make future security
decisions.

---

# Foundational Principles

The following principles govern every architectural decision made within USOP.

These principles are intended to remain stable as the platform evolves. New
features, engines, connectors, intelligence models, and commercial offerings
must reinforce these principles rather than contradict them.

## Principle 1 — Evidence Before Decision

USOP is an evidence platform before it is a recommendation platform.

Recommendations emerge from observable evidence rather than undocumented
assumptions or opaque automation.

Every recommendation presented by USOP should be reproducible from the evidence
available when it was generated.

Historical recommendations must remain explainable even after source systems
change.

---

## Principle 2 — Human Accountability

USOP assists security professionals.

It does not replace them.

Whenever uncertainty exists, USOP presents evidence, confidence, historical
context, and recommendations while leaving final authority with appropriately
authorized personnel.

Human accountability remains a core security control.

---

## Principle 3 — Organizational Knowledge Belongs to the Organization

Knowledge created by analysts is organizational intellectual property.

USOP preserves this knowledge independently of individual employees.

Security capability should improve as an organization gains operational
experience rather than reset whenever experienced personnel leave.

---

## Principle 4 — Explainability Is Mandatory

Every recommendation produced by USOP should answer four questions.

- Why is this recommendation being made?
- Which evidence supports it?
- How confident is USOP?
- Which systems or knowledge sources contributed to this conclusion?

Recommendations that cannot be explained should never be presented as
authoritative.

---

## Principle 5 — Unknown Is a Valid Security State

USOP never manufactures certainty.

When evidence is insufficient to establish ownership, authorization,
attribution, or security state with confidence, USOP explicitly represents that
uncertainty.

Unknown is preferable to incorrect.

Analyst review is preferable to unsafe automation.

---

## Principle 6 — Relationships Are First-Class

Security information should be connected rather than duplicated.

USOP preserves explicit relationships between identities, accounts, evidence,
recommendations, decisions, knowledge, policies, and historical events.

Relationships remain first-class architectural objects rather than
implementation details.

---

## Principle 7 — Platform Agnostic by Design

USOP does not revolve around any single technology vendor.

Microsoft Entra ID, AWS, Google Cloud, Snowflake, CrowdStrike, GitHub,
ServiceNow, USOP itself, and future systems are treated as independent sources
of security evidence.

No connected platform becomes the center of the architecture.

The canonical identity model remains platform neutral.

---

## Principle 8 — Core Must Stand Alone

USOP Core must provide significant operational value without requiring
additional commercial packages.

Connector Packs expand visibility.

Knowledge Packs enrich understanding.

Threat Packs improve prioritization.

Core remains a complete professional security platform.

---

## Principle 9 — Knowledge Evolves

Knowledge changes.

History does not.

USOP therefore separates reusable organizational knowledge from historical
security decisions.

Knowledge may evolve through controlled versioning.

Historical decisions preserve the knowledge version that existed when the
decision was made.

---

## Principle 10 — Evolution Before Replacement

USOP favors extending proven architecture rather than replacing it.

Existing capabilities should evolve whenever practical.

Architectural replacement should occur only when extension would compromise
clarity, maintainability, or long-term correctness.

This principle minimizes unnecessary disruption while preserving architectural
continuity.

---

# Core Domain Architecture

USOP separates organizational security knowledge into distinct but connected
domains.

Each domain has a single responsibility.

No domain should duplicate another domain's responsibilities.

Instead, Organizational Memory emerges from the relationships between them.

The core domains are:

```
Identity
    ↓
Source Accounts
    ↓
Evidence
    ↓
Recommendations
    ↓
Decisions
    ↓
Knowledge
    ↓
Policy References
    ↓
Organizational Memory
```

Each domain answers a different question.

---

## Identity

Identity represents a real person, service identity, workload, device identity,
or other security principal recognized by the organization.

Identity is platform neutral.

Identity does not belong to Microsoft Entra ID, AWS, Google Cloud, Snowflake,
CrowdStrike, or USOP.

Instead, Identity represents the canonical security subject to which one or
more platform-specific accounts may belong.

Identity answers:

- Who is this?
- What relationships exist?
- What overall risk exists?
- Which systems recognize this identity?

Identity becomes the center of Identity Intelligence.

---

## Source Accounts

Source Accounts represent identities as observed by individual systems.

Examples include:

- Microsoft Entra ID user
- AWS IAM Identity Center account
- Google Cloud principal
- Snowflake user
- CrowdStrike console account
- GitHub organization member
- USOP Platform User

Each Source Account belongs to exactly one source system.

Multiple Source Accounts may ultimately relate to a single canonical Identity.

USOP never assumes this relationship without sufficient evidence or approved
organizational policy.

---

## Evidence

Evidence represents observable facts.

Evidence is neither opinion nor recommendation.

Examples include:

- Authentication status
- Group membership
- Role assignment
- Privilege level
- Last sign-in
- Device ownership
- Platform recommendation
- Infrastructure inventory
- Threat intelligence
- Historical analyst observations

Evidence always records its source.

Evidence should answer:

- What was observed?
- When was it observed?
- Which system observed it?
- How reliable is the observation?

Evidence remains immutable.

If observations change, new evidence is created rather than rewriting
historical evidence.

---

## Recommendations

Recommendations interpret evidence.

Recommendations never replace evidence.

Recommendations explain possible actions based upon available observations.

Examples include:

- Enable MFA
- Remove inactive privilege
- Review excessive access
- Confirm identity ownership
- Investigate shared credentials

Recommendations include:

- Supporting evidence
- Confidence
- Recommendation type
- Source system
- Risk context

Recommendations are explainable.

Every recommendation must be reproducible from observable evidence.

---

## Decisions

A Decision represents accountable human judgment.

A Decision transforms recommendation into organizational action.

Every Decision preserves:

- Decision type
- Analyst
- Justification
- Supporting evidence
- Recommendation
- Confidence
- Approval
- Verification
- Review schedule
- Outcome

A Decision records what the organization decided at a specific point in time.

Historical Decisions never change.

---

## Knowledge

Knowledge represents reusable organizational experience.

Knowledge differs from Decisions.

A Decision explains:

"What did we decide?"

Knowledge explains:

"What should future analysts know?"

Examples include:

- Identity naming conventions
- Application ownership patterns
- Recurring investigation procedures
- Organization-specific exceptions
- Lessons learned
- Repeatable investigative techniques
- Verified operational guidance

Knowledge is reusable.

Knowledge may evolve through controlled versioning.

Knowledge is organizational intellectual property.

---

## Policy References

Policies provide interpretive context.

Policies do not independently make decisions.

Future Policy References may include:

- Company SSP
- Company SOP
- Company Directives
- Internal Standards
- NIST SP 800-53
- NIST SP 800-171
- ISO 27001
- CMMC
- GDPR
- Vendor recommendations

Policy References explain why evidence or recommendations matter within an
enabled organizational context.

Policies enrich Decisions.

Policies do not replace analyst judgment.

---

# Organizational Memory

Organizational Memory is not a database table.

It is an architectural capability.

Organizational Memory emerges through the relationships among:

- Evidence
- Recommendations
- Decisions
- Knowledge
- Policies
- Audit History

The result is a continuously expanding organizational understanding of
security operations.

USOP therefore preserves not only what happened, but why it happened and what
future analysts should understand before making similar decisions.

---

# Relationship Model

USOP intentionally favors explicit relationships over duplicated data.

```
Canonical Identity
        │
        ├──────── Source Accounts
        │
        ├──────── Evidence
        │
        ├──────── Recommendations
        │
        ├──────── Decisions
        │              │
        │              ├──── Evidence References
        │              ├──── Knowledge References
        │              ├──── Related Decisions
        │              └──── Audit History
        │
        └──────── Organizational Knowledge
                        │
                        ├──── Policy References
                        ├──── Framework References
                        └──── Related Knowledge
```

Every relationship remains explicit.

USOP avoids copying information whenever practical.

Relationship-first architecture preserves consistency while supporting future
expansion.

---

# Identity Resolution

Identity Resolution demonstrates the Organizational Memory architecture.

USOP may calculate candidate identity matches.

Examples include:

- Username similarity
- Email similarity
- Display name similarity
- Organizational context
- Manager relationships
- Historical mappings
- Authentication claims
- Immutable provider identifiers

Candidate matches remain recommendations.

USOP shall not permanently attach uncertain Source Accounts to canonical
Identities without deterministic verification or authorized human approval.

Analysts remain responsible for confirming or rejecting ambiguous identity
relationships.

Their reasoning becomes part of Organizational Memory.

Future analysts benefit from that accumulated experience.

---

# Architectural Outcome

The Organizational Memory architecture ensures that every meaningful security
activity contributes to the long-term capability of the organization.

Evidence becomes Recommendations.

Recommendations become Decisions.

Decisions produce Knowledge.

Knowledge strengthens future Decisions.

As a result, USOP becomes more valuable every day it is used.

Security knowledge compounds.

It never disappears.
