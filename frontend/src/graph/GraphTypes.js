export const GRAPH_ENTITY_TYPES = {
  IDENTITY: "identity",
  ACCOUNT: "account",
  GROUP: "group",
  ROLE: "role",
  OBJECT: "object",
};

export const GRAPH_RISK_LEVELS = {
  LOW: "Low",
  MEDIUM: "Medium",
  HIGH: "High",
  CRITICAL: "Critical",
};

export function displayNodeType(type) {
  if (type === GRAPH_ENTITY_TYPES.IDENTITY) return "Identity";
  if (type === GRAPH_ENTITY_TYPES.ACCOUNT) return "Account";
  if (type === GRAPH_ENTITY_TYPES.GROUP) return "Group";
  if (type === GRAPH_ENTITY_TYPES.ROLE) return "Role";
  return "Object";
}

export function riskColorHex(riskLevel) {
  if (riskLevel === GRAPH_RISK_LEVELS.CRITICAL) return "#EF4444";
  if (riskLevel === GRAPH_RISK_LEVELS.HIGH) return "#F97316";
  if (riskLevel === GRAPH_RISK_LEVELS.MEDIUM) return "#F59E0B";
  return "#22C55E";
}

export function riskChipColor(riskLevel) {
  if (riskLevel === GRAPH_RISK_LEVELS.CRITICAL) return "error";
  if (riskLevel === GRAPH_RISK_LEVELS.HIGH) return "warning";
  if (riskLevel === GRAPH_RISK_LEVELS.MEDIUM) return "info";
  return "success";
}