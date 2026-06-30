ADR-009: Engine-First Architecture

Version: 1.0
Status: Accepted
Author: Marvin G. Dewitt

Context

USOP contains multiple business capabilities including connectors, normalization, relationships, operational intelligence, workflows, knowledge, evidence, compliance, and Mission Control.

Placing business logic inside the UI would make the platform harder to test, scale, and maintain.

Decision

USOP will use an Engine-First Architecture.

Business logic belongs inside platform engines.

Mission Control and future clients consume engine outputs through APIs.

Consequences

The UI remains a presentation layer.

Future clients such as mobile apps, CLI tools, APIs, plugins, and AI assistants can use the same business logic.

Product Principle

Business logic belongs in engines, not interfaces.
