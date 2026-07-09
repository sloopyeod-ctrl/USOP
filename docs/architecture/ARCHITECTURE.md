# USOP Architecture

## Overview

USOP (Unified Security Operations Platform) is designed as an intelligence-driven cybersecurity platform.

Rather than tightly coupling business logic, visualization, and data ingestion, USOP separates responsibilities into independent architectural layers.

Each layer performs one responsibility and exposes its output to the next layer.

This approach allows the platform to remain modular, testable, extensible, and suitable for future enterprise-scale capabilities.

---

## Platform Layers

USOP is organized into six primary architectural layers.

1. Connectors
2. Intelligence
3. State Management
4. Services
5. Rendering
6. User Experience

Each layer communicates only with adjacent layers.

This prevents business logic from leaking into visualization components while allowing new capabilities to be added without major refactoring.

# Architectural Principles

USOP follows several core principles.

## Backend Intelligence Is the Source of Truth

Security intelligence is produced by backend services.

The frontend visualizes intelligence.

Business logic should never migrate into visualization components.

---

## Intelligence Before Visualization

The platform first determines:

- what changed,
- why it changed,
- what it means,

before deciding how that information should be displayed.

---

## Single Responsibility

Every major subsystem owns exactly one responsibility.

Examples:

- Intelligence Engines generate intelligence.
- Services coordinate workflows.
- Adapters translate between layers.
- Renderers visualize.
- Pages orchestrate.

---

## Layered Architecture

```
                External Security Platforms

   Microsoft Entra ID
   Microsoft Sentinel
   Microsoft Defender
   Tenable
   BloodHound
   Future Connectors

                │
                ▼

      Synchronization Layer

                │
                ▼

        Identity Graph Platform

                │
                ▼

      Workspace State Engine

                │
     ┌──────────┼───────────┐
     ▼          ▼           ▼

Graph      Decision     Transition
Engine      Engine       Engine

     └──────────┼───────────┘
                ▼

     Graph Animation Service

                ▼

 Graph Render Animation Adapter

                ▼

         Graph Renderer

                ▼

      Analyst Workspace
```

---

# Backend Architecture

The backend owns all security reasoning.

Examples include:

- Identity Intelligence
- Risk Analytics
- Governance
- Synchronization
- Reconciliation
- Attack Path Analysis
- Recommendations
- Simulation

Backend APIs expose intelligence through FastAPI.

The frontend consumes these APIs without duplicating business logic.

---

# Frontend Architecture

The frontend is intentionally divided into several layers.

## Workspace State

Responsible for:

- current graph
- projected graph
- selections
- simulations
- replay state
- transition state

---

## Intelligence

Examples:

- Graph Intelligence
- Decision Intelligence
- Transition Intelligence

These modules calculate meaning.

---

## Services

Examples:

- Graph Animation Service

Services coordinate platform behavior.

---

## Adapters

Examples:

- Graph Render Animation Adapter

Adapters translate platform models into renderer-specific formats.

---

## Renderers

Examples:

- GraphRenderer

Renderers display prepared data.

They do not create intelligence.

---

## Components

Examples:

- AttackPathNode
- MissionContextPanel
- DecisionRenderer

Components visualize prepared information.

---

## Pages

Examples:

- AnalystWorkspace

Pages orchestrate user workflows.

---

# Current Intelligence Pipeline

```
Backend Intelligence
        │
        ▼
Workspace State
        │
        ▼
Graph Diff Engine
        │
        ▼
Graph Transition Engine
        │
        ▼
Graph Animation Service
        │
        ▼
Graph Render Animation Adapter
        │
        ▼
GraphRenderer
        │
        ▼
AttackPathNode
```

---

# Benefits

This architecture provides several advantages.

## Modularity

Subsystems evolve independently.

---

## Testability

Business logic can be tested without rendering.

---

## Maintainability

Responsibilities remain clearly separated.

---

## Extensibility

Future intelligence engines can be added without redesigning the frontend.

Examples include:

- AI Investigation Engine
- Threat Correlation Engine
- Vulnerability Intelligence Engine
- Timeline Engine

---

## Technology Independence

Visualization technologies may change without affecting intelligence generation.

---

# Current Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Docker

## Frontend

- React
- Material UI
- React Flow
- Recharts
- Vite

## Architecture

- Engine-first design
- State-driven UI
- API-first communication
- Modular rendering pipeline

# Future Evolution

The architecture is intentionally designed to support:

- live connectors
- streaming events
- WebSockets
- AI copilots
- investigation sessions
- replay timeline
- collaborative investigations
- multi-tenant deployments
- plugin-based intelligence engines

without requiring significant architectural redesign.

---

# Architecture Maturity

USOP is currently in the v1.0-alpha phase.

The core platform architecture is now established.

Future development is expected to focus primarily on expanding platform capabilities rather than restructuring the underlying architecture.

This allows future features to be developed within an already established engineering framework.

# Summary

USOP is designed around one central idea:

> Intelligence should drive visualization.

Security meaning belongs in engines.

Visualization belongs in renderers.

Maintaining this separation allows the platform to scale while remaining understandable and maintainable.