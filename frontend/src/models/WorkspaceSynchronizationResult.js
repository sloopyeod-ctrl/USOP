export const WORKSPACE_REFRESH_REASONS = {
  WORKSPACE_LOADED: "workspace-loaded",
  DECISION_RECORDED: "decision-recorded",
};

export const WORKSPACE_PROJECTIONS = {
  IDENTITY_INTELLIGENCE: "identity-intelligence",
  ATTACK_PATH: "attack-path",
  GRAPH: "graph",
  RECOMMENDATIONS: "recommendations",
  RISK: "risk",
  MISSION_STATUS: "mission-status",
  OPERATIONAL_TIMELINE: "operational-timeline",
};

export function createWorkspaceSynchronizationResult({
  generation,
  reason,
  organizationId,
  identityId,
  intelligence,
  attackPath,
  startedAt,
  completedAt,
}) {
  const started = new Date(startedAt);
  const completed = new Date(completedAt);

  return Object.freeze({
    organization_id: organizationId,
    identity_id: identityId,
    intelligence,
    attack_path: attackPath,
    refresh: Object.freeze({
      generation,
      reason,
      started_at: startedAt,
      completed_at: completedAt,
      duration_ms: Math.max(0, completed.getTime() - started.getTime()),
      successful: true,
      partial: false,
      updated_projections: Object.freeze([
        WORKSPACE_PROJECTIONS.IDENTITY_INTELLIGENCE,
        WORKSPACE_PROJECTIONS.ATTACK_PATH,
        WORKSPACE_PROJECTIONS.GRAPH,
        WORKSPACE_PROJECTIONS.RECOMMENDATIONS,
        WORKSPACE_PROJECTIONS.RISK,
        WORKSPACE_PROJECTIONS.MISSION_STATUS,
        WORKSPACE_PROJECTIONS.OPERATIONAL_TIMELINE,
      ]),
    }),
  });
}
