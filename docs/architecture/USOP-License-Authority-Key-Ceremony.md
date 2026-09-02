# USOP License Authority Key Ceremony

## 1. Purpose

This document defines the operational security contract for creation,
protection, use, rotation, backup, and compromise response of USOP License
Authority signing keys.

The private License signing key is a vendor-controlled commercial security
asset.

It must never become customer-controlled runtime material.


## 2. Initial Signing Authority

The first production USOP License signing authority identifier is:

`usop-license-root-2026-01`

The identifier represents a vendor signing-key generation and rotation epoch.

It does not identify:

- a customer;
- an Organization;
- a Deployment;
- a Commercial Edition;
- a Commercial Purpose;
- a License;
- a product module.


## 3. Cryptographic Contract

Production License signing uses:

- ECDSA;
- NIST P-256 / secp256r1;
- SHA-256;
- ASN.1 DER ECDSA signatures;
- Base64 signature encoding.

The production key must satisfy the same validation contract enforced by the
USOP License Authority implementation.


## 4. Private-Key Boundary

The production private signing key must never:

- be committed to Git;
- exist inside the USOP source repository;
- be included in a customer container or distribution;
- be included in a License artifact;
- be stored in the customer runtime database;
- be supplied through a customer API;
- be written to application logs;
- be transmitted to a Design Partner;
- be placed in runtime vendor-trust material.

The `.operator-secrets/` Git ignore rule is defense in depth only.

It is not an approved production private-key storage location.


## 5. Initial Operator Storage

For the first Design Partner phase, production License Authority material must
be stored outside the USOP source repository in an operator-controlled
location.

The initial Windows operator root is:

`C:\USOP-License-Authority\`

Private signing material must be stored beneath a restricted subdirectory that
is accessible only to the authorized License Authority operator account.

For the initial Windows filesystem-backed authority:

- inherited ACL permissions must be disabled on the private-key directory;
- ordinary Users and other non-authorized principals must not have access;
- the authorized License Authority operator account must have the permissions
  required to read and use the signing material;
- SYSTEM and Administrators may retain administrative control where required
  for operating-system recovery and administration;
- ACL state must be reviewed before the first production key is generated and
  after any recovery or migration of the signing authority;
- private signing material must never be made broadly readable merely to solve
  an operator tooling or permissions problem.

This filesystem-based arrangement is an initial operational mechanism, not a
permanent architectural dependency.

Future signing implementations may use an HSM, KMS, managed signing service,
or equivalent protected signer without changing the License artifact contract.


## 6. Public Verification Material

The public verification key derived from the production private key is not
secret.

The public key must be exported separately and provisioned into USOP through
the product-controlled vendor trust mechanism.

The public verification key may be committed as release-controlled USOP
application material.

A SHA-256 fingerprint of the DER-encoded public key must be calculated when a
production signing authority is created.

The signing-key identifier and public-key SHA-256 fingerprint must be recorded
together in the License Authority key inventory.

Before public verification material is committed into runtime vendor trust, its
fingerprint must be compared with the fingerprint recorded during the key
ceremony.

Customer configuration, License artifacts, API requests, environment
variables, and customer database state must never define or extend the vendor
trust root.


## 7. Backup and Recovery

At least one protected backup of production private signing material must exist
before the key is relied upon for commercial License issuance.

The backup must be logically or physically separate from the active working
copy.

A private-key backup must not be stored in:

- Git;
- the USOP source repository;
- customer infrastructure;
- a customer distribution package;
- ordinary email;
- an unprotected shared folder.

Backup protection must be sufficient to prevent unauthorized recovery of the
private signing key.

For the initial filesystem-backed authority, the backup must be encrypted at
rest independently of ordinary filesystem access to the active working copy.

The backup encryption secret must not be stored beside the encrypted backup.

A recovery test must be completed before the production key is relied upon for
commercial License issuance.

The recovery test must prove that:

- the private key can be recovered by an authorized operator;
- the recovered key retains the expected signing-key identifier;
- the recovered public key produces the expected SHA-256 fingerprint;
- a License signed using the recovered authority verifies using the
  release-controlled public verification key.

Recovery must preserve the original signing-key identifier.


## 8. License Authority Key Inventory

A production License Authority key inventory must be maintained outside the
private-key file itself.

For every production signing authority, the inventory must record at least:

- signing-key identifier;
- cryptographic algorithm and curve;
- public-key SHA-256 fingerprint;
- creation date;
- operational status;
- active, rotated, compromised, or retired state;
- location class of the active private-key authority;
- confirmation that a protected backup exists;
- date and result of the most recent recovery test.

The inventory must never contain private-key bytes or the backup encryption
secret.


## 9. Rotation

Every new production signing key receives a new signing-key identifier.

A rotated key must never silently reuse the identifier of a different private
key.

Old public verification keys may remain in product-controlled vendor trust
while legitimate unexpired Licenses signed by those keys remain supported.

New License issuance must use the currently active signing authority.


## 10. Suspected Compromise

If production private signing material is suspected to be exposed or
compromised:

1. stop issuing Licenses with the affected key;
2. preserve incident evidence;
3. create a new signing authority with a new identifier;
4. provision the new public verification key through controlled release;
5. reissue affected active Licenses as required;
6. determine whether the compromised public trust entry must be removed;
7. document the incident and resulting trust transition.

Removal of an old trusted public key intentionally invalidates License
verification for artifacts signed exclusively by that key.

That consequence must be treated as an explicit security decision.


## 11. Key Generation Gate

A real production private signing key must not be generated until:

- License issuance implementation is regression-tested;
- artifact interoperability is proven;
- product-controlled runtime trust provisioning is implemented;
- this key ceremony contract is reviewed and frozen;
- the intended operator storage location is prepared;
- the backup approach is prepared.

Development and regression tests continue to use ephemeral signing keys.


## 12. Production Key Material and Git

Only public verification material may cross the production signing-authority
boundary into the USOP repository.

Production private signing material must remain outside Git for its entire
lifecycle.

No test fixture may contain a copy of the production private key.


## 13. Evolution

The initial filesystem-backed signing process exists to support controlled
Design Partner issuance.

USOP must preserve the ability to evolve the private signer behind an
operator-controlled abstraction, including HSM, KMS, cloud-managed signing, or
equivalent mechanisms, without changing the customer License artifact or
customer runtime verification contract.
