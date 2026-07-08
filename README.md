# USOP

# USOP — Unified Security Operations Platform

USOP is an Identity Governance and Intelligence platform built with FastAPI, PostgreSQL, SQLAlchemy, and Alembic.

It models identities, accounts, groups, roles, permissions, access reviews, governance policies, risk analytics, exposure scoring, recommendations, synchronization, reconciliation, and identity intelligence.

## Current v1 Capabilities

### Identity Governance
- Identity inventory
- Accounts
- Groups
- Roles
- Permissions
- Memberships
- Role assignments
- Access reviews
- Review campaigns
- Reviewer workbench

### Risk and Governance
- Identity risk scoring
- Governance policy engine
- Policy action engine
- Automated review creation
- Audit event tracking

### Synchronization Pipeline
- Connector framework
- Entra connector foundation
- Synchronization engine
- Normalization engine
- Reconciliation engine
- Graph change detection
- Change event engine

### Identity Intelligence
- Identity graph
- Identity timeline
- Exposure score engine
- Recommendation engine
- Executive exposure dashboard

## Architecture

```text
Connectors
    ↓
Synchronization Engine
    ↓
Normalization Engine
    ↓
Reconciliation Engine
    ↓
Identity Graph
    ↓
Risk Engine / Policy Engine / Review Engine
    ↓
Identity Intelligence / Executive Dashboard

# Why I Built USOP

Throughout my career I have worked in military operations, federal security, cloud security, vulnerability management, endpoint security, identity management, and CMMC compliance.

One thing became consistently clear:

Security data exists everywhere, but rarely in one place.

Most organizations have:

- Active Directory / Entra ID
- Cloud IAM
- Endpoint Management
- SIEM
- Vulnerability Management
- CMDB
- Ticketing Systems

Analysts spend significant time pivoting between systems to answer relatively simple questions.

USOP is my attempt to model security data as a unified platform rather than a collection of disconnected tools.

---


## Intelligence

### Identity Access Summary

```
### Key Endpoints
GET  /identities/
GET  /accounts/
GET  /groups/
GET  /roles/
GET  /access-reviews/
GET  /review-campaigns/
GET  /reviewer-workbench/
GET  /executive-dashboard/
GET  /executive-exposure-dashboard/
GET  /identity-graph/{identity_id}
GET  /identity-intelligence/{identity_id}
POST /governance-jobs/run-synchronization/{connector_name}
POST /governance-jobs/run-identity-risk-analysis
```


# Getting Started

Clone the repository

```bash
git clone https://github.com/sloopyeod-ctrl/USOP.git
```

Start the application

```bash
docker compose up
```

Run the API locally

```bash
cd backend

python -m venv .venv

source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Swagger

```
http://127.0.0.1:8000/docs
```

---

# Architecture Decision Records

USOP uses ADRs to document architectural decisions.

Examples include:

- ADR-001 Project Principles
- ADR-012 Database Strategy
- ADR-013 Identity Domain Model

Every major architectural change is documented before implementation.

---

# Current Roadmap

## ✅ v0.1.0

Platform Foundation

- FastAPI
- Docker
- PostgreSQL
- Alembic
- SQLAlchemy

---

## ✅ v0.2.0

Identity Graph

- Identity
- Accounts
- Groups
- Memberships
- Roles
- Permissions
- Identity Access Summary
- Domain Scaffold Generator

---

Example Intelligence Output

The Identity Intelligence API combines:

Identity profile
Risk score
Exposure score
Access graph
Timeline
Recommendations

Example:

GET /identity-intelligence/{identity_id}

Returns identity risk, exposure rating, access paths, recent activity, and prioritized remediation recommendations.

Tech Stack
Python
FastAPI
PostgreSQL
SQLAlchemy
Alembic
Pydantic
Uvicorn
Project Status

USOP is currently in active v1 development.

Completed:

Core identity model
Governance workflows
Policy and risk engines
Synchronization and reconciliation
Identity intelligence
Executive exposure dashboard

Planned:

AI security copilot
Real Microsoft Graph connector
Scheduled background jobs
Frontend dashboard
Workflow approvals
Ticketing integrations
---

# About the Author

Marvin G. Dewitt

Retired U.S. Army Master Sergeant (EOD)

Security Engineer

Bachelor of Applied Science
Computer Information Systems – Cloud Computing

Areas of Interest

- Cloud Security
- Identity & Access Management
- Security Engineering
- Threat Detection
- Vulnerability Management
- Enterprise Architecture
- Security Operations

---

## License

MIT License

---
