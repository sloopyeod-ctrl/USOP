erDiagram
    IDENTITY ||--o{ ACCOUNT : has
    IDENTITY ||--o{ SERVICE_ACCOUNT : owns
    IDENTITY ||--o{ TASK : assigned
    IDENTITY ||--o{ OPERATIONAL_JOURNAL : authors

    APPLICATION ||--o{ ACCOUNT : contains
    APPLICATION ||--o{ SERVICE_ACCOUNT : uses
    APPLICATION }o--o{ ASSET : runs_on

    ASSET ||--o{ SERVICE_ACCOUNT : supports
    ASSET ||--o{ RISK : has
    ASSET ||--o{ EVIDENCE : produces

    CONNECTOR ||--o{ OPERATIONAL_EVENT : generates
    CONNECTOR ||--o{ ACCOUNT : discovers
    CONNECTOR ||--o{ ASSET : discovers

    OPERATIONAL_EVENT ||--o{ TASK : creates
    TASK ||--o{ OPERATIONAL_JOURNAL : records
    TASK ||--o{ EVIDENCE : produces

    FRAMEWORK ||--o{ CONTROL : contains
    CONTROL ||--o{ EVIDENCE : supported_by
    CONTROL ||--o{ POLICY : implemented_by
    CONTROL ||--o{ PROCEDURE_DOCUMENT : executed_by
    CONTROL ||--o{ RISK : has
    CONTROL ||--o{ POAM : remediated_by

    POLICY ||--o{ PROCEDURE_DOCUMENT : supported_by
    POLICY ||--o{ EVIDENCE : produces

    RISK ||--o{ POAM : creates
    POAM ||--o{ TASK : generates
    POAM ||--o{ EVIDENCE : produces

    RELATIONSHIP }o--|| IDENTITY : source_or_target
    RELATIONSHIP }o--|| ACCOUNT : source_or_target
    RELATIONSHIP }o--|| SERVICE_ACCOUNT : source_or_target
    RELATIONSHIP }o--|| APPLICATION : source_or_target
    RELATIONSHIP }o--|| ASSET : source_or_target
    RELATIONSHIP }o--|| CONTROL : source_or_target
    RELATIONSHIP }o--|| EVIDENCE : source_or_target
