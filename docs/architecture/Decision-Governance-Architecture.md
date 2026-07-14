# Decision Governance Architecture

**USOP Architecture Document**

**Version:** 1.0  
**Status:** Draft

---

## 1. Mission

USOP Decision Governance exists to capture, preserve, and explain security decisions at the moment they are made.

Its purpose is to reduce repetitive administrative work while improving accountability, audit readiness, review scheduling, and organizational knowledge.

Decision Governance is not intended to replace ticketing systems, GRC platforms, change-management systems, or compliance repositories.

USOP serves as the authoritative security decision record that those systems may consume.

---

## 2. Core Philosophy

Security engineers create value by reducing risk.

They should not repeatedly document the same decision across multiple systems.

USOP follows one guiding principle:

> **Write Once. Use Everywhere.**

A security decision should be recorded once and automatically become available for:

- Audit evidence
- Compliance reporting
- Executive reporting
- Review workflows
- Governance dashboards
- Historical investigations
- Future engineering decisions
- External ticketing and GRC integrations

---

## 3. Force Multiplier Principle

USOP should reduce repeated analysis, repeated data collection, and repeated documentation.

A capability belongs in Decision Governance when it:

- Reduces analyst workload
- Preserves security knowledge
- Improves accountability
- Prevents repeated investigation
- Automates audit documentation
- Schedules required follow-up
- Improves the quality of future decisions

USOP must remain a force multiplier rather than becoming another administrative burden or security liability.

---

## 4. Guiding Principles

### 4.1 Evidence Before Opinion

Every recommendation and decision must be traceable to observable evidence.

USOP must not invent conclusions that cannot be explained.

---

### 4.2 Organizations Define Governance

USOP recommends security actions.

Organizations define governance requirements.

Approval workflows, review intervals, justification requirements, ticket references, and verification requirements are controlled by configurable governance policies—not hardcoded application logic.

---

### 4.3 Preserve Organizational Knowledge

Every decision becomes part of the organization’s security memory.

Future analysts should be able to determine:

- What decision was made
- Why it was made
- Who made it
- Who approved it
- What evidence supported it
- When it should be reviewed
- Whether it was later corrected
- Whether remediation was verified

This information should be available without rediscovering the original context.

---

### 4.4 Single Authoritative Decision

One decision record should support many organizational functions.

The decision record becomes the authoritative source for:

- Audit history
- Review scheduling
- Compliance evidence
- Executive reporting
- Governance dashboards
- Historical investigations
- External integrations

---

### 4.5 Secure by Design

Decision Governance must not weaken the security posture it is designed to improve.

The platform must:

- Enforce workflow validation in the backend
- Avoid placing authorization decisions in frontend logic
- Prevent secrets and credentials from entering decision evidence
- Preserve immutable audit history
- Apply least privilege to governance administration
- Record trustworthy server-generated timestamps
- Distinguish authenticated actors from user-supplied text
- Fail safely when evidence or policy is incomplete

---

## 5. Decision Lifecycle

```text
Evidence
    ↓
Recommendation
    ↓
Decision Opportunity
    ↓
Analyst Decision
    ↓
Governance Validation
    ↓
Approval, if required by policy
    ↓
Review
    ↓
Verification
    ↓
Closure
    ↓
Historical Record

The lifecycle must preserve both current state and append-only history.

#6. Canonical Decision Types

Version 1 supports the following decision types.

## 6.1 Accept Risk

The organization intentionally accepts an identified security risk.

Acceptance may be:

Permanent
Temporary

Temporary acceptance may include a future review date.

Whether approval, justification, or review scheduling is required is determined by organizational policy.

#6.2 Correct Risk

The organization remediates or mitigates the identified issue.

Examples include:

Removing privileged access
Enabling MFA
Disabling dormant accounts
Changing role scope
Updating policy
Applying a compensating control

Corrective actions may require later verification depending on governance policy.

#6.3 Escalate

Responsibility is transferred to another owner, team, or authority.

Potential recipients include:

Identity team
Cloud team
Application owner
Security leadership
Business owner
Executive review
External service provider

Escalation may include a due date, ticket reference, and assigned owner.

#6.4 Defer

The organization intentionally delays remediation.

Deferred decisions should support a future review or action date.

Whether a review date is mandatory is controlled through governance policy.

#6.5 False Positive

The organization determines that the finding or recommendation is not applicable.

False-positive decisions remain historically visible and must include sufficient notes when required by policy.

#7. Decision Opportunity

A Decision Opportunity represents an actionable security issue that has not yet received an organizational decision.

It may reference:

Identity
Finding
Recommendation
Authorization classification
Exposure evidence
Risk assessment
Attack path
Policy violation
External alert or ticket

A Decision Opportunity becomes a Decision Record when an analyst records an action.

#8. Decision Record

Every analyst decision becomes a first-class governance object.

#8.1 Identity and References
Decision ID
Identity ID
Finding reference
Recommendation reference
Evidence snapshot reference
External ticket reference
Source system
Source identifier

#8.2 Decision State
Decision type
Status
Current owner
Created by
Created at
Updated by
Updated at

#8.3 Documentation
Justification
Analyst notes
Action taken
Supporting evidence
Compensating controls
Expected outcome

#8.4 Acceptance
Acceptance type
Permanent or temporary
Review due date
Acceptance expiration date

#8.5 Approval
Approval required
Approval status
Approved by
Approved at
Approval notes

#8.6 Escalation
Escalated to
Escalated at
Escalation reason
Target completion date
External ticket reference

#8.7 Verification
Verification required
Verified by
Verified at
Verification notes
Verification evidence

#8.8 Closure
Closed by
Closed at
Closure reason
Closure notes

#9. Decision Statuses

Version 1 should support a controlled vocabulary such as:

Draft
Open
Pending Approval
Approved
Rejected
In Progress
Accepted
Deferred
Escalated
Pending Verification
Verified
Closed
Review Due
Overdue
Reopened

Transitions must be validated by backend lifecycle rules.

#10. Governance Policy

Decision Governance behavior is controlled by organization-defined policies.

#10.1 Example Settings
Require approval
Require business justification
Require analyst notes
Require a review date
Require a review date for temporary acceptance
Allow permanent acceptance
Require a ticket reference
Require a business owner
Require verification
Require verification evidence
Default review interval
Maximum acceptance duration
Allowed approver roles
Escalation workflow
Automatic overdue handling

#10.2 Policy Defaults

Defaults should remain conservative but flexible.

USOP must not assume that one organization’s governance rules apply to another.

10.3 Policy Enforcement

The backend evaluates applicable policy before permitting a decision transition.

The frontend may display required fields, but it must not be the authoritative enforcement point.

#11. Review Scheduling

Decision records may create future review obligations.

Examples include:

Temporary risk acceptance review
Deferred remediation review
Escalation due date
Corrective-action verification
Periodic permanent-acceptance review

The system should support:

Upcoming reviews
Due-today reviews
Overdue reviews
Review reminders
Review completion
Review rescheduling
Decision reopening

#12. Audit History

Every meaningful transition generates an append-only audit event.

Examples include:

Decision created
Decision updated
Risk accepted
Corrective action recorded
Decision escalated
Decision deferred
False positive recorded
Approval requested
Approval granted
Approval rejected
Review scheduled
Review completed
Review date changed
Verification completed
Decision closed
Decision reopened

Audit history must preserve:

Actor
Timestamp
Event type
Entity type
Entity ID
Human-readable message
Relevant metadata

Historical events must never be silently overwritten.

#13. Decision History

The investigation experience should display a chronological decision history.

A future analyst should be able to understand:

Evidence identified
    ↓
Recommendation generated
    ↓
Risk accepted temporarily
    ↓
Approval recorded
    ↓
Review completed
    ↓
Corrective action started
    ↓
Remediation verified
    ↓
Decision closed

Decision history is organizational memory, not merely application logging.

#14. Decision Workspace

Every investigation begins with:

Decision summary
Evidence
Classification
Recommendations

Every investigation should support completion through:

Accept Risk
Correct Risk
Escalate
Defer
False Positive

The available fields and requirements are rendered dynamically from governance policy.

The Decision Workspace should clearly separate:

Current evidence
USOP recommendation
Organizational decision
Governance requirements
Historical record

#15. Write Once, Use Everywhere

A decision should be documented once.

The same authoritative Decision Record may then support:

Identity history
Audit evidence
Compliance evidence
Review scheduling
Governance dashboards
Executive reporting
POA&M workflows
ServiceNow integration
Jira integration
GRC integration
Future investigations

USOP should prevent engineers from rewriting the same explanation in multiple places.

#16. Relationship to Existing Governance Components

Decision Governance should extend the existing USOP governance architecture rather than duplicate it.

Existing capabilities include:

Access reviews
Review campaigns
Governance policies
Audit events
Review scheduling
Review state transitions

Decision Governance should reuse these patterns where appropriate while maintaining a clear distinction between:

Access Review
Security Decision
Audit Event
Governance Policy

A security decision may trigger a review, but a decision and a review are not the same object.

#17. External Integrations

Decision Governance is designed to integrate with external systems without replacing them.

Potential integrations include:

ServiceNow
Jira
Microsoft Planner
Archer
POA&M repositories
CMMC evidence packages
RMF documentation
Executive-reporting platforms
Compliance-management systems

External integrations should consume or reference the authoritative USOP Decision Record.

#18. Reporting

Decision Records should support reporting such as:

Accepted risks
Temporary acceptances
Permanent acceptances
Reviews due
Reviews overdue
Corrections in progress
Corrections verified
Escalations
False positives
Decisions by severity
Decisions by owner
Decisions by approver
Average time to decision
Average time to correction
Engineering time returned

#19. Success Criteria

Decision Governance succeeds when:

Engineers document decisions once.
Required follow-up is scheduled automatically.
Organizations retain complete decision history.
Auditors can trace security decisions without searching multiple systems.
New analysts can understand earlier decisions.
Governance policy remains customer configurable.
Corrective actions can be verified.
Administrative effort is reduced.
Security knowledge is preserved.
Engineers spend more time reducing risk than documenting it.

#20. Architectural Summary

USOP does not merely identify security risk.

USOP preserves the complete lifecycle of a security decision.

The platform transforms evidence into recommendations, recommendations into accountable organizational decisions, and decisions into reusable organizational knowledge.

USOP should remain a force multiplier by reducing repeated investigation and documentation while improving security, governance, and accountability.
