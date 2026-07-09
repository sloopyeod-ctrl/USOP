# USOP Engineering Handbook

Welcome to the engineering documentation for the **Unified Security Operations Platform (USOP)**.

This documentation describes the vision, architecture, engineering standards, development process, and long-term roadmap for the platform.

Unlike the repository README, these documents are intended for engineers, architects, contributors, and anyone interested in understanding how USOP is designed and why architectural decisions were made.

---

# Documentation Map

## Vision

**Document**

`VISION.md`

**Purpose**

Defines the long-term vision of USOP, the problems it aims to solve, and the guiding principles that shape the platform.

---

## Platform Architecture

**Document**

`architecture/ARCHITECTURE.md`

**Purpose**

Describes the layered architecture of USOP including:

- platform layers
- backend architecture
- frontend architecture
- intelligence pipeline
- rendering pipeline
- architectural principles

---

## Architecture Documents

Located in:

```
docs/architecture/
```

Current documents include:

- API Architecture
- Backend Architecture
- Frontend Architecture
- Graph Pipeline
- Workspace State
- Decision Engine
- Transition Engine
- Animation Pipeline
- System Context
- Data Flow Architecture
- Reference Architecture
- Technology Decisions

---

## Architecture Decision Records (ADR)

Located in:

```
docs/architecture/adr/
```

Architecture Decision Records document significant engineering decisions made throughout the development of USOP.

Every major architectural decision should be captured as an ADR before or during implementation.

---

## Development Standards

**Document**

```
development/DEVELOPMENT_STANDARDS.md
```

Defines the engineering process used during development including:

- coding philosophy
- architecture principles
- testing expectations
- Git workflow
- review process
- definition of done

---

## Sprint Documentation

Located in:

```
docs/development/
```

Each sprint documents:

- objectives
- completed milestones
- lessons learned
- architectural changes
- release summary

---

## Product Documentation

Located in:

```
docs/product/
```

Contains long-term product planning including:

- Product Requirements
- Functional Requirements
- Branding
- Product Vision
- Product Roadmap

---

## UX Documentation

Located in:

```
docs/ux/
```

Contains user experience documentation for major workspaces and future interface concepts.

---

## Compliance Documentation

Located in:

```
docs/compliance/
```

Documents future compliance capabilities including:

- CMMC
- NIST SP 800-171
- Additional compliance frameworks

---

# Engineering Philosophy

USOP follows several architectural principles.

- Backend Intelligence is the source of truth.
- Engines produce intelligence.
- Services coordinate workflows.
- Adapters translate between layers.
- Renderers display intelligence.
- Pages orchestrate user workflows.
- Documentation evolves with the platform.

These principles are documented throughout this handbook.

---

# Current Platform Status

Current Version

```
v1.0-alpha
```

Current Development Phase

```
Sprint 10
Theme:
Productization
```

Current Focus

- Engineering documentation
- Platform architecture
- Repository productization
- Engineering standards
- Documentation consistency

---

# Repository Structure

```
USOP

backend/
frontend/
docs/

docker/

scripts/

tests/
```

The platform is intentionally organized around modular architecture and clearly separated responsibilities.

---

# Documentation Standards

Every major capability should be documented.

Preferred order:

1. Vision
2. Architecture
3. Engineering Standards
4. Roadmap
5. Detailed subsystem documentation
6. Sprint documentation

Documentation is considered part of the implementation rather than an afterthought.

---

# Contributing

Future contributors should read the following documents before making architectural changes:

1. Vision
2. Architecture
3. Engineering Standards

These documents establish the engineering philosophy that guides the development of USOP.

---

# Future Documentation

Planned additions include:

- Live Connector Guide
- Investigation Workspace Guide
- AI Analyst Design
- Plugin Development Guide
- Deployment Guide
- Operations Guide
- Performance Guide
- Security Hardening Guide

---

# Closing Statement

USOP is being engineered as a modular, intelligence-driven cybersecurity platform.

This handbook exists to ensure that the architecture, engineering standards, and long-term vision evolve alongside the software itself.