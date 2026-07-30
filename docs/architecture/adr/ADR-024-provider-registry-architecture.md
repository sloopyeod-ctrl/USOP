# ADR-024: Provider Registry Architecture

- **Status:** Accepted
- **Date:** 2026-07-30
- **Decision Makers:** USOP Architecture
- **Supersedes:** None
- **Superseded By:** None

---

# Context

USOP consumes information from authoritative external systems and transforms
that information into normalized relationships, evidence, operational context,
and explainable security decisions.

Microsoft Entra ID is the first implemented connector provider, but the platform
is expected to support many future authoritative systems, including:

- Amazon Web Services
- Microsoft Azure
- Google Cloud Platform
- Okta
- SecureW2
- NetBox
- Zabbix
- Tenable
- Microsoft Defender
- Microsoft Sentinel
- ServiceNow
- Other identity, cloud, infrastructure, monitoring, vulnerability, and
  governance platforms

These systems remain authoritative for the information they own.

USOP does not attempt to replace them.

USOP exists to understand their information, relationships, changes, and
combined operational meaning.

As connector support expands, the platform requires a consistent method for
describing, discovering, constructing, and activating connector providers
without embedding vendor-specific knowledge throughout the application.

---

# Problem

The original connector architecture registered Microsoft Entra directly inside
the application service.

This approach was sufficient while only one connector existed, but it created
several future risks.

Without a provider registry:

- Application services must know every concrete provider class.
- Every new provider requires additional service-level registration logic.
- Provider metadata becomes scattered across provider implementations.
- Provider discovery and provider runtime lifecycle become coupled.
- Frontend and API capabilities may become vendor-specific.
- New integrations may invent inconsistent metadata conventions.
- Licensing, configuration, health, and runtime concerns may become
  incorrectly combined.
- The platform may accumulate parallel connector architectures as it grows.

USOP requires one canonical architectural doorway through which connector
providers enter the platform.

---

# Decision

USOP adopts a Provider Registry architecture.

The Provider Registry is the canonical catalog of available connector provider
types.

It owns:

- Provider descriptors
- Provider names
- Provider discovery metadata
- Provider construction factories
- Deterministic provider enumeration

It does not own:

- Runtime provider lifecycle
- Authentication
- Health evaluation
- Synchronization
- Customer configuration
- Secrets
- Deployment enablement
- Licensing
- Persistence
- Decision intelligence

These concerns remain separate.

The resulting architecture is:

```text
ProviderDescriptor
        ↓
ProviderRegistry
        ↓
ConnectorService
        ↓
ConnectorManager
        ↓
Connector Provider
        ↓
Synchronization
        ↓
Canonical Platform Data
        ↓
Decision Intelligence

Architectural Responsibilities
ProviderDescriptor

ProviderDescriptor defines what a provider is and what it is capable of
supplying.

The descriptor contains immutable provider metadata, including:

Canonical provider identifier
Display name
Vendor
Component version
Intelligence domains
Capabilities
Supported operating modes

The descriptor intentionally excludes runtime and customer-specific state.

A descriptor answers:

What is this provider, and what can it supply?

It does not answer:

Is this provider healthy, configured, licensed, or enabled for this customer?

ProviderRegistry

ProviderRegistry catalogs provider descriptors and provider factories.

The registry:

Registers provider descriptors
Registers provider construction factories
Rejects duplicate provider registrations
Returns descriptors deterministically
Creates provider instances by canonical provider name
Verifies that constructed providers match their registered descriptor
Returns None for unknown provider names

The registry does not execute provider operations.

A registry answers:

Which provider types are available?

ConnectorManager

ConnectorManager remains responsible for active provider instances and their
runtime lifecycle.

The manager:

Holds active provider instances
Initializes providers
Evaluates provider health
Executes provider synchronization
Coordinates provider lifecycle operations

A manager answers:

Which provider instances are currently active, and how are they operating?

ConnectorService

ConnectorService remains the application-facing facade for connector
operations.

The service:

Registers built-in provider descriptors and factories
Activates registered providers through the registry
Preserves injected manager providers
Exposes active provider names
Exposes provider descriptor metadata
Adapts health and synchronization results into application-facing structures
Preserves temporary provider aliases where compatibility requires them

The service does not own provider-specific implementation logic.

Separation of Concerns

Provider identity, deployment configuration, operational state, and commercial
entitlement are separate concepts.

ProviderDescriptor
    What the provider is and what it supports

ProviderConfiguration
    How a deployment connects to and uses the provider

ProviderState
    How the provider is operating right now

ProviderLicense
    Whether the organization is commercially entitled to use it

Only ProviderDescriptor and ProviderRegistry are implemented by this
decision.

The other boundaries are documented so future implementations extend the
architecture without overloading the descriptor or registry.

USOP will not create speculative implementations for configuration, runtime
state, or licensing until a concrete platform capability requires them.

Canonical Provider Identifiers

Every provider must use a canonical lowercase identifier.

Canonical identifiers may contain:

Lowercase letters
Numbers
Hyphens

Canonical identifiers must not:

Begin with a hyphen
End with a hyphen
Contain consecutive hyphens
Contain uppercase letters
Contain spaces
Contain unsupported punctuation

Example:

microsoft-entra

Temporary compatibility aliases may exist at the service boundary.

Aliases do not become registry identities.

For example:

entra
    ↓
microsoft-entra

The registry contains only the canonical identifier.

Intelligence Domains

Providers describe the intelligence domains to which they contribute.

Examples include:

Identity
Authentication
Authorization
Cloud
Infrastructure
Networking
Monitoring
Vulnerability
Endpoint
Compliance
Governance

Intelligence domains describe broad areas of platform understanding.

They are not vendor names and are not licensing decisions.

A single provider may contribute to multiple domains.

For example, Microsoft Entra contributes to:

Identity
Authentication
Authorization
Provider Capabilities

Providers declare specific capabilities representing the information they can
supply.

Microsoft Entra currently declares:

identities
accounts
groups
memberships
roles
role_assignments

Future providers may declare capabilities such as:

AWS
organizations
cloud_accounts
iam_users
iam_roles
iam_policies
resources
security_findings
NetBox
devices
interfaces
sites
networks
vlans
virtual_machines
SecureW2
certificates
radius_clients
enrollments
devices
users
Zabbix
hosts
services
alerts
availability
metrics

Capabilities describe provider knowledge.

They do not imply that every declared capability is enabled, licensed, or
successfully collected in every deployment.

Supported Modes

Providers may declare supported operating modes.

Examples include:

demo
test
live

Supported modes describe implementation capability.

They do not represent current runtime state.

For example, a provider may support both demo and live while a specific
deployment is currently configured only for demo.

Factory Validation

Provider factories must construct a provider whose canonical provider name
matches the registered descriptor.

The registry rejects a factory result when:

descriptor.provider_name != provider.provider_name

This protects the platform from metadata and runtime identity drift.

Deterministic Enumeration

Provider names and descriptors must be returned in deterministic canonical
order.

Deterministic enumeration supports:

Stable tests
Predictable APIs
Reproducible diagnostics
Consistent frontend rendering
Reliable operational comparisons

Registration order must not determine API output order.

Relationship to the Future Intelligence Registry

The Provider Registry is intentionally limited to connector providers.

USOP may eventually require broader registries for:

Analytics builders
Knowledge packs
Detection packs
Threat intelligence extensions
Visualization modules
Licensed intelligence capabilities

USOP will not create a speculative universal Intelligence Registry before those
concrete component types exist.

Instead, the Provider Registry is designed so it can later be composed into a
broader architecture.

Future Intelligence Registry
    ├── Provider Registry
    ├── Analytics Registry
    ├── Knowledge Registry
    └── Extension Registry

The Provider Registry will evolve through composition rather than replacement.

This follows ADR-017, Evolution Before Replacement.

Relationship to Pipeline-Based Intelligence

ADR-021 establishes that USOP intelligence should scale through independent,
composable capabilities rather than increasingly large engines.

The Provider Registry supports that decision by standardizing how authoritative
external information enters the platform.

Providers supply facts.

Normalization translates provider-specific facts.

Relationships connect those facts.

Independent intelligence builders interpret those relationships.

Decision intelligence prepares explainable operational meaning.

Authoritative System
        ↓
Provider
        ↓
Normalization
        ↓
Canonical Relationships
        ↓
Independent Intelligence Capabilities
        ↓
Explainable Decisions

The registry does not perform normalization or intelligence analysis.

Relationship to Commercial Licensing

The Provider Registry does not make licensing decisions.

Commercial licensing may later determine whether a registered provider or
capability is available to an organization.

This distinction is intentional.

A provider may be:

Known to the platform
Registered in the provider catalog
Unlicensed for a particular organization
Disabled in a particular deployment
Unconfigured
Temporarily unhealthy

These states must not be collapsed into one field or one registry decision.

The registry answers whether the provider type exists.

Licensing answers whether the organization may use it.

Configuration answers how it connects.

Runtime state answers how it is operating.

Relationship to Authoritative Systems

Provider registration does not transfer authority to USOP.

External systems remain authoritative for their source data.

Examples:

Microsoft Entra remains authoritative for Entra identities and assignments.
AWS remains authoritative for AWS accounts, resources, policies, and
findings.
NetBox remains authoritative for network inventory when designated by the
organization.
Zabbix remains authoritative for its monitoring observations.
Tenable remains authoritative for its vulnerability findings.

USOP normalizes, correlates, evaluates, and preserves organizational
understanding of that information.

USOP does not become the system of record merely because a provider is
registered.

Initial Implementation

The initial implementation introduces:

backend/app/connectors/provider/
    ProviderDescriptor.py
    ProviderRegistry.py
    __init__.py

Microsoft Entra declares a provider descriptor containing:

Provider Name:
microsoft-entra

Display Name:
Microsoft Entra ID

Vendor:
Microsoft

Intelligence Domains:
- Identity
- Authentication
- Authorization

Capabilities:
- identities
- accounts
- groups
- memberships
- roles
- role_assignments

Supported Modes:
- demo
- live

ConnectorService now registers Microsoft Entra through ProviderRegistry
rather than constructing it directly as an active provider.

The registry constructs the provider.

ConnectorManager owns the resulting active instance.

Compatibility

The temporary legacy alias:

entra

continues resolving to:

microsoft-entra

This compatibility behavior remains at the service boundary.

The alias is not registered as a separate provider and does not appear in
canonical provider listings.

Unknown provider collection and synchronization requests continue returning
None to preserve the existing application contract.

# Testing Requirements

Provider registry regression coverage must verify:

Deterministic descriptor collection ordering
Capability queries
Intelligence domain queries
Supported mode queries
Canonical provider-name validation
Descriptor registration
Provider construction
Duplicate registration rejection
Factory identity mismatch rejection
Unknown provider behavior
Registry-driven ConnectorService activation
Descriptor serialization through ConnectorService
Preservation of canonical provider names
Preservation of temporary aliases
Preservation of health behavior
Preservation of synchronization behavior

The full backend regression suite must remain green.

# Consequences
Positive Consequences
New providers enter the platform through one architectural doorway.
ConnectorService no longer owns direct provider construction.
Provider discovery is separated from runtime lifecycle.
Provider metadata becomes standardized.
Provider enumeration becomes deterministic.
Future APIs can expose provider capabilities without vendor-specific logic.
Future frontend experiences can render provider metadata generically.
Future licensing can evaluate providers and capabilities without changing
provider construction.
Future AWS, GCP, Okta, SecureW2, NetBox, Zabbix, Tenable, and other providers
can follow the same conventions.
Provider factories are protected against canonical-name drift.
The architecture can evolve into a broader intelligence registry through
composition.
Negative Consequences
The connector architecture gains another abstraction.
Provider implementations must maintain descriptor metadata.
Some provider capability metadata may temporarily duplicate existing runtime
health details.
Provider registration remains explicit until module discovery is justified.
Descriptor versioning requires future governance as provider implementations
mature.

These costs are accepted because the registry removes larger long-term coupling
and inconsistency risks.

Rejected Alternatives
Register Providers Directly in ConnectorService

Rejected because application services would need knowledge of every concrete
provider and would continue growing vendor-specific registration logic.

Place Descriptors Inside ConnectorManager

Rejected because discovery metadata and runtime lifecycle are separate
responsibilities.

ConnectorManager manages active instances.

ProviderRegistry catalogs available provider types.

Create a Universal Intelligence Registry Immediately

Rejected because analytics packs, knowledge packs, detection packs, and other
future component types do not yet have proven runtime contracts.

Creating one universal registry now would introduce speculative abstraction.

The current provider registry is designed for future composition instead.

Combine Descriptor, Configuration, Health, and Licensing

Rejected because these values have different ownership and lifecycles.

Descriptor data is static provider identity.
Configuration is deployment-specific.
Health is runtime-specific.
Licensing is organization-specific and commercial.

Combining them would create an overloaded and unstable provider model.

Automatically Discover All Python Provider Modules

Rejected for the initial implementation because explicit registration is easier
to test, reason about, secure, and govern.

Automatic plugin discovery may be considered later when the provider ecosystem
requires it.

# Future Evolution

Potential future increments include:

Generic provider descriptor API endpoints
Provider configuration schemas
Organization-specific provider enablement
Provider operational state
Provider synchronization history
Capability-level licensing
Provider dependency declarations
Provider compatibility validation
Provider package signing
External provider plugin loading
Broader Intelligence Registry composition

Each increment must be driven by a concrete platform requirement.

The Provider Registry must not become responsible for runtime, commercial, or
customer-specific concerns merely for convenience.

Final Architectural Principle

Authoritative systems provide facts.

Connector providers retrieve those facts.

The Provider Registry describes and constructs providers.

ConnectorManager operates active provider instances.

Normalization creates canonical meaning.

Relationships create context.

Intelligence capabilities explain why the information matters.

Human analysts remain accountable for material security decisions.

USOP scales by adding providers and intelligence capabilities through stable
architectural boundaries rather than enlarging vendor-specific application
logic.