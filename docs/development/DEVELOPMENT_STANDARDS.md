# USOP Development Standards

## Purpose

This document defines the engineering standards used during the development of the Unified Security Operations Platform (USOP).

These standards exist to ensure the platform remains modular, maintainable, testable, and extensible as new capabilities are added.

Every contribution should reinforce the architecture rather than increase technical debt.

---

# Engineering Philosophy

USOP is engineered as a commercial cybersecurity platform rather than a collection of features.

Every architectural decision should answer one question:

> Does this improve the platform without compromising its architecture?

If the answer is no, reconsider the implementation.

---

# Core Principles

## Backend Intelligence Is the Source of Truth

Security meaning belongs in backend intelligence engines.

Examples:

- Risk scoring
- Recommendations
- Decision Intelligence
- Graph Intelligence
- Transition Intelligence

Frontend components visualize intelligence.

They should never become the source of security reasoning.

---

## Engines Produce Intelligence

Business logic belongs in engines.

Examples:

- Graph Intelligence Engine
- Decision Intelligence Engine
- Transition Engine
- Policy Engine
- Recommendation Engine

Engines should not contain rendering logic.

---

## Services Coordinate

Services manage workflows.

Examples:

- Animation Service
- Synchronization Service
- Connector Services

Services coordinate.

They should not own business intelligence.

---

## Adapters Translate

Adapters convert one representation into another.

Examples include:

- React Flow adapters
- Render adapters
- Connector adapters

Adapters should not contain business logic.

---

## Renderers Display

Renderers display prepared information.

Renderers should never calculate security meaning.

---

## Pages Orchestrate

Pages coordinate user workflows.

Pages should not become business logic containers.

---

# Commit Standards

Every commit should represent one architectural responsibility.

Good examples:

- Add Decision Intelligence Engine
- Add Graph Transition Engine
- Integrate Transition Engine into Workspace State
- Add Reset Simulation

Avoid combining unrelated work into a single commit.

---

# Development Workflow

Every feature follows the same lifecycle.

1. Design
2. Build
3. Test
4. Review
5. Commit
6. Push

Do not skip review simply because the code compiles.

---

# Testing Standards

Before every commit:

- Verify browser behavior.
- Confirm expected functionality.
- Review Git diff.
- Check for whitespace errors.
- Confirm Vite (or backend) reports no runtime errors.

Only then should changes be committed.

---

# Git Standards

Commits should:

- Be small.
- Be reviewable.
- Be reversible.
- Represent one milestone.

Sprint milestones should be tagged.

Major architectural milestones should be documented.

---

# Documentation Standards

Major architectural changes require documentation updates.

Preferred order:

1. Vision
2. Architecture
3. Development Standards
4. Roadmap
5. Detailed subsystem documentation

Documentation is considered part of the implementation.

---

# Code Quality

Prioritize:

- readability,
- maintainability,
- modularity,
- consistency,
- explicit naming,
- single responsibility.

Avoid premature optimization.

Avoid unnecessary abstraction.

Favor clarity over cleverness.

---

# Architecture First

When implementing new functionality, prefer creating a reusable architectural layer over solving a single immediate problem.

Examples:

Instead of:

- directly animating a graph,

build:

- Transition Engine
- Animation Service
- Render Adapter

Future features should naturally reuse existing architecture.

---

# Platform Mindset

USOP should be engineered as though it may eventually support:

- multiple analysts,
- live security environments,
- enterprise deployments,
- AI-assisted investigations,
- plugin-based intelligence engines,
- cloud-native scaling.

Every design decision should consider future extensibility.

---

# Review Before Commit

Every commit should undergo a lightweight engineering review before being merged into the main branch.

The review process includes:

- Verify functionality in the running application.
- Confirm expected behavior after user interaction.
- Review the Git diff for unintended changes.
- Verify no build or runtime errors are present.
- Confirm the implementation follows the documented architecture.
- Ensure the commit represents a single architectural responsibility.

This process intentionally favors smaller, well-tested milestones over large feature drops.

The goal is to maintain a clean, understandable project history while minimizing regressions.

# Definition of Done

A feature is considered complete when:

- functionality works,
- tests pass,
- browser validation succeeds,
- documentation is updated (when applicable),
- Git diff is reviewed,
- code is committed with a meaningful message,
- repository remains clean.

---

# Guiding Principle

> Build software that is easy to extend, easy to understand, and difficult to break.

The long-term quality of the platform is more important than the short-term speed of feature delivery.
