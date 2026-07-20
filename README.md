# USOP

# USOP — Unified Security Operations Platform

> **An intelligence-driven cybersecurity platform that unifies identity, governance, attack-path analysis, risk analytics, and security operations into a single analyst workspace.**

![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)
![Version](https://img.shields.io/badge/Version-v1.0--alpha-blue)
![Sprint](https://img.shields.io/badge/Sprint-10-orange)
![License](https://img.shields.io/badge/License-MIT-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![React](https://img.shields.io/badge/React-Frontend-61DAFB)

---

# What is USOP?

Modern security teams operate across dozens of disconnected security products.

Identity lives in one platform.

Endpoint telemetry lives in another.

Vulnerability data lives somewhere else.

Security alerts, cloud resources, governance workflows, ticketing systems, and compliance evidence are often scattered across multiple tools.

USOP was created to solve that problem.

Rather than treating security as a collection of disconnected technologies, USOP models the enterprise as a connected intelligence platform that enables analysts to investigate, visualize, simulate, prioritize, and understand security risk from a single workspace.

---

# Why USOP?

Security operations should answer questions—not create more of them.

USOP is designed to help security teams answer questions such as:

* Which identities present the greatest enterprise risk?
* How can an attacker move through my environment?
* Which remediation provides the greatest reduction in risk?
* What changed after remediation?
* Which vulnerabilities create exploitable attack paths?
* How can technical findings be explained to leadership?

The goal is to reduce investigation time while improving the quality of security decisions.

---

# Current Platform Capabilities

## Identity Intelligence

* Identity graph
* Identity timeline
* Exposure scoring
* Risk analytics
* Recommendation engine

## Identity Governance

* Accounts
* Groups
* Roles
* Permissions
* Memberships
* Access Reviews
* Review Campaigns
* Governance workflows

## Attack Path Intelligence

* Attack graph generation
* Attack path ranking
* Replay engine
* Simulation engine
* Transition engine
* Graph visualization

## Decision Intelligence

* Decision Intelligence Engine
* Simulation comparison
* Remediation recommendations
* Executive decision summaries

## Analyst Workspace

* Interactive graph visualization
* Mission context
* Decision Intelligence panel
* Animated graph rendering
* Attack replay
* Simulation reset
* Animated risk metrics

---

# Platform Architecture

```text
External Security Platforms
        │
        ▼
Synchronization Layer
        │
        ▼
Identity Graph
        │
        ▼
Workspace State Engine
        │
 ┌──────┼────────────┐
 ▼      ▼            ▼

Graph  Decision  Transition
Engine Engine     Engine

        ▼
Animation Pipeline

        ▼
Analyst Workspace
```

---

# Engineering Principles

USOP is engineered around several core principles.

* Backend intelligence is the source of truth.
* Engines produce intelligence.
* Services coordinate workflows.
* Adapters translate between architectural layers.
* Renderers display intelligence.
* Pages orchestrate user experiences.
* One architectural responsibility per commit.
* Documentation evolves with the platform.

---

# Technology Stack

### Backend

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Docker

### Frontend

* React
* Material UI
* React Flow
* Recharts
* Vite

---

# Engineering Handbook

Detailed engineering documentation is available in the `/docs` directory.

Current documentation includes:

* Vision
* Platform Architecture
* Engineering Standards
* Architecture Decision Records (ADRs)
* Roadmap
* Release Notes
* Sprint Documentation

---

# Getting Started

Clone the repository:

```bash
git clone https://github.com/sloopyeod-ctrl/USOP.git
```

Start the platform:

```bash
docker compose up
```

Run the backend locally:

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# Roadmap

## Completed

* Platform Foundation
* Identity Governance
* Identity Intelligence
* Analyst Workspace
* Decision Intelligence
* Attack Path Analysis
* Simulation Engine
* Transition Engine
* Graph Animation Pipeline

## In Progress

* Productization
* Engineering Handbook
* Documentation
* Repository modernization

## Planned

* Microsoft Entra ID connector
* Microsoft Graph integration
* Microsoft Sentinel ingestion
* BloodHound integration
* Tenable integration
* AI Security Analyst
* Investigation sessions
* Timeline replay
* Plugin architecture
* Enterprise reporting

---

# Current Status

**Version:** v1.0-alpha

**Current Sprint:** Sprint 10

**Theme:** Productization

USOP is under active development with a focus on modular architecture, intelligence-driven design, and enterprise security operations.

---

# About the Author

**Marvin G. Dewitt**

Retired U.S. Army Master Sergeant (EOD)

Cloud Security Engineer • Security Platform Engineer • Identity & Access Management • Enterprise Cybersecurity Architecture

USOP represents my vision for a modern, intelligence-driven security operations platform that unifies identity, governance, attack-path analysis, decision intelligence, and analyst workflows into a single operational experience.

---

# License

## License and Ownership

© 2026 Marvin Dewitt. All rights reserved.

This repository contains the public artifacts of the Marvin Security Platform.
The core backend and associated services are licensed separately and are
not open source.

Use of this platform, including its backend services and APIs, is governed
by the proprietary Marvin Security Platform License. For licensing inquiries,
contact: mgeoffdewitt@gmail.com
