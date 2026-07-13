USOP Demonstration Scenario
Purpose

This document defines the standard demonstration of USOP Version 1.

The purpose of the demonstration is not to showcase features.

The purpose is to demonstrate how USOP returns engineering time while improving the quality and speed of security decisions.

Every Version 1 capability should strengthen this demonstration.

Audience

This demonstration is designed for:

Security Engineers
Security Architects
Security Managers
Security Directors
CISOs
Product Evaluators
Investors
Technical Partners

The demonstration should remain understandable regardless of technical depth.

Demonstration Goal

At the conclusion of the demonstration, the audience should understand one thing:

USOP transforms security information into security decisions.

Not:

"USOP has a nice dashboard."

Not:

"USOP synchronizes Microsoft Entra."

Those are implementation details.

The demonstration should communicate the product's purpose.

Demonstration Story

The demonstration follows the lifecycle of a security investigation.

Collect

↓

Correlate

↓

Understand

↓

Decide

↓

Document

Every capability should reinforce this workflow.

Scenario

A security engineer receives a request to review a privileged identity.

The engineer needs to answer:

Who is this identity?
What can they access?
Why do they have that access?
Should the organization be concerned?
What action should be taken?

Without USOP this investigation requires information from multiple security systems.

With USOP the investigation occurs from one decision workspace.

Demonstration Workflow
Step 1

Synchronize Microsoft Entra.

Demonstrate:

Live synchronization
Canonical normalization
Provider-neutral architecture

Purpose:

Show that information enters the platform automatically.

Step 2

Open Identity 360.

Select:

Geoff Dewitt

Purpose:

Demonstrate that an analyst begins with an identity rather than disconnected infrastructure.

Step 3

Identity Summary

Display:

Identity
Accounts
Authentication
Group Memberships
Directory Roles

Purpose:

Show that identity context has already been correlated.

The analyst does not manually gather information.

Step 4

Authorization Context

Display:

Groups

Roles

Authorization relationships

Assignment scope

Assignment type

Purpose:

Answer:

Why does this identity have access?

Step 5

Exposure

Display:

Exposure Score

Contributing factors

Privilege summary

Attack-path participation

Purpose:

Explain:

Why should the analyst care?

Not simply:

The score is 82.

Explain why.

Step 6

Recommendations

Display:

Recommended actions

Evidence

Priority

Reasoning

Purpose:

Answer:

What should I do next?

Step 7

Decision

The analyst records:

Accepted

Rejected

Deferred

Requires Investigation

Purpose:

Capture organizational knowledge.

Future analysts should benefit from previous work.

Step 8

Report

Generate a report containing:

Identity

Evidence

Risk

Decision

Recommendations

Purpose:

Reduce documentation effort.

The investigation is complete.

Demonstration Outcome

Without USOP

The analyst manually gathers information from multiple security products.

Investigation time:

Approximately 15–20 minutes.

With USOP

Information is already correlated.

The analyst spends time making a decision rather than gathering information.

Investigation time:

Target:

Less than 30 seconds.

Success Criteria

A successful demonstration causes the audience to understand that:

USOP does not replace security engineers.

USOP removes repetitive work so security engineers can focus on reducing risk.

Version 1 Demonstration Checklist

Before demonstrating Version 1:

Live synchronization works.
Identity Graph is operational.
Authorization Graph is operational.
Identity 360 is complete.
Recommendations are available.
Decision recording works.
Reporting works.

Every demonstration should use the same workflow.

Product Message

USOP does not exist to collect security information.

USOP exists to transform security information into defensible security decisions.

The Closing Question

Every Version 1 demonstration should end with a single question:

"How long would this investigation have taken without USOP?"

The answer demonstrates the value of the platform more effectively than any feature list.
