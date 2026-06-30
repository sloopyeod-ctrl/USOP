ADR-002: Operational Source of Truth

Version: 1.0
Status: Accepted
Author: Marvin G. Dewitt

Context

USOP connects to authoritative systems such as Entra ID, GitHub, SharePoint, Tenable, NetBox, Keeper, Docker, Azure, AWS, and Sentinel.

Each external system remains authoritative for the data it owns.

Decision

USOP will serve as the Operational Source of Truth.

USOP will not replace authoritative systems. Instead, it will collect, normalize, correlate, and present operational intelligence from those systems.

Consequences

USOP stores relationships, metadata, verification status, operational history, evidence mappings, and workflow state.

Authoritative systems remain responsible for operational records.

Product Principle

USOP references authoritative systems. It does not replace them.
