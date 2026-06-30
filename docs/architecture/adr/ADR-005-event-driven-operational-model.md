ADR-005: Event-Driven Operational Model

Version: 1.0
Status: Accepted
Author: Marvin G. Dewitt

Context

Security operations are driven by change.

Examples include new users, role changes, service account changes, policy updates, vulnerabilities, evidence expiration, and connector failures.

Decision

USOP will use an event-driven operational model.

Meaningful changes become Operational Events.

Operational Events may generate tasks, reviews, journal entries, evidence updates, risks, or compliance updates.

Consequences

USOP does not rely on engineers manually searching for changes.

The platform detects meaningful changes and routes them into operational workflows.

Product Principle

Security Engineers should review meaningful changes, not hunt for them.
