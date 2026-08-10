# RC-002.3 - Production Deployment Architecture

## Objective

Convert the development-oriented Docker topology into a customer-ready release topology without disturbing the existing developer workflow.

## Release Topology

```text
Customer Browser
        |
        v
USOP Web Container
Nginx + built React assets
        |
        +---- /api/* ----> USOP API :8000
        |
        +---- /health ---> USOP API :8000/health
                           |
                           v
                       PostgreSQL
                     internal network
```

## Security Properties

- PostgreSQL is not published to the host.
- The API is not published to the host.
- Only the web service is customer-facing by default.
- Development source-code bind mounts are removed.
- Database credentials are customer supplied.
- Microsoft Graph credentials are customer supplied.
- RC1 secret provider is explicitly `env`.
- The API runs as a non-root user.
- Frontend assets are compiled into an immutable image.
- Web-to-API traffic uses service discovery on the Docker network.
- Health checks gate dependent service startup.

## Patchability

Release images remain split by responsibility:

- `usop-api`
- `usop-web`
- `postgres`

This allows API, web, and database base images to be patched and validated independently while preserving the same customer-facing topology.

Every dependency or base-image update must trigger regression validation before a new release artifact is frozen.

## Important RC1 Boundaries

This step does not yet claim:

- final image digests;
- final Docker or Compose minimum versions;
- final TLS termination;
- final Graph permission matrix;
- Keeper support;
- pagination support;
- PIM eligibility or activation-history support;
- production scale limits.

Those remain explicit release gates.
