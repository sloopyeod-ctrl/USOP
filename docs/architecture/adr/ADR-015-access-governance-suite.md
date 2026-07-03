# ADR-015: Access Governance Suite

Version: 1.0  
Status: Accepted  
Author: Marvin G. Dewitt  

---

## Context

USOP has evolved from an identity inventory into an identity graph with an analytics foundation.

The platform can currently model identities, accounts, groups, memberships, roles, role assignments, permissions, and role permissions. It also includes initial analytics for privileged identities and orphaned accounts.

To continue growing methodically, USOP needs a defined Access Governance Suite that groups related analytics capabilities around identity and access risk.

---

## Decision

USOP will implement an Access Governance Suite as part of the analytics layer.

The suite will focus on answering operational security and governance questions, including:

- Which identities are privileged?
- Which accounts are orphaned?
- Which accounts are dormant?
- Which privileged accounts are stale?
- Which identities have elevated access?
- Which identities require review?
- What is the overall access risk posture?

The analytics layer will remain separate from CRUD services.

---

## Initial Capabilities

The Access Governance Suite will include:

1. Privileged Identities
2. Orphaned Accounts
3. Dormant Accounts
4. Stale Privileged Accounts
5. Shared Accounts
6. High-Risk Permissions
7. Identity Risk Summary
8. Analytics Dashboard
9. Access Review Recommendations

---

## Architecture

USOP will use the following structure:

```text
API
  ↓
Analytics Service
  ↓
Analyzers
  ↓
Repositories / Models