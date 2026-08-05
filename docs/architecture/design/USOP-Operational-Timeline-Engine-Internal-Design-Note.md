# USOP Operational Timeline Engine — Internal Design Note

**Document type:** Internal architecture design note  
**Status:** Proposed for Sprint 28.3.3.1  
**Scope:** USOP Core  
**Persistence model:** Derived projection; not an authoritative database model

## 1. Purpose

The Operational Timeline Engine provides one canonical, extension-safe way to
assemble operational history across USOP.

It answers:

> What happened, in what order, to which subjects, and through which domain?

The timeline is a projection assembled from authoritative domain records. It is
not a duplicate source of truth and must not become a replacement audit store.

## 2. Architectural Statement

> **Timeline represents operational history, not database history.**

```text
Authoritative Domain Records
        │
        ▼
Timeline Contributors
        │
        ▼
Timeline Contributor Registry
        │
        ▼
Operational Timeline Engine
        │
        ▼
Operational Timeline Result
        │
        ▼
Any Timeline Renderer
```

## 3. Permanent Responsibility Boundary

### Contributors produce history

Each contributor:

- reads only its authoritative domain data;
- translates facts into canonical `TimelineEvent` objects;
- does not sort globally;
- does not render;
- does not modify source records;
- does not interpret events from other contributors.

### The engine produces chronology

The engine:

- resolves active contributors;
- invokes contributors independently;
- validates returned events;
- normalizes timestamps;
- detects duplicate event IDs;
- enforces Organization scope;
- merges and deterministically sorts events;
- applies query limits and cursors;
- returns diagnostics and partial-result status.

### Renderers produce presentation

The frontend:

- chooses icons and colors;
- groups dates;
- formats timestamps;
- renders summaries and metadata;
- does not recreate backend chronology rules.

## 4. Non-Goals for Sprint 28.3.3.1

This sprint does not:

- add a timeline database table;
- persist canonical timeline events;
- replace `AuditEvent`;
- replace authoritative domain models;
- implement production contributors;
- change frontend timeline components;
- introduce AI interpretation;
- introduce archive retrieval;
- add an API endpoint.

## 5. Package Boundary

```text
backend/app/timeline/
    __init__.py
    timeline_event.py
    timeline_query.py
    timeline_contributor.py
    timeline_contributor_descriptor.py
    timeline_contributor_registry.py
    operational_timeline_engine.py
    operational_timeline_result.py
```

Core timeline files must not import specific domain models such as:

- `AuthorizationEvent`
- `DecisionRecord`
- `PendingDecisionWorkItem`
- `KnowledgeAsset`
- extension-specific models
- provider-specific connector code

## 6. Canonical Timeline Event

`TimelineEvent` is a Pydantic schema, not a SQLAlchemy model.

```python
class TimelineSubjectReference(BaseModel):
    subject_type: str
    subject_id: str
    label: str | None = None


class TimelineEvent(BaseModel):
    event_id: str
    occurred_at: datetime
    category: TimelineCategory
    visibility: TimelineVisibility
    title: str
    summary: str | None = None
    actor: str | None = None

    contributor_name: str
    contributor_version: str

    source_type: str
    source_id: str
    organization_id: str

    subject_references: list[TimelineSubjectReference]
    correlation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    schema_version: int = 1
```

### Stable event identity

`event_id` must be deterministic.

Examples:

```text
authorization-event:<id>:detected
pending-work:<id>:created
pending-work:<id>:resolved
decision-record:<id>:created
decision-record:<id>:approved
```

Random IDs are discouraged because they weaken caching, diffing, pagination,
bookmarks, and deterministic tests.

### Immutability

A timeline event describes a fact that occurred. State changes create additional
events; prior operational facts are not rewritten.

Because the timeline is assembled, immutability means stable event semantics
for the same authoritative source state, not a new persistence requirement.

## 7. Canonical Categories

Initial categories:

```text
Operational
Authorization
Identity
Decision
Knowledge
Governance
Threat
Cloud
Compliance
Asset
System
```

Categories represent operational domains, not database entities.

Adding a category requires architectural review because renderers, filters,
analytics, extensions, and AI consumers may depend on the shared vocabulary.

## 8. Timeline Visibility

Visibility is separate from risk.

Initial values:

```text
Information
Notice
Warning
Critical
```

The contributor maps domain meaning to visibility. The engine validates the
canonical value but does not reinterpret domain risk.

## 9. Subject References

Events support multiple related subjects.

```json
{
  "subject_references": [
    {
      "subject_type": "Identity",
      "subject_id": "identity-001",
      "label": "Alex Morgan"
    },
    {
      "subject_type": "PendingDecisionWorkItem",
      "subject_id": "work-001"
    },
    {
      "subject_type": "DecisionRecord",
      "subject_id": "decision-001"
    }
  ]
}
```

This avoids freezing the timeline around Identity and supports future:

- assets;
- cloud resources;
- threats;
- incidents;
- policies;
- vulnerabilities;
- customer archive packages.

## 10. Timeline Query

`TimelineQuery` is mandatory from version one.

```python
class TimelineQuery(BaseModel):
    organization_id: str

    subject_references: list[TimelineSubjectReference] = []
    identity_id: str | None = None
    work_item_id: str | None = None
    decision_id: str | None = None
    correlation_id: str | None = None

    categories: set[TimelineCategory] = set()
    visibility_levels: set[TimelineVisibility] = set()

    start_at: datetime | None = None
    end_at: datetime | None = None

    cursor: str | None = None
    limit: int = 100
    sort_direction: Literal["ascending", "descending"] = "descending"
```

Rules:

- `organization_id` is mandatory.
- Core enforces default and maximum limits.
- Contributors use only relevant fields.
- Contributors must not return cross-Organization data.
- The engine owns final ordering, limits, and cursor behavior.
- Time ranges use timezone-aware timestamps.

## 11. Stable Pagination

Offset pagination is prohibited for the canonical design.

The stable ordering key is:

```text
occurred_at + event_id
```

Cursor payloads are opaque to clients and internally versioned.

## 12. Contributor Contract

```python
class TimelineContributor(Protocol):
    descriptor: TimelineContributorDescriptor

    def contribute(
        self,
        query: TimelineQuery,
    ) -> list[TimelineEvent]:
        ...
```

Contributor rules:

- return canonical events;
- do not commit transactions;
- do not mutate authoritative records;
- do not globally sort;
- do not render;
- do not expose credentials or raw secrets;
- do not fabricate missing history;
- preserve uncertainty explicitly.

## 13. Contributor Descriptor

```python
class TimelineContributorDescriptor(BaseModel):
    name: str
    version: str
    display_name: str
    categories: set[TimelineCategory]

    priority: int = 100
    enabled_by_default: bool = True

    extension_id: str | None = None
    requires_license: bool = False

    schema_versions_supported: set[int] = {1}
```

The descriptor expresses capability and compatibility. It does not perform
licensing checks itself.

## 14. Contributor Registry

The registry owns:

- registration;
- duplicate-name rejection;
- descriptor lookup;
- deterministic ordering;
- activation filtering;
- compatibility filtering;
- registry diagnostics.

It must not:

- contain domain-specific construction logic;
- query domain data;
- interpret metadata;
- render events;
- mutate contributor output.

Conceptual API:

```python
registry.register(contributor)
registry.get(name)
registry.list_descriptors()
registry.active_contributors(context)
registry.validate()
```

## 15. Operational Timeline Engine

```python
class OperationalTimelineEngine:
    def __init__(
        self,
        registry: TimelineContributorRegistry,
    ):
        ...

    def build(
        self,
        query: TimelineQuery,
    ) -> OperationalTimelineResult:
        ...
```

Processing order:

```text
Validate Query
    ↓
Resolve Active Contributors
    ↓
Invoke Contributors Independently
    ↓
Collect Events and Diagnostics
    ↓
Validate Canonical Events
    ↓
Reject Cross-Organization Results
    ↓
Detect Duplicate Event IDs
    ↓
Normalize Timestamps
    ↓
Apply Filters
    ↓
Deterministically Sort
    ↓
Apply Cursor and Limit
    ↓
Return OperationalTimelineResult
```

## 16. Failure Isolation

A broken optional extension must not erase valid Core history.

If one contributor fails:

- successful events remain available;
- the failed contributor receives a diagnostic;
- the result is marked partial;
- no synthetic failure event is fabricated;
- client diagnostics do not expose stack traces or secrets.

Core may fail the full request only when a mandatory Core contributor or an
Organization isolation invariant fails.

## 17. Duplicate Event Policy

Duplicate event IDs are architectural defects.

Recommended first policy:

- identical duplicates: deduplicate and add a warning;
- conflicting duplicates: raise a deterministic engine error.

Silent last-write-wins behavior is prohibited.

## 18. Operational Timeline Result

```python
class TimelineContributorDiagnostic(BaseModel):
    contributor_name: str
    contributor_version: str
    status: Literal[
        "Succeeded",
        "Failed",
        "Skipped",
        "Unavailable",
    ]
    event_count: int = 0
    message: str | None = None


class OperationalTimelineResult(BaseModel):
    organization_id: str
    events: list[TimelineEvent]

    contributor_diagnostics:
        list[TimelineContributorDiagnostic]

    warnings: list[str] = []
    is_partial: bool = False

    next_cursor: str | None = None
    generated_at: datetime
    schema_version: int = 1
```

## 19. Deterministic Ordering

The global sort key is:

```python
(
    event.occurred_at,
    event.event_id,
)
```

Determinism is mandatory for:

- tests;
- pagination;
- caching;
- UI rendering;
- event diffing;
- AI consumption.

## 20. Organization Isolation

Rules:

- every query requires `organization_id`;
- contributors query within that Organization;
- every event carries the same Organization;
- the engine rejects mismatched events;
- diagnostics do not disclose cross-Organization existence;
- paid and customer-specific contributors receive identical isolation rules.

## 21. Metadata Boundary

Core may:

- require a JSON-compatible object;
- preserve metadata;
- apply future size or redaction limits.

Core must not:

- branch on provider-specific keys;
- interpret extension-specific meaning;
- store credentials;
- expose unrestricted source payloads;
- depend on metadata for canonical sorting or Organization scope.

Essential meaning belongs in canonical fields.

## 22. Licensing and Extension Boundary

Future extensions register contributors such as:

```text
ThreatTimelineContributor
CloudTimelineContributor
ComplianceTimelineContributor
```

Activation is controlled by the applicable licensing and extension service.

The engine must never contain logic such as:

```python
if contributor.name == "Threat":
```

An unlicensed extension must not operationalize external content merely because
the timeline engine can represent it.

## 23. Customer-Owned Archive Compatibility

ADR-029 applies immediately.

A timeline event may reference:

- active database records;
- USOP Archive Packages;
- Azure Blob objects;
- S3 objects;
- on-prem archives;
- rehydrated artifacts.

The timeline contract describes meaning and references. It does not assume the
physical storage location of long-term knowledge.

Core must not automatically retrieve or analyze archived content solely because
a timeline event references it.

## 24. Security Requirements

Contributors and results must not expose:

- connector credentials;
- access tokens;
- secret-provider values;
- authentication headers;
- unrestricted source payloads;
- cross-Organization identifiers;
- sensitive metadata without an explicit contract.

The architecture must allow future metadata-redaction policies without changing
the contributor interface.

## 25. Performance Evolution

The first implementation assembles contributor results in memory.

Future optimization may add:

```text
Authoritative Domain Records
        ↓
Contributors
        ↓
Rebuildable Timeline Projection Cache
        ↓
Operational Timeline Engine
```

Any cache must remain:

- derived;
- disposable;
- rebuildable;
- Organization-scoped;
- versioned;
- non-authoritative.

Timeline must not become a second ownership store.

## 26. Existing Timeline Evolution

Existing components remain untouched during the foundation sprint:

- `IdentityTimelineService`
- `IdentityTimelineBuilder`
- `DecisionTimelinePanel`

They are specialized and are not the canonical extension contract.

Migration follows ADR-017:

```text
Build Canonical Engine
    ↓
Add Contributors
    ↓
Validate Output
    ↓
Migrate Consumers
    ↓
Retire Specialized Paths
```

## 27. Required Foundation Tests

1. Empty registry returns an empty, non-partial result.
2. One contributor returns validated events.
3. Multiple contributors merge in deterministic order.
4. Duplicate contributor names are rejected.
5. Invalid categories fail validation.
6. Invalid visibility values fail validation.
7. Cross-Organization events are rejected.
8. Contributor failure produces a partial result and diagnostic.
9. Ordering uses `occurred_at` and `event_id`.
10. Query limits are enforced.
11. Duplicate event IDs follow the explicit policy.
12. Metadata remains opaque to the engine.
13. Registry order is deterministic.
14. Event and result schema versions are exposed.
15. No SQLAlchemy model or migration is introduced.

## 28. Extension-Proof Acceptance Test

A future domain must be able to contribute history by adding only:

```python
class FutureDomainTimelineContributor:
    descriptor = TimelineContributorDescriptor(...)

    def contribute(
        self,
        query: TimelineQuery,
    ) -> list[TimelineEvent]:
        ...
```

It must not require changes to:

- the canonical event;
- the registry;
- the engine;
- existing contributors;
- frontend rendering of canonical fields.

## 29. Design Rules

1. Timeline is assembled, not owned.
2. Timeline is a projection, not a second audit database.
3. Contributors produce history.
4. The engine produces chronology.
5. Renderers produce presentation.
6. Organization scope is mandatory.
7. Core contains no domain-specific timeline branches.
8. Contributor failures are isolated and visible.
9. Event IDs and ordering are deterministic.
10. Archive location remains outside timeline semantics.
11. Extensions register capabilities rather than modify Core.
12. Metadata remains opaque to Core.
13. Existing specialized timelines evolve only after the foundation is proven.
14. Schema changes are versioned.
15. Operational history must remain understandable independently of database
    implementation details.

## 30. Sprint 28.3.3.1 Definition of Done

The sprint is complete when:

- the Core timeline package exists;
- canonical schemas validate;
- contributor protocol and descriptor are defined;
- the registry supports deterministic registration and discovery;
- the engine validates, merges, sorts, limits, and diagnoses contributor output;
- failures produce partial results without hiding valid events;
- the full backend regression passes;
- no UI, API, migration, or production contributor is added;
- existing timeline implementations remain unchanged;
- the work is committed as one focused backend architecture sprint.

## 31. Governing Principle

> **Timeline contributors produce history.  
> The Operational Timeline Engine produces chronology.  
> Timeline renderers produce presentation.**

This is the permanent extension boundary for operational history in USOP.
