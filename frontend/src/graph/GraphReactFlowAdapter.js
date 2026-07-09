import { displayNodeType, riskColorHex } from "./GraphTypes";

function getConnectedIds(edges, selectedNodeId) {
  if (!selectedNodeId) return new Set();

  const connected = new Set([selectedNodeId]);

  edges.forEach((edge) => {
    if (edge.source === selectedNodeId) connected.add(edge.target);
    if (edge.target === selectedNodeId) connected.add(edge.source);
  });

  return connected;
}

export function buildReactFlowNodes(usopGraph, selectedNode, activeNodes) {
  const selectedId = selectedNode?.id;
  const replayActiveSet = new Set(activeNodes || []);

  const connectedIds = selectedId
    ? getConnectedIds(usopGraph.edges, selectedId)
    : new Set(usopGraph.nodes.map((node) => node.id));

  return usopGraph.nodes.map((node) => {
    const isSelected = node.id === selectedId;
    const isConnected = !selectedId || connectedIds.has(node.id);
    const isReplayActive = replayActiveSet.has(node.id);

    return {
      id: node.id,
      type: "attackPathNode",
      position: node.position,
      data: {
        details: node.details,
        nodeType: displayNodeType(node.entityType),
        attackPathNode: node.original,
        graphNode: node,
        isSelected,
        isConnected,
        isReplayActive,
      },
    };
  });
}

export function buildReactFlowEdges(usopGraph, selectedNode, activeEdges) {
  const selectedId = selectedNode?.id;
  const replayEdgeSet = new Set(activeEdges || []);

  return usopGraph.edges.map((edge) => {
    const isReplayActive = replayEdgeSet.has(edge.replayId);

    const isConnected =
      !selectedId || edge.source === selectedId || edge.target === selectedId;

    const color = isReplayActive
      ? "#22D3EE"
      : isConnected
        ? riskColorHex(edge.riskLevel)
        : "#64748B";

    return {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      animated: isReplayActive || (isConnected && edge.riskLevel !== "Low"),
      label: `+${edge.riskContribution}`,
      data: edge.original,
      style: {
        stroke: color,
        strokeWidth: isReplayActive ? 5 : isConnected ? 4 : 1.5,
        opacity: isReplayActive || isConnected ? 1 : 0.2,
      },
      labelStyle: {
        fill: color,
        fontWeight: 900,
        fontSize: 12,
      },
      labelBgStyle: {
        fill: "#111827",
        fillOpacity: 0.95,
      },
      labelBgPadding: [6, 4],
      labelBgBorderRadius: 6,
    };
  });
}