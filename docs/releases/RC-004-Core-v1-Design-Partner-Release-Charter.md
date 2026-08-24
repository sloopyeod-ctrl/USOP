# RC-004 Core v1.0 Design Partner Release Charter

## Mission

RC-004 exists to transform the proven USOP Core capability into a frozen, reproducible, supportable Design Partner release.

RC-004 must prove that a Design Partner can securely deploy USOP Core, connect the supported Microsoft Entra environment, understand what matters, complete the documented investigation and decision workflow, and operate the platform without undocumented developer assistance.

RC-004 is a release-readiness milestone, not a feature-expansion milestone.

## Product Outcome

The release must allow a security engineer to move through the permanent Core workflow:

Connect -> Orient -> Investigate -> Decide -> Learn -> Operate

The product must help the analyst answer:

1. What matters right now?
2. Why does it matter?
3. What should I do next?

The release succeeds when this workflow reduces investigation effort and improves decision confidence without creating additional operational burden.

## Frozen Starting Baseline

- Runtime version: 0.14.0
- Architecture: Engine First
- RC-003 closeout commit: 2c7c8cc
- RC-003 tag: rc-003-platform-administration-complete
- Backend regression baseline: 870 passed
- Working tree at RC-004 start: clean

RC-003 Platform Administration is treated as a proven foundation.

RC-004 must not reopen RC-003 architecture unless release validation identifies a concrete defect, security issue, data-integrity issue, or supported-workflow failure.

## Core Investigation Experience

RC-004 validates the following operational path as one product experience:

Microsoft Entra connection
-> synchronization and reconciliation
-> operational priority
-> Executive Dashboard orientation
-> investigation selection
-> Mission Brief
-> Decision Intelligence
-> supporting Operational Context
-> Organizational Experience
-> Organizational Decision
-> persisted organizational knowledge
-> governed reassessment or new material-change detection
-> Operational Pulse
-> return to normal security work

Individual components are not sufficient.

The complete supported workflow must function coherently against the frozen release artifact.

## Analyst Promise

Every RC-004 decision must be evaluated against the USOP product test:

- Does this reduce investigation time?
- Does this reduce manual correlation?
- Does this improve decision quality?
- Does this reduce repetitive administrative work?
- Does this increase actionable outcomes?
- Would a security engineer genuinely benefit from this during normal work?

A change that does not materially support the Core release workflow should be deferred.

## RC-004.0 - Frozen Release Contract

Objective:

Define exactly what the Design Partner artifact supports.

RC-004.0 must freeze and validate:

- supported Microsoft Entra connector behavior
- minimum required Microsoft Graph permissions
- supported Platform User authentication model
- supported secret-provider modes
- supported host operating system
- supported Docker version or version range
- supported Docker Compose version or version range
- inbound ports
- required outbound destinations
- DNS requirements
- TLS and ingress assumptions
- persistent storage boundaries
- database persistence expectations
- supported deployment topology
- credential reload or restart behavior
- application health and readiness expectations

No customer-facing release claim may remain based on development assumptions.

## RC-004.1 - Core Workflow End-to-End Validation

Objective:

Prove the permanent USOP investigation model against representative synchronized data.

RC-004.1 must validate:

- supported Microsoft Entra synchronization
- relationship and authorization reconciliation
- material authorization-change behavior
- operational priority generation
- Executive Dashboard orientation
- Mission Brief
- Decision Intelligence
- supporting identity, relationship, authorization, timeline, and exposure context
- Organizational Experience
- Organizational Decision recording
- persistence of organizational knowledge
- governed review scheduling where supported
- immediate new decision opportunity for new material authorization changes
- Operational Pulse

A prior decision, exception, review schedule, eligible assignment, temporary assignment, or PIM state must not silently suppress a new material security change.

## RC-004.2 - Deployment and Operational Validation

Objective:

Replace deployment assumptions with measured support boundaries.

RC-004.2 must validate and document:

- installation prerequisites
- CPU requirements
- memory requirements
- storage requirements
- container resource behavior
- dashboard responsiveness
- investigation load time
- graph responsiveness
- synchronization performance
- database behavior
- supported scale boundaries
- backup procedure
- restore procedure
- upgrade behavior
- rollback behavior
- credential rotation behavior
- customer-facing failure states
- logging destinations
- secret-redaction expectations
- monitoring and health behavior

Performance and scale statements must be based on measured validation rather than intuition.

## RC-004.3 - Clean-Room Installation

Objective:

Prove that a customer can deploy the release using only the frozen package and customer-facing documentation.

The clean-room environment must not depend on:

- developer workstation state
- development database contents
- source-tree secrets
- undocumented environment variables
- previously created containers
- undocumented Docker state
- VS Code
- developer-only scripts not included in the release
- verbal developer coaching

The clean-room validation must prove:

- package acquisition
- configuration
- secret configuration
- container startup
- migration
- health validation
- Microsoft Entra configuration
- first authentication
- first supported synchronization
- opening the product
- completing a representative investigation

Any undocumented dependency discovered during clean-room validation is an RC readiness issue.

## RC-004.4 - Artifact Freeze and Design Partner Package

Objective:

Create the exact reproducible artifact that will be delivered for Design Partner evaluation.

The frozen package must define or include:

- release identifier
- build identifier
- release date
- pinned application images
- container image identifiers or digests
- checksums where appropriate
- Docker Compose configuration
- environment template
- supported configuration contract
- database migration state
- customer documentation
- final Release Notes
- final Known Limitations
- final Graph permission matrix
- final network requirements
- final host/runtime requirements
- backup and restore guidance
- upgrade guidance
- rollback guidance
- supported authentication model

The artifact delivered to a Design Partner must be the exact artifact that passed final validation.

## Customer Documentation Gate

The Design Partner package must reconcile the frozen artifact against:

- 01-Installation-Guide.md
- 02-Secrets-Configuration-Guide.md
- 03-Security-Deployment-Guide.md
- 04-User-Guide.md
- 05-Design-Partner-Guide.md
- 06-Feedback-Questionnaire.md
- 07-Release-Notes.md
- 08-Known-Limitations.md

Customers should encounter documented boundaries, not surprises.

## Rapid Situational Awareness Gate

The primary analyst surfaces must support the 10-20 Second Rule.

Within approximately 10-20 seconds, the analyst should be able to determine:

- what matters
- why it matters
- what to do next

If the analyst must first learn the interface before understanding the security problem, the workflow requires review.

## Design Partner Operational Gate

The frozen release should support the intended evaluation rhythm:

Day 1 - Deploy
Day 2 - Orient
Day 3 - Decide
Day 4 - Learn
Day 5 - Operate

The strongest Design Partner success question is:

Would the team want to keep using USOP after the evaluation period ends?

## Security Gates

RC-004 must preserve:

- customer-owned credential handling
- no embedded production secrets
- least-privilege Microsoft Graph access
- provider-neutral secret architecture
- Microsoft Entra inbound authentication
- delegated API scope enforcement
- runtime Platform RBAC
- Organization boundaries
- trusted actor attribution
- non-enumerating authorization failures
- persistent audit evidence
- separation of authentication, authorization, licensing, and Seat allocation

A release-readiness change must not weaken the security contracts proven during RC-003.

## Explicit Non-Goals

Unless required to repair a supported Core workflow defect, RC-004 will not add:

- AWS support
- Google Cloud support
- Okta support
- SecureW2 support
- GitHub support
- NetBox support
- Zabbix support
- Kubernetes deployment
- arbitrary container-runtime support
- autonomous AI analyst behavior
- CISA KEV operational ingestion
- DISA advisory operational ingestion
- NVD operational ingestion
- new threat-intelligence modules
- broad vulnerability-intelligence expansion
- broad asset-intelligence expansion
- CIAM expansion
- SaaS-governance expansion
- unrelated UI redesign

These remain future roadmap capabilities unless separately brought into a validated release.

## Change-Control Rule

No new feature enters RC-004 merely because it would be useful.

A code change during RC-004 must satisfy at least one of these conditions:

1. It fixes behavior that contradicts the documented Core release.
2. It repairs a supported workflow.
3. It removes a security or data-integrity risk.
4. It removes undocumented deployment dependence.
5. It materially reduces friction in the permanent Core investigation workflow.
6. It is required to create or validate the frozen release artifact.

Everything else should be recorded for future roadmap consideration.

## Freeze Reopen Rule

After the Design Partner artifact is frozen, changes to deployment-critical or application behavior reopen validation.

Examples include:

- application code
- dependencies
- container images
- deployment configuration
- environment contract
- secret-provider support
- Graph permissions
- network requirements
- persistence behavior
- database migrations
- deployment-critical customer documentation

## RC-004 Completion Criteria

RC-004 is complete only when:

- the supported release contract is explicit
- the complete Core investigation workflow passes end-to-end validation
- material authorization changes create appropriate analyst work
- organizational decisions persist correctly
- Operational Pulse reflects supported operational truth
- deployment requirements are measured and documented
- backup and restore are validated
- upgrade and rollback boundaries are documented
- clean-room installation succeeds using customer documentation only
- the frozen release artifact passes backend regression
- the frontend builds successfully
- frontend lint passes
- release containers build and start successfully
- health validation passes
- real Microsoft Entra authentication passes
- supported synchronization passes
- secret-redaction review passes
- customer documentation matches the frozen artifact
- Release Notes contain no unsupported capability claims
- Known Limitations contain no material undocumented boundaries
- the Design Partner package is reproducible

## Release Success Criterion

USOP Core v1.0 is ready for Design Partner delivery only when the exact frozen artifact can be securely installed, validated, understood, and used through the documented investigation workflow without undocumented developer assistance.

RC-004 therefore answers one question:

Is USOP Core ready to leave the developer workstation and prove its value in someone else's security environment?
