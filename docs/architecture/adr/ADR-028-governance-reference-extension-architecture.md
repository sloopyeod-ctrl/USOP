# ADR-028: Governance Reference Extension Architecture

## Status

Accepted

## Context

USOP Core owns operational security workflows such as authorization events,
materiality classification, pending analyst work, human decision recording,
organizational memory, operational attention, evidence preservation, and audit
history.

Customers may follow one or more external governance, regulatory, assurance,
or certification frameworks. Examples include NIST SP 800-53, ISO/IEC 27001,
GDPR, CMMC, PCI DSS, CIS Controls, DISA STIGs, and future standards not yet
known to USOP.

Framework-specific capabilities are commercially distinct extensions. A
customer administrator must be able to license and enable only the extensions
required by each Organization.

USOP Core must not hardcode framework names, control identifiers, framework
logic, or unlicensed framework content. Core must also avoid redesign when new
framework extensions are introduced.

## Decision

USOP Core will understand a generic Governance Reference contract and will
never depend on a framework-specific domain model.

Framework extensions own framework-specific knowledge and expose governance
references through a stable provider contract.

> Core owns workflows. Extensions own framework-specific knowledge.

### Core responsibilities

USOP Core may:

- create and manage governed analyst work;
- record human decisions and justifications;
- link decisions to generic Governance References;
- preserve organization-authored policies, SOPs, exceptions, tickets, and
  internal Knowledge Assets;
- retain immutable evidence showing which references supported a decision;
- enforce Tenant and Organization boundaries;
- verify that an extension is licensed and enabled before accepting or using
  references supplied by that extension;
- expose generic query and relationship capabilities independent of framework.

USOP Core must not:

- contain branches such as `if framework == "NIST"`;
- ship hidden framework catalogs as Core data;
- ingest, analyze, map, recommend from, or operationalize framework content
  without the corresponding licensed extension;
- assume generic external guidance overrides customer policy;
- automatically convert pending work into a human DecisionRecord.

### Extension responsibilities

Each framework extension owns:

- framework identity and version;
- control, article, requirement, benchmark, or safeguard catalogs;
- framework-specific descriptions and metadata;
- mappings and relationships;
- applicability logic;
- assessment or evidence expectations;
- framework-specific recommendations;
- content lifecycle and updates;
- licensing and entitlement checks;
- paid framework-specific intelligence.

### Governance Reference contract

Core treats every external or internal supporting reference through a generic
shape such as:

```text
reference_id
organization_id
provider_key
reference_type
external_identifier
title
summary
version
source_uri
status
effective_at
retired_at
metadata
```

The exact persistence model may evolve, but the semantic contract is stable.

`provider_key` identifies the registered provider or extension without causing
Core to understand its framework semantics.

`reference_type` is generic and extensible. Example values may include:

- Policy
- SOP
- StandardControl
- RegulationArticle
- CertificationRequirement
- Exception
- RiskAcceptance
- ChangeTicket
- KnowledgeAsset
- ExternalGuidance

Core stores extensible values as strings governed by shared application
vocabulary so new providers do not require PostgreSQL enum migrations.

### Decision relationships

A pending decision work item may suggest candidate Governance References, but
only the human decision confirms which references supported the final judgment.

```text
AuthorizationEvent
    -> PendingDecisionWorkItem
    -> Human Review
    -> DecisionRecord
    -> GovernanceReference relationships
    -> Organizational Memory
```

The DecisionRecord remains the authoritative state of the human decision.

### Historical integrity

USOP must preserve decision-time reference context.

A future extension update must not silently rewrite evidence used by an older
decision. Historical relationships retain the version or snapshot identifier
used at decision time.

Corrections are append-only or superseding operations. Historical evidence is
never silently overwritten.

### Licensing boundary

Framework extensions are commercially optional.

Core may preserve a customer-supplied opaque link to an unlicensed external
publication, but Core must not ingest, read, analyze, map, recommend from, or
operationalize that publication without the corresponding licensed extension.

When an extension license is disabled or expires:

- historical decision evidence remains readable according to contract and
  retention policy;
- new framework-specific ingestion, analysis, recommendations, mappings, and
  updates stop;
- Core workflows continue operating;
- no Core redesign is required.

### Tenant and Organization isolation

Extension registration may occur at the Tenant level, but enablement,
configuration, references, assessments, and resulting evidence are scoped to
an Organization unless explicitly inherited through authorized configuration.

An MSP or MSSP Tenant may license many Organization entitlements. A child
Organization can access only its own enabled references, decisions, evidence,
and extension results.

### Provider architecture

Framework extensions register using the same provider principles as other USOP
capabilities:

- stable provider key;
- declared capabilities;
- health and version metadata;
- explicit activation;
- Organization-owned configuration;
- entitlement verification;
- deterministic outputs;
- no hidden side effects.

Core consumes the provider contract, not framework-specific implementations.

### Future recommendation and AI capabilities

Future licensed recommendation or local AI extensions may use governed
organizational knowledge, approved policies and SOPs, historical DecisionRecords,
linked Governance References, prior outcomes, and current security evidence.

They must not treat unsupported model knowledge or assumptions as organizational
truth.

Every recommendation must remain explainable through evidence, references,
historical decisions, confidence, and provider provenance.

The AI remains advisory. Humans retain accountability for final decisions.

## Consequences

### Positive

- New frameworks can be added without redesigning Core.
- Framework products can be licensed independently.
- Customers select only the extensions they need.
- Core remains small, stable, and framework-neutral.
- Human decisions remain explainable and auditable.
- Historical evidence survives framework updates.
- MSP and MSSP deployments can enable different frameworks by Organization.
- Future AI recommendations can be grounded in governed organizational facts.

### Negative

- A generic provider and relationship contract must be maintained carefully.
- Framework extensions must map native structures into the common contract.
- Historical snapshots or version references increase lifecycle responsibility.
- Cross-framework mappings may require separately licensed capabilities.

## Implementation guidance

This ADR does not require Core to build framework catalogs now.

Current Core work should:

1. build a generic pending decision work-item domain;
2. preserve the triggering AuthorizationEvent;
3. keep DecisionRecord human-driven;
4. avoid framework-specific fields;
5. leave a stable future relationship boundary for Governance References;
6. continue using Organization-scoped, caller-owned transactions;
7. preserve append-only evidence and audit history.

A later Core sprint may introduce generic Governance Reference and
Decision-to-Governance-Reference relationship models. Framework content and
framework-specific logic remain extension work.

## Governing principles

- Core owns workflows. Extensions own knowledge.
- Core understands Governance References, not framework names.
- Human decisions remain human-driven.
- Historical evidence is preserved at decision time.
- Unlicensed external content is never operationalized.
- Recommendations must be explainable and Organization-specific.
- Evolution Before Replacement.
