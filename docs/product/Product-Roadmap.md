USOP Product Roadmap
Purpose

This roadmap describes the long-term direction of USOP.

Unlike the Version 1 Definition, this document is intentionally expected to evolve over time as the product matures.

The roadmap focuses on customer outcomes rather than implementation details.

Technologies, providers, and integrations may change.

The mission of USOP does not.

Product Vision

USOP will evolve into a modular Security Decision Intelligence Platform.

The platform will help organizations answer a single question:

What matters right now, and what should we do next?

Everything in the roadmap supports that objective.

Version 1
Identity Decision Intelligence

Objective

Demonstrate that security engineers can investigate identity and authorization risk significantly faster than traditional workflows.

Primary capabilities include:

Microsoft Entra integration
Identity synchronization
Authorization synchronization
Canonical Security Knowledge Graph
Identity 360
Authorization context
Exposure analysis
Attack-path foundation
Analyst Workspace
Findings
Recommendations
Decision tracking
Reporting

Version 1 intentionally focuses on demonstrating value rather than breadth.

Version 1.5
Operational Decision Intelligence

After Version 1 is stable, USOP expands operational awareness.

Potential capabilities:

Asset awareness
Asset ownership
Historical analyst decisions
Vulnerability correlation
Expanded reporting
Additional identity providers
Cloud authorization providers
Expanded graph analytics

Primary objective:

Allow analysts to understand how identities, assets, and vulnerabilities intersect.

Version 2
Threat Decision Intelligence

Version 2 introduces modular threat intelligence.

Potential modules include:

CISA Known Exploited Vulnerabilities (KEV)
National Vulnerability Database (NVD)
Microsoft Security Advisories
Ubuntu Security Notices
Cisco Security Advisories
Juniper Security Advisories
DISA Advisories
Threat prioritization
Exposure correlation
Recommended SIEM detections

The objective is not to display every vulnerability.

The objective is to answer:

Which threats actually matter to my environment today?

Version 3
Automated Security Decision Intelligence

Once the platform has sufficient context and historical analyst knowledge, USOP begins assisting with higher-level decision support.

Potential capabilities include:

Decision recommendations
Automated evidence collection
Suggested hardening actions
Suggested detections
Historical decision reuse
Risk forecasting
Executive reporting
Compliance evidence generation

Security engineers remain responsible for security decisions.

USOP provides evidence, context, and recommendations.

Modular SaaS Strategy

USOP is designed as a modular platform.

Organizations should only purchase the capabilities they need.

Potential modules include:

Core Platform
Identity Decision Intelligence
Threat Intelligence
Threat prioritization
Advisory correlation
Compliance
Control mapping
Evidence generation
Detection Engineering
Detection recommendations
SIEM correlation
Executive Reporting
Risk summaries
Operational metrics
Engineering time saved

This architecture allows organizations of different sizes and maturity levels to adopt USOP incrementally.

Long-Term Architectural Direction

Every future capability should build upon the existing architecture.

Future providers should extend—not replace—the platform.

Examples include:

Identity Providers

Microsoft Entra
Okta
Active Directory

Cloud Providers

AWS IAM
Azure RBAC
Google Cloud IAM

Infrastructure

Linux
Kubernetes
VMware

Networking

Cisco
Juniper
Palo Alto

Security

Vulnerability Management
Threat Intelligence
Detection Engineering

Every provider contributes to one canonical Security Knowledge Graph.

What Will Not Change

Regardless of future features, USOP will continue following the Product Constitution.

Future development should always prioritize:

Returning engineering time
Improving security decisions
Reducing manual investigation
Reducing repetitive administrative work
Increasing actionable outcomes

Those principles are more important than any individual feature.

The Future of USOP

USOP is not intended to become another collection of disconnected security tools.

Its long-term purpose is to become the platform that connects identities, assets, authorization, exposure, threats, analyst knowledge, and organizational context into a single decision-making system.

Every new capability should strengthen that system.

Success

The long-term success of USOP will not be measured by the number of integrations or features it supports.

Success will be measured by a single outcome:

Security engineers spend more time reducing risk and less time gathering information.
