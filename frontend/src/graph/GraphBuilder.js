import { GRAPH_ENTITY_TYPES } from "./GraphTypes";

function layoutNodes(nodes) {
  const positions = {};

  const identity = nodes.find((node) => node.entityType === GRAPH_ENTITY_TYPES.IDENTITY);
  const accounts = nodes.filter((node) => node.entityType === GRAPH_ENTITY_TYPES.ACCOUNT);
  const groups = nodes.filter((node) => node.entityType === GRAPH_ENTITY_TYPES.GROUP);
  const roles = nodes.filter((node) => node.entityType === GRAPH_ENTITY_TYPES.ROLE);

  if (identity) positions[identity.id] = { x: 420, y: 20 };

  accounts.forEach((node, index) => {
    positions[node.id] = { x: index * 250, y: 210 };
  });

  groups.forEach((node, index) => {
    positions[node.id] = { x: 420 + index * 290, y: 420 };
  });

  roles.forEach((node, index) => {
    positions[node.id] = { x: 275 + index * 290, y: 620 };
  });

  return positions;
}

export function buildUsopGraph(attackPath) {
  const rawNodes = attackPath?.attack_path?.nodes || [];
  const rawEdges = attackPath?.attack_path?.edges || [];

  const nodes = rawNodes.map((node) => ({
    id: node.id,
    entityType: node.type || GRAPH_ENTITY_TYPES.OBJECT,
    details: node.details || {},
    riskLevel: node.risk_level || null,
    original: node,
    position: { x: 420, y: 820 },
    state: {
      selected: false,
      connected: true,
      replayActive: false,
      added: false,
      removed: false,
      changed: false,
    },
  }));

  const positions = layoutNodes(nodes);

  const modeledNodes = nodes.map((node) => ({
    ...node,
    position: positions[node.id] || node.position,
  }));

  const edges = rawEdges.map((edge, index) => ({
    id: `${edge.source}-${edge.target}-${index}`,
    replayId: `${edge.source}-${edge.target}`,
    source: edge.source,
    target: edge.target,
    riskLevel: edge.risk_level || "Low",
    riskContribution: edge.risk_contribution || 0,
    relationship: edge.relationship || edge.edge_type || "related",
    original: edge,
    state: {
      connected: true,
      replayActive: false,
      added: false,
      removed: false,
      changed: false,
    },
  }));

  return {
    id: attackPath?.identity?.id || "unknown-graph",
    identity: attackPath?.identity || null,
    riskLevel: attackPath?.attack_path?.risk_level || "Low",
    summary: attackPath?.summary || null,
    nodes: modeledNodes,
    edges,
    source: attackPath,
  };
}