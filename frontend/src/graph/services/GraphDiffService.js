function normalizeRiskLevel(riskLevel) {
  return riskLevel || "Low";
}

function normalizeNumber(value) {
  if (typeof value === "number") return value;
  if (!value) return 0;

  const parsed = Number(value);
  return Number.isNaN(parsed) ? 0 : parsed;
}

function hasPositionChanged(previousPosition, nextPosition) {
  if (!previousPosition || !nextPosition) return false;

  return (
    previousPosition.x !== nextPosition.x ||
    previousPosition.y !== nextPosition.y
  );
}

function hasNodeChanged(previousNode, nextNode) {
  if (!previousNode || !nextNode) return false;

  return (
    previousNode.entityType !== nextNode.entityType ||
    normalizeRiskLevel(previousNode.riskLevel) !==
      normalizeRiskLevel(nextNode.riskLevel) ||
    hasPositionChanged(previousNode.position, nextNode.position)
  );
}

function hasEdgeChanged(previousEdge, nextEdge) {
  if (!previousEdge || !nextEdge) return false;

  return (
    previousEdge.source !== nextEdge.source ||
    previousEdge.target !== nextEdge.target ||
    normalizeRiskLevel(previousEdge.riskLevel) !==
      normalizeRiskLevel(nextEdge.riskLevel) ||
    normalizeNumber(previousEdge.riskContribution) !==
      normalizeNumber(nextEdge.riskContribution) ||
    previousEdge.relationship !== nextEdge.relationship
  );
}

function indexById(items = []) {
  return new Map(items.map((item) => [item.id, item]));
}

export function diffGraphs(previousGraph, nextGraph) {
  const previousNodes = indexById(previousGraph?.nodes || []);
  const nextNodes = indexById(nextGraph?.nodes || []);

  const previousEdges = indexById(previousGraph?.edges || []);
  const nextEdges = indexById(nextGraph?.edges || []);

  const addedNodes = [];
  const removedNodes = [];
  const changedNodes = [];
  const unchangedNodes = [];

  const addedEdges = [];
  const removedEdges = [];
  const changedEdges = [];
  const unchangedEdges = [];

  nextNodes.forEach((nextNode, nodeId) => {
    const previousNode = previousNodes.get(nodeId);

    if (!previousNode) {
      addedNodes.push(nextNode);
      return;
    }

    if (hasNodeChanged(previousNode, nextNode)) {
      changedNodes.push({
        id: nodeId,
        previous: previousNode,
        next: nextNode,
      });
      return;
    }

    unchangedNodes.push(nextNode);
  });

  previousNodes.forEach((previousNode, nodeId) => {
    if (!nextNodes.has(nodeId)) {
      removedNodes.push(previousNode);
    }
  });

  nextEdges.forEach((nextEdge, edgeId) => {
    const previousEdge = previousEdges.get(edgeId);

    if (!previousEdge) {
      addedEdges.push(nextEdge);
      return;
    }

    if (hasEdgeChanged(previousEdge, nextEdge)) {
      changedEdges.push({
        id: edgeId,
        previous: previousEdge,
        next: nextEdge,
      });
      return;
    }

    unchangedEdges.push(nextEdge);
  });

  previousEdges.forEach((previousEdge, edgeId) => {
    if (!nextEdges.has(edgeId)) {
      removedEdges.push(previousEdge);
    }
  });

  return {
    previousGraphId: previousGraph?.id || null,
    nextGraphId: nextGraph?.id || null,

    nodes: {
      added: addedNodes,
      removed: removedNodes,
      changed: changedNodes,
      unchanged: unchangedNodes,
    },

    edges: {
      added: addedEdges,
      removed: removedEdges,
      changed: changedEdges,
      unchanged: unchangedEdges,
    },

    summary: {
      addedNodeCount: addedNodes.length,
      removedNodeCount: removedNodes.length,
      changedNodeCount: changedNodes.length,
      unchangedNodeCount: unchangedNodes.length,

      addedEdgeCount: addedEdges.length,
      removedEdgeCount: removedEdges.length,
      changedEdgeCount: changedEdges.length,
      unchangedEdgeCount: unchangedEdges.length,

      totalNodeChanges:
        addedNodes.length + removedNodes.length + changedNodes.length,

      totalEdgeChanges:
        addedEdges.length + removedEdges.length + changedEdges.length,

      hasChanges:
        addedNodes.length > 0 ||
        removedNodes.length > 0 ||
        changedNodes.length > 0 ||
        addedEdges.length > 0 ||
        removedEdges.length > 0 ||
        changedEdges.length > 0,
    },
  };
}

export function summarizeGraphDiff(diff) {
  if (!diff) {
    return {
      title: "No graph comparison available",
      description: "No baseline or projected graph was available to compare.",
      severity: "info",
    };
  }

  if (!diff.summary.hasChanges) {
    return {
      title: "No graph changes detected",
      description:
        "The projected graph matches the current baseline graph structure.",
      severity: "success",
    };
  }

  const parts = [];

  if (diff.summary.addedNodeCount) {
    parts.push(`${diff.summary.addedNodeCount} node(s) added`);
  }

  if (diff.summary.removedNodeCount) {
    parts.push(`${diff.summary.removedNodeCount} node(s) removed`);
  }

  if (diff.summary.changedNodeCount) {
    parts.push(`${diff.summary.changedNodeCount} node(s) changed`);
  }

  if (diff.summary.addedEdgeCount) {
    parts.push(`${diff.summary.addedEdgeCount} edge(s) added`);
  }

  if (diff.summary.removedEdgeCount) {
    parts.push(`${diff.summary.removedEdgeCount} edge(s) removed`);
  }

  if (diff.summary.changedEdgeCount) {
    parts.push(`${diff.summary.changedEdgeCount} edge(s) changed`);
  }

  return {
    title: "Graph changes detected",
    description: parts.join(", "),
    severity: "warning",
  };
}