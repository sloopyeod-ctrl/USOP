# USOP Patch and Rebuild Procedure

## Purpose

This procedure defines how USOP should respond to dependency, application, or base-image security updates without allowing patch activity to bypass regression or release controls.

## Patch Triggers

A patch cycle may be triggered by:

- newly disclosed vulnerability;
- dependency advisory;
- base-image update;
- Microsoft Graph or platform compatibility change;
- defect;
- security configuration change;
- customer-reported issue;
- scheduled release-health review.

## Step 1 — Identify the Affected Layer

Classify the issue as:

```text
Application code
Python runtime dependency
Frontend dependency
API base image
Web base image
PostgreSQL upstream image
Deployment configuration
Customer documentation
```

Do not update unrelated layers merely because newer versions exist.

## Step 2 — Determine Fix Availability

For each finding, determine:

- affected version;
- fixed version;
- whether the finding exists in the actual shipped artifact;
- whether the package is used at runtime;
- whether the finding is inherited from an upstream image;
- whether remediation introduces a compatibility change.

## Step 3 — Patch Deliberately

Preferred order:

1. smallest safe patch;
2. compatible minor update where required;
3. major/runtime transition only after explicit compatibility testing.

Do not use force-upgrade behavior merely to produce a lower scanner count.

## Step 4 — Rebuild from Release Inputs

Rebuild the affected image from the release Dockerfile.

Use fresh base-image pulls when evaluating current security state.

Do not patch a running customer container interactively.

The container should be replaced by a validated rebuilt artifact.

## Step 5 — Run the Applicable Validation Gates

### Backend Change

Run:

- backend regression;
- dependency integrity;
- API image build;
- API runtime validation;
- API vulnerability scan.

### Frontend Change

Run:

- full npm audit;
- production npm audit;
- lint;
- build;
- web image scan.

### Base-Image Change

Run:

- full affected service build;
- health validation;
- vulnerability scan;
- runtime-user validation;
- clean-room deployment validation when the change may affect installation.

### PostgreSQL Change

Run:

- database startup;
- application connectivity;
- migration validation;
- backup/restore validation where applicable;
- regression;
- vulnerability scan.

## Step 6 — Regenerate Supply-Chain Evidence

For every patched release:

- regenerate SBOM;
- regenerate provenance;
- capture new immutable digests;
- update vulnerability exception register;
- update release manifest.

Never carry an old digest forward after rebuilding an image.

## Step 7 — Update Customer Documentation

If the patch changes any of the following, update the customer documentation:

- required environment variables;
- image identifiers;
- ports;
- Graph permissions;
- prerequisites;
- upgrade procedure;
- rollback procedure;
- known limitations;
- supported versions.

## Step 8 — Clean-Room Validation

A patch that changes deployment-critical behavior should be installed on a clean host using the release package and customer documentation.

## Step 9 — Freeze and Publish

A patch release is publishable only when the exact rebuilt artifact has passed the required validation gates.

## Rollback Principle

Do not assume rollback is equivalent to replacing a container image.

Before publishing a patch, confirm whether database migrations, persistent state, configuration changes, or dependency changes affect rollback compatibility.

## Emergency Patch Principle

Urgency may shorten administrative delay.

Urgency does not eliminate:

- regression testing;
- vulnerability review;
- artifact identity;
- digest capture;
- required security validation.

If a full non-security validation cannot be completed before an emergency security release, document the reduced scope explicitly and schedule immediate post-release validation.

## Maintenance Principle

> Patch the layer that needs repair, rebuild the immutable artifact, prove it still works, scan it again, and only then replace what the customer runs.
