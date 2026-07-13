Sprint 11.1 Discovery Report
Purpose

Before implementing the Identity Decision Workspace, we performed a discovery review of the existing USOP platform.

The objective of this review was to identify mature capabilities already present within the repository so Version 1 could be built by extending proven architecture rather than creating parallel implementations.

This document records those findings and establishes the implementation plan for Sprint 11.1.

Sprint Objective

Build the first complete Identity Decision Workspace.

The goal is not to introduce new backend infrastructure.

The goal is to transform the existing Security Knowledge Graph into an analyst experience that supports faster and better security decisions.

Primary success criteria:

A security engineer should understand an identity in less than 30 seconds.

Discovery Findings
Identity Graph

Status:

✅ Existing

Current capability:

Identity traversal
Account traversal
Membership traversal
Group traversal
Role assignment traversal
Role traversal

Conclusion:

The Identity Graph already exists.

No replacement required.

Only enrichment.

Identity Intelligence Service

Status:

✅ Existing

Current capability:

Identity Graph integration
Exposure Engine integration
Recommendation Engine integration
Timeline integration
Access Analyzer integration

Conclusion:

Identity Intelligence already aggregates the major backend services.

Sprint 11.1 should extend existing responses rather than introduce another orchestration layer.

Analyst Workspace

Status:

✅ Existing

Current capability:

Workspace Header
Mission Status
Risk Summary
Identity Graph
Mission Context
Decision Renderer
Attack Simulation
Immediate Actions
Timeline

Conclusion:

The Analyst Workspace already represents the primary user experience for Version 1.

Identity Decision Workspace should evolve from this implementation.

No replacement required.

Security Knowledge Graph

Status:

✅ Existing

Current capability:

Identity

↓

Accounts

↓

Groups

↓

Roles

↓

Memberships

↓

Role Assignments

Conclusion:

The graph already contains the relationships required to support Version 1.

The remaining work focuses on presentation rather than collection.

Synchronization

Status:

✅ Complete

Current live synchronization includes:

Identities
Accounts
Groups
Memberships
Roles
Role Assignments

Conclusion:

Synchronization is sufficiently mature for Version 1.

Future effort should prioritize intelligence rather than additional providers.

Authorization

Status:

✅ Complete

Current capability:

Groups
Roles
Assignment Types
Directory Scope
Application Scope
Canonical Relationships

Conclusion:

Authorization context already exists.

The analyst experience should expose it more effectively.

Current Gaps

The existing platform answers:

"What exists?"

Version 1 must answer:

"Why does it matter?"

Current opportunities:

Richer authorization summaries
Explainable exposure
Better recommendation context
Improved analyst workflow
Decision-focused presentation
Investigation narrative
Sprint Implementation Strategy

This sprint will extend, not replace.

The following components will be reviewed before modification:

IdentityGraphService
IdentityIntelligenceService
AnalystWorkspace
IdentityGraphPanel
MissionContextPanel
ImmediateActionsPanel
RecentActivityPanel

Only capabilities that improve analyst understanding will be added.

Version 1 User Journey

Identity Decision Workspace should guide an analyst through one investigation.

Identity

↓

Authentication

↓

Authorization

↓

Exposure

↓

Recommendations

↓

Decision

↓

Report

Every screen should reinforce this flow.

Success Criteria

Sprint 11.1 is complete when:

Identity information is immediately understandable.
Authorization is explained rather than listed.
Exposure is explainable.
Recommendations are actionable.
The investigation naturally progresses toward a decision.
No existing architectural components are unnecessarily replaced.
Lessons Learned

This discovery produced an important realization.

The Identity Decision Workspace already exists in the repository.

The remaining work is not construction.

It is refinement.

USOP has entered the Decision Intelligence phase of development.

Future sprints should prioritize enriching analyst understanding over introducing additional infrastructure.

Engineering Impact

This discovery reinforces an important engineering principle.

Inspect. Discover. Understand. Extend.

Version 1 will be built primarily by extending mature architecture rather than replacing it.

That approach reduces technical debt, improves maintainability, and allows every sprint to focus on customer value instead of rebuilding existing capabilities.
