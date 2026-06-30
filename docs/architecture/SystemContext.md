# USOP System Context

Version: 0.1  
Status: Draft  
Author: Marvin G. Dewitt  

---

## Purpose

The System Context defines where USOP fits within an enterprise security environment.

USOP does not replace authoritative enterprise systems. Instead, it connects to them, normalizes operational data, identifies meaningful changes, builds relationships, creates workflows, preserves knowledge, and presents operational intelligence through Mission Control.

---

## System Context Summary

USOP sits between enterprise security tools and the people responsible for operating, securing, governing, and assessing the environment.

External systems remain authoritative.

USOP provides the operational intelligence layer above them.

---

## Primary Users

- Security Engineer
- Compliance Manager
- System Owner
- Executive
- Auditor

---

## External Systems

- Microsoft Entra ID
- GitHub Enterprise
- Docker
- Kubernetes
- Keeper
- NetBox
- Microsoft Sentinel
- Tenable
- SharePoint
- Azure
- AWS
- Zabbix
- Snowflake
- Ticketing Systems
- Future Connectors

---

## Context Diagram

```mermaid
flowchart TD
    Users[Users<br/>Security Engineer<br/>Compliance Manager<br/>System Owner<br/>Executive<br/>Auditor]

    USOP[USOP<br/>Security Operations Intelligence Platform]

    Entra[Microsoft Entra ID]
    GitHub[GitHub Enterprise]
    Docker[Docker / Kubernetes]
    Keeper[Keeper]
    NetBox[NetBox]
    Sentinel[Microsoft Sentinel]
    Tenable[Tenable]
    SharePoint[SharePoint]
    Cloud[Azure / AWS]
    Zabbix[Zabbix]
    Snowflake[Snowflake]
    Ticketing[Ticketing Systems]

    Users --> USOP

    USOP <--> Entra
    USOP <--> GitHub
    USOP <--> Docker
    USOP <--> Keeper
    USOP <--> NetBox
    USOP <--> Sentinel
    USOP <--> Tenable
    USOP <--> SharePoint
    USOP <--> Cloud
    USOP <--> Zabbix
    USOP <--> Snowflake
    USOP <--> Ticketing
