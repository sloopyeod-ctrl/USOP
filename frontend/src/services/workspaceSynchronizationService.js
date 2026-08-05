import api from "../api/usopApi";

import {
  createWorkspaceSynchronizationResult,
  WORKSPACE_REFRESH_REASONS,
} from "../models/WorkspaceSynchronizationResult";

let synchronizationGeneration = 0;

function requireValue(value, fieldName) {
  if (value === null || value === undefined || value === "") {
    throw new Error(`${fieldName} is required.`);
  }
  return value;
}

function requireRefreshReason(reason) {
  const allowedReasons = new Set(Object.values(WORKSPACE_REFRESH_REASONS));
  if (!allowedReasons.has(reason)) {
    throw new Error(`Unknown workspace refresh reason: ${reason}`);
  }
  return reason;
}

export async function synchronizeWorkspace({ organizationId, identityId, reason }) {
  requireValue(organizationId, "Organization");
  requireValue(identityId, "Identity");
  requireRefreshReason(reason);

  const generation = ++synchronizationGeneration;
  const startedAt = new Date().toISOString();
  const intelligenceUrl = (
    "/api/v1/organizations/"
    + encodeURIComponent(organizationId)
    + "/identity-intelligence/"
    + encodeURIComponent(identityId)
  );

  const [intelligenceResponse, attackPathResponse] = await Promise.all([
    api.get(intelligenceUrl),
    api.get(`/attack-path/${encodeURIComponent(identityId)}`),
  ]);

  return createWorkspaceSynchronizationResult({
    generation,
    reason,
    organizationId,
    identityId,
    intelligence: intelligenceResponse.data,
    attackPath: attackPathResponse.data,
    startedAt,
    completedAt: new Date().toISOString(),
  });
}

export { WORKSPACE_REFRESH_REASONS };
