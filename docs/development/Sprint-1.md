Epic 1 — Backend Foundation
FastAPI application skeleton
Configuration management
Database connection
Health endpoint
Version endpoint
Logging framework
Epic 2 — Identity Domain
Identity model
Account model
Database migrations
Repository layer
Service layer
Epic 3 — Connector Framework
Base connector interface
Connector scheduler
Connector configuration
Sync status tracking
Epic 4 — Entra Connector (Mock First)

This is an important architectural decision:

Don't connect to Microsoft Graph first.

Instead, use a mock connector with realistic JSON.

Why?

Faster development
Repeatable tests
No cloud dependency
Easier debugging
Deterministic results

Once the pipeline works, swapping in Microsoft Graph becomes straightforward because the connector interface remains the same.
