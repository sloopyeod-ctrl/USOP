USOP Version 1 Definition
Purpose

Version 1 of USOP is not intended to be a complete security platform.

It is intended to be a polished, production-quality proof of concept that clearly demonstrates the value of Security Decision Intelligence.

Version 1 should prove that USOP helps security engineers investigate identity and authorization risk faster, make better decisions, and spend less time manually collecting information.

Every capability included in Version 1 should directly support that objective.

Capabilities that do not materially strengthen the demonstration of that objective should be postponed until a later release.

Version 1 Success Criteria

Version 1 is complete when a security engineer can:

Understand an identity in less than 30 seconds.
Understand why an identity has access.
Understand why an identity is considered risky.
Receive actionable recommendations.
Record a security decision.
Produce evidence supporting that decision.

If those outcomes are not possible, Version 1 is not complete regardless of how many supporting features have been implemented.

Core Demonstration

The primary Version 1 demonstration is:

Microsoft Entra

↓

Synchronization

↓

Canonical Security Graph

↓

Identity 360

↓

Authorization Context

↓

Exposure Analysis

↓

Recommendations

↓

Analyst Decision

↓

Report

Everything included in Version 1 should strengthen this workflow.

Version 1 Capability Checklist
Foundation

These capabilities establish the platform.

 Connector Framework
 Secret Provider Framework
 Provider-neutral domain model
 Canonical normalization
 Canonical reconciliation
 Identity synchronization
 Account synchronization
 Group synchronization
 Membership synchronization
 Role synchronization
 Role assignment synchronization
 Identity Graph
 Authorization Graph
 Shared relationship resolution
Identity Decision Intelligence

These capabilities allow an analyst to understand an identity.

 Identity 360
 Authorization summary
 Authentication summary
 Privilege summary
 Exposure summary
Security Intelligence

These capabilities explain why something matters.

 Exposure scoring
 Attack-path analysis
 Findings framework
 Recommendations
 Evidence collection
Analyst Workflow

These capabilities support operational security work.

 Decision tracking
 Analyst Workspace
 Reporting
 Investigation workflow
Platform Quality

Version 1 should also demonstrate engineering quality.

 Stable architecture
 Clean regression testing
 Provider-neutral design
 Documentation
 Product Constitution
 Development Workflow
 Demonstration Scenario
Version 1 Non-Goals

The following capabilities are intentionally outside the scope of Version 1.

AWS IAM
Azure RBAC
Linux authorization
Kubernetes authorization
Threat Intelligence
Vulnerability correlation
Asset inventory
Compliance automation
Executive dashboards
PIM intelligence
Automated decision making

These capabilities remain important but should not delay completion of Version 1.

Version 1 Quality Standards

Version 1 should demonstrate:

Clean architecture.
Provider-neutral design.
Stable synchronization.
Reliable regression testing.
Clear analyst workflow.
Professional user experience.
Demonstrable engineering value.
Definition of Done

Version 1 is complete when:

Every Version 1 capability has been implemented.
All regression tests pass.
The demonstration scenario can be completed from beginning to end without manual intervention.
The platform clearly demonstrates reduced investigation effort.
The Product Constitution remains fully supported.
Guiding Question

Before beginning any new sprint, ask:

Does this move Version 1 closer to demonstrating Security Decision Intelligence?

If the answer is No, reconsider whether the capability belongs in Version 1.
