from typing import Any

from pydantic import BaseModel


class AttackPathNode(BaseModel):
    id: str
    type: str
    label: str
    risk_contribution: int
    risk_level: str
    criticality: int
    blast_radius: int
    recommendation_count: int
    details: dict[str, Any] | None = None


class AttackPathEdge(BaseModel):
    source: str
    target: str
    relationship: str
    risk_contribution: int
    risk_level: str


class AttackPathGraph(BaseModel):
    risk_score: int
    risk_level: str
    nodes: list[AttackPathNode]
    edges: list[AttackPathEdge]


class AttackPathRecommendation(BaseModel):
    priority: int
    severity: str
    title: str
    description: str
    risk_reduction: int
    estimated_effort: str


class AttackPathFinding(BaseModel):
    type: str
    weight: int
    account_id: str | None = None
    username: str | None = None
    group_id: str | None = None
    group_name: str | None = None
    role_id: str | None = None
    role_name: str | None = None
    policy_id: str | None = None
    policy_name: str | None = None
    severity: str | None = None


class CriticalPath(BaseModel):
    source: str
    target: str
    relationship: str
    risk_contribution: int
    risk_level: str


class BlastRadiusSummary(BaseModel):
    total_objects: int
    critical_objects: int
    high_risk_objects: int
    medium_risk_objects: int


class RankedAttackPathStep(BaseModel):
    order: int
    node_id: str
    node_type: str
    label: str
    risk_contribution: int
    risk_level: str


class RankedAttackPath(BaseModel):
    path_rank: int
    name: str
    likelihood: int
    difficulty: str
    estimated_time: str
    total_risk: int
    risk_level: str
    steps: list[RankedAttackPathStep]


class AttackPathSummary(BaseModel):
    total_nodes: int
    total_edges: int
    highest_risk_node: AttackPathNode | None = None
    top_remediation: AttackPathRecommendation | None = None
    blast_radius: BlastRadiusSummary
    critical_paths: list[CriticalPath]
    ranked_paths: list[RankedAttackPath]


class AttackPathIdentity(BaseModel):
    id: str
    display_name: str
    primary_email: str


class AttackPathResponse(BaseModel):
    identity: AttackPathIdentity
    attack_path: AttackPathGraph
    recommendations: list[AttackPathRecommendation]
    findings: list[AttackPathFinding]
    summary: AttackPathSummary