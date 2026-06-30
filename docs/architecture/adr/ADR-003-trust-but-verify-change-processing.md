ADR-003: Trust but Verify Change Processing

Version: 1.0
Status: Accepted
Author: Marvin G. Dewitt

Context

USOP will receive data from connectors and detect changes across identity, access, assets, evidence, risks, and documentation.

Some changes may be high confidence. Others may require human review.

Decision

USOP will use a Trust but Verify model.

Automation may detect and propose changes, but operationally significant changes require engineer review before becoming verified operational truth.

Consequences

Connectors submit change proposals.

Engineers approve, reject, or investigate proposed changes.

All decisions are recorded in the Operational Journal.

Product Principle

Automation proposes. Engineers approve.
