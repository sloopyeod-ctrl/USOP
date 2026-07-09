export function buildDecisionIntelligence({
  graphIntelligence = null,
  simulationResult = null,
  identityContext = null,
  missionContext = null,
  vulnerabilityContext = null,
  connectorContext = null,
} = {}) {
  const graphAvailable = Boolean(graphIntelligence?.available);

  const originalRisk =
    graphIntelligence?.metrics?.originalRisk ??
    simulationResult?.original_risk_score ??
    null;

  const projectedRisk =
    graphIntelligence?.metrics?.projectedRisk ??
    simulationResult?.projected_risk_score ??
    null;

  const riskReduction =
    graphIntelligence?.metrics?.riskReduction ??
    simulationResult?.risk_reduction ??
    null;

  return {
    available: graphAvailable || Boolean(simulationResult),

    executiveSummary:
      graphIntelligence?.executiveSummary ||
      "Decision intelligence is available after running a simulation.",

    risk: {
      original: originalRisk,
      projected: projectedRisk,
      reduction: riskReduction,
      hasReduction:
        typeof riskReduction === "number" ? riskReduction > 0 : false,
    },

    graph: graphIntelligence,

    identity: identityContext,

    mission: missionContext,

    vulnerabilities: vulnerabilityContext,

    connectors: connectorContext,

    findings: graphIntelligence?.findings || [],

    metrics: {
      totalChanges: graphIntelligence?.metrics?.totalChanges || 0,
      removedAttackRelationships:
        graphIntelligence?.metrics?.removedAttackRelationships || 0,
      reducedRelationships:
        graphIntelligence?.metrics?.reducedRelationships || 0,
      increasedRelationships:
        graphIntelligence?.metrics?.increasedRelationships || 0,
      addedExposure: graphIntelligence?.metrics?.addedExposure || 0,
      removedObjects: graphIntelligence?.metrics?.removedObjects || 0,
      addedObjects: graphIntelligence?.metrics?.addedObjects || 0,
      changedObjects: graphIntelligence?.metrics?.changedObjects || 0,
    },

    recommendedNextStep:
      graphIntelligence?.recommendedNextStep ||
      "Review ranked attack paths and select a remediation action.",

    sources: {
      graph: graphAvailable,
      simulation: Boolean(simulationResult),
      identity: Boolean(identityContext),
      mission: Boolean(missionContext),
      vulnerabilities: Boolean(vulnerabilityContext),
      connectors: Boolean(connectorContext),
    },
  };
}