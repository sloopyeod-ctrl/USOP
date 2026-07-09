function safeNumber(value) {
  if (typeof value === "number") return value;
  if (!value) return 0;

  const parsed = Number(value);
  return Number.isNaN(parsed) ? 0 : parsed;
}

function riskWeight(riskLevel) {
  if (riskLevel === "Critical") return 4;
  if (riskLevel === "High") return 3;
  if (riskLevel === "Medium") return 2;
  return 1;
}

function describeRemovedEdge(edge) {
  const contribution = safeNumber(edge.riskContribution);

  if (contribution >= 25) {
    return "A high-impact attack relationship was removed from the projected graph.";
  }

  if (contribution >= 10) {
    return "A meaningful attack relationship was removed from the projected graph.";
  }

  return "A low-impact attack relationship was removed from the projected graph.";
}

function describeChangedEdge(change) {
  const previous = safeNumber(change.previous?.riskContribution);
  const next = safeNumber(change.next?.riskContribution);

  if (next < previous) {
    return "An attack relationship remained, but its risk contribution was reduced.";
  }

  if (next > previous) {
    return "An attack relationship became more risky in the projected graph.";
  }

  return "An attack relationship changed in the projected graph.";
}

function describeChangedNode(change) {
  const previousRisk = change.previous?.riskLevel || "Low";
  const nextRisk = change.next?.riskLevel || "Low";

  if (riskWeight(nextRisk) < riskWeight(previousRisk)) {
    return "An identity graph object remained present, but its risk level was reduced.";
  }

  if (riskWeight(nextRisk) > riskWeight(previousRisk)) {
    return "An identity graph object became more risky in the projected graph.";
  }

  return "An identity graph object changed in the projected graph.";
}

export function buildGraphIntelligence(diff, simulationResult = null) {
  if (!diff) {
    return {
      available: false,
      executiveSummary: "No graph intelligence is available yet.",
      findings: [],
      metrics: {
        totalChanges: 0,
        removedAttackRelationships: 0,
        reducedRelationships: 0,
        increasedRelationships: 0,
        addedExposure: 0,
      },
      recommendedNextStep: "Run a simulation to generate graph intelligence.",
    };
  }

  const findings = [];

  const removedEdges = diff.edges?.removed || [];
  const addedEdges = diff.edges?.added || [];
  const changedEdges = diff.edges?.changed || [];
  const removedNodes = diff.nodes?.removed || [];
  const addedNodes = diff.nodes?.added || [];
  const changedNodes = diff.nodes?.changed || [];

  removedEdges.forEach((edge) => {
    findings.push({
      type: "removed_edge",
      severity: edge.riskLevel || "Low",
      title: "Attack relationship removed",
      description: describeRemovedEdge(edge),
      source: edge.source,
      target: edge.target,
      riskContribution: safeNumber(edge.riskContribution),
    });
  });

  addedEdges.forEach((edge) => {
    findings.push({
      type: "added_edge",
      severity: edge.riskLevel || "Low",
      title: "New attack relationship introduced",
      description:
        "A new relationship appeared in the projected graph and should be reviewed.",
      source: edge.source,
      target: edge.target,
      riskContribution: safeNumber(edge.riskContribution),
    });
  });

  changedEdges.forEach((change) => {
    const previousContribution = safeNumber(change.previous?.riskContribution);
    const nextContribution = safeNumber(change.next?.riskContribution);

    findings.push({
      type: "changed_edge",
      severity: change.next?.riskLevel || "Low",
      title:
        nextContribution < previousContribution
          ? "Attack relationship risk reduced"
          : "Attack relationship changed",
      description: describeChangedEdge(change),
      source: change.next?.source,
      target: change.next?.target,
      previousRiskContribution: previousContribution,
      nextRiskContribution: nextContribution,
      delta: nextContribution - previousContribution,
    });
  });

  removedNodes.forEach((node) => {
    findings.push({
      type: "removed_node",
      severity: node.riskLevel || "Low",
      title: "Graph object removed",
      description:
        "A graph object was removed from the projected attack path view.",
      nodeId: node.id,
      entityType: node.entityType,
    });
  });

  addedNodes.forEach((node) => {
    findings.push({
      type: "added_node",
      severity: node.riskLevel || "Low",
      title: "Graph object added",
      description:
        "A new graph object appeared in the projected attack path view.",
      nodeId: node.id,
      entityType: node.entityType,
    });
  });

  changedNodes.forEach((change) => {
    findings.push({
      type: "changed_node",
      severity: change.next?.riskLevel || "Low",
      title: "Graph object changed",
      description: describeChangedNode(change),
      nodeId: change.id,
      entityType: change.next?.entityType,
      previousRiskLevel: change.previous?.riskLevel,
      nextRiskLevel: change.next?.riskLevel,
    });
  });

  const reducedRelationships = changedEdges.filter(
    (change) =>
      safeNumber(change.next?.riskContribution) <
      safeNumber(change.previous?.riskContribution)
  ).length;

  const increasedRelationships = changedEdges.filter(
    (change) =>
      safeNumber(change.next?.riskContribution) >
      safeNumber(change.previous?.riskContribution)
  ).length;

  const addedExposure = addedEdges.length + addedNodes.length;

  const riskReduction = simulationResult?.risk_reduction ?? null;
  const originalRisk = simulationResult?.original_risk_score ?? null;
  const projectedRisk = simulationResult?.projected_risk_score ?? null;

  let executiveSummary = "Graph intelligence was generated for this simulation.";

  if (riskReduction !== null) {
    executiveSummary = `Simulation reduced projected risk by ${riskReduction} point(s).`;
  } else if (removedEdges.length || reducedRelationships) {
    executiveSummary =
      "Simulation reduced attack exposure by removing or weakening attack relationships.";
  } else if (addedExposure) {
    executiveSummary =
      "Simulation introduced new graph exposure that should be reviewed.";
  } else if (!diff.summary?.hasChanges) {
    executiveSummary =
      "Simulation completed, but no structural graph changes were detected.";
  }

  let recommendedNextStep = "Review remaining ranked paths and compare additional remediation options.";

  if (addedExposure > 0) {
    recommendedNextStep =
      "Review newly introduced graph exposure before approving this remediation plan.";
  } else if (removedEdges.length > 0 || reducedRelationships > 0) {
    recommendedNextStep =
      "Replay the projected path and validate whether remaining exposure still affects mission-critical access.";
  } else if (!diff.summary?.hasChanges) {
    recommendedNextStep =
      "Try a stronger remediation action or combine multiple actions for greater risk reduction.";
  }

  return {
    available: true,
    executiveSummary,
    findings,
    metrics: {
      totalChanges:
        diff.summary?.totalNodeChanges + diff.summary?.totalEdgeChanges || 0,
      removedAttackRelationships: removedEdges.length,
      reducedRelationships,
      increasedRelationships,
      addedExposure,
      removedObjects: removedNodes.length,
      addedObjects: addedNodes.length,
      changedObjects: changedNodes.length,
      originalRisk,
      projectedRisk,
      riskReduction,
    },
    recommendedNextStep,
  };
}