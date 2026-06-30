# API Architecture

Version: 0.1

Status: Draft

---

# Purpose

The USOP API provides a versioned, secure, REST-first interface for all platform functionality.

The API is the contract between Mission Control, automation, integrations, plugins, future mobile applications, and external systems.

No client communicates directly with internal engines.

All interactions occur through the API Gateway.

---

# Design Principles

REST First

OpenAPI Generated

Stateless

Versioned

JSON Everywhere

OAuth2/OIDC Protected

Role-Based Authorization

Idempotent Operations

Consistent Error Responses

Pagination by Default

---

# API Gateway Responsibilities

Authentication

Authorization

Rate Limiting

Request Validation

API Versioning

Audit Logging

Routing

Response Normalization

---

# Versioning Strategy

/api/v1/

/api/v2/

Older versions remain supported according to platform support policy.

---

# Authentication

OIDC

OAuth2

SAML

Future:

API Keys

Service Accounts

Mutual TLS

---

# Authorization

RBAC

Future:

ABAC

Relationship-aware authorization

Context-aware authorization

---

# Core API Domains

/api/v1/identities

/api/v1/accounts

/api/v1/service-accounts

/api/v1/applications

/api/v1/assets

/api/v1/relationships

/api/v1/tasks

/api/v1/events

/api/v1/journal

/api/v1/evidence

/api/v1/frameworks

/api/v1/controls

/api/v1/policies

/api/v1/procedures

/api/v1/risks

/api/v1/poams

/api/v1/connectors

/api/v1/search

/api/v1/dashboard

---

# API Standards

Every resource supports:

GET

POST

PUT

PATCH

DELETE

LIST

SEARCH

---

# Response Format

{
  "success": true,
  "data": {},
  "metadata": {},
  "links": {}
}

---

# Error Format

{
  "success": false,
  "error": {
      "code": "",
      "message": "",
      "details": []
  }
}

---

# Pagination

limit

offset

cursor (future)

---

# Filtering

status

owner

framework

control

date

connector

risk

priority

search

---

# Sorting

created_date

updated_date

priority

severity

confidence

name

status

---

# Future APIs

GraphQL

Streaming Events

Webhook Framework

Plugin SDK

CLI

Python SDK

Go SDK

PowerShell SDK

Terraform Provider

---

# Architecture Notes

The API is intentionally independent of Mission Control.

Future clients should include:

Mobile

CLI

Automation

Partner Integrations

AI Assistants

without changing business logic.
