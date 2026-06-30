USOP Engineering Principles
Version

1.0

Purpose

The USOP Engineering Principles define the architectural philosophy of the platform.

These principles guide every engineering, architectural, and product decision made throughout the life of USOP.

Whenever competing solutions exist, the option that best aligns with these principles should be selected.

Principle 1 — Source of Truth
Philosophy

USOP does not become the authoritative source for enterprise operational data.

USOP consumes, correlates, and presents operational intelligence while authoritative systems continue to own operational records.

Why

Organizations already have mature systems for Identity Management, Asset Management, Vulnerability Management, Documentation, and Ticketing.

Replacing those systems is unnecessary.

USOP exists to connect them.

Examples
Microsoft Entra ID remains the Identity Provider.
GitHub remains the repository authority.
SharePoint remains the document authority.
NetBox remains the network inventory.
Tenable remains the vulnerability authority.

USOP references—not replaces.

Principle 2 — Trust but Verify
Philosophy

Automation should propose.

Engineers should approve.

Why

Security decisions often require human judgment.

USOP should accelerate engineering work without silently modifying operational truth.

Examples
Identity correlation
Service account ownership
Role changes
Risk acceptance
Evidence validation

High-confidence actions may be automated.

Operationally significant changes require review.

Principle 3 — Relationships Over Records
Philosophy

Operational context is more valuable than isolated records.

Why

Security Engineers rarely investigate a single object.

They investigate how objects relate to one another.

Questions USOP Should Answer

Who owns this?

What depends on this?

What breaks if this changes?

Which controls does this affect?

Which evidence supports this?

Principle 4 — Continuous Evidence
Philosophy

Evidence should be generated continuously through operational work.

Why

Engineers should not spend weeks assembling evidence before an assessment.

Audit readiness should be the natural byproduct of secure operations.

Goal

Always audit-ready.

Principle 5 — Knowledge Over Documentation
Philosophy

USOP preserves organizational understanding, not just documents.

Why

Documentation often explains what.

Engineers need to know why.

USOP captures engineering decisions, lessons learned, approvals, investigations, and operational history.

Principle 6 — Framework Agnostic
Philosophy

Operational work should support multiple compliance frameworks without redesign.

Why

Organizations frequently operate under multiple compliance requirements.

The same operational evidence should support:

CMMC
NIST 800-171
NIST 800-53
ISO 27001
SOC 2
FedRAMP
Future Frameworks
Principle 7 — Engine-First Architecture
Philosophy

Business logic belongs within platform engines.

User interfaces should remain thin presentation layers.

Benefits

Improved maintainability

Simplified testing

Consistent business logic

Future API support

Future mobile support

Principle 8 — Operational Intelligence Over Operational Noise
Philosophy

USOP should surface meaningful work—not every operational event.

Why

Security Engineers suffer from information overload.

USOP should prioritize significance over volume.

Every notification should answer:

Why does this matter?

Principle 9 — Engineer First
Philosophy

USOP is designed for the Security Engineer first.

Compliance, reporting, and management visibility are natural outcomes of helping engineers perform their work efficiently.

Success Metric

If engineers save time, everyone benefits.

Principle 10 — Security Operations Before Compliance
Philosophy

Strong security operations create compliant organizations.

Compliance should never become the primary objective.

Why

Compliance demonstrates security.

It does not create security.

USOP exists to improve operational security first.

Principle 11 — Modular by Design
Philosophy

Every major capability should be independently replaceable, extendable, and testable.

Why

Organizations change technologies over time.

Today's Entra ID connector may become tomorrow's Okta connector.

Today's Tenable connector may become tomorrow's Wiz connector.

USOP should adapt through modular connectors and engines rather than platform redesign.

Principle 12 — Configuration Over Customization
Philosophy

Organizations should configure USOP, not fork it.

Why

Naming conventions, workflows, review schedules, connectors, and compliance frameworks vary between organizations.

These differences should be handled through configuration wherever practical.

Principle 13 — Explainability
Philosophy

USOP should always explain why it made a recommendation.

Why

Security engineers need confidence in automation.

Every recommendation should include:

Source systems
Relationship reasoning
Confidence score
Supporting evidence
Impact analysis

Engineers should never have to trust a "black box."

Principle 14 — Human-Centered Automation
Philosophy

Automation exists to remove repetitive work—not human judgment.

Why

The platform should eliminate tasks like:

Copying data between systems
Building audit evidence manually
Chasing document links
Repeating the same access reviews

But it should preserve human review where security decisions have meaningful impact.

Principle 15 — Continuous Improvement
Philosophy

USOP should improve itself over time.

Why

Every accepted or rejected recommendation, workflow completion, review, and operational decision provides feedback that can refine future recommendations and automation.

The platform should become more accurate as organizations use it.
