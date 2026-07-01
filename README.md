# USOP

# USOP
## Unified Security Operations Platform

> An enterprise security platform designed to model identities, access, applications, infrastructure, and investigations as a connected security graph.

![Version](https://img.shields.io/badge/version-v0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

# Overview

USOP (Unified Security Operations Platform) is a security engineering project focused on building an enterprise-grade platform for identity governance, access analysis, security operations, and future investigation workflows.

Rather than treating identities, accounts, permissions, applications, and infrastructure as isolated records, USOP models them as a connected graph that enables security analysts to answer complex operational questions.

Examples include:

- What permissions does this identity actually have?
- Which accounts belong to this person?
- What privileged groups does this account belong to?
- Which roles grant access to a specific application?
- What resources are reachable through inherited permissions?

The long-term goal is to evolve USOP into a modern Security Operations Platform capable of supporting identity governance, cloud security, investigations, evidence management, and security analytics.

---

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

# Current Architecture

```
                    Identity
                        │
        ┌───────────────┴───────────────┐
        │                               │
 Identity Attributes                Accounts
                                        │
                              Memberships
                                        │
                                    Groups

                                        │

                               Role Assignments
                                        │
                                     Roles
                                        │
                               Role Permissions
                                        │
                                  Permissions
```

Current graph traversal:

```
Identity
    ↓
Accounts
    ↓
Memberships
    ↓
Groups

Accounts
    ↓
Role Assignments
    ↓
Roles
    ↓
Permissions
```

---

# Current Features

## Identity Management

- Identity records
- Identity attributes
- Identity lifecycle
- Source tracking
- Confidence scoring

## Account Management

- User accounts
- System ownership
- Authentication methods
- Privilege levels

## Authorization

- Groups
- Memberships
- Roles
- Role Assignments
- Permissions
- Role Permissions

## Intelligence

### Identity Access Summary

```
GET /api/v1/identities/{id}/access-summary
```

Returns:

- Identity
- Accounts
- Groups
- Roles
- Permissions

This represents the first analytical endpoint within USOP.

---

# Technology Stack

Backend

- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL

Infrastructure

- Docker
- Docker Compose

Architecture

- ADR (Architecture Decision Records)
- Repository Pattern
- Service Layer
- Vertical Slice Architecture

Documentation

- OpenAPI / Swagger
- ADR Documentation

Development

- Git
- GitHub
- Python 3.11

---

# Project Structure

```
backend/
    app/
        api/
        models/
        repositories/
        schemas/
        services/

    migrations/

    scripts/

docs/
    architecture/
        adr/

docker/

```

---

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

## 🚧 v0.3.0

Applications

Resources

Entitlements

Application Access Summary

---

## Planned

Azure Entra ID Connector

Microsoft Graph API Integration

AWS IAM Integration

Risk Scoring Engine

Security Findings

Investigations

Evidence Management

Timeline Analysis

Graph Visualization

React Frontend

Authentication

RBAC

CI/CD

Unit Testing

Integration Testing

---

# Current Capabilities

| Capability | Status |
|------------|--------|
| Identity Management | ✅ |
| Account Inventory | ✅ |
| Group Management | ✅ |
| Role Management | ✅ |
| Permission Modeling | ✅ |
| Identity Access Summary | ✅ |
| Application Modeling | 🚧 |
| Resource Modeling | 🚧 |
| Investigation Management | Planned |
| Risk Scoring | Planned |
| Security Analytics | Planned |

---

# Project Status

Current Release

**v0.2.0 – Identity Graph**

USOP currently provides a fully functional identity and authorization model with graph traversal capable of answering identity access questions across accounts, groups, roles, and permissions.

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
