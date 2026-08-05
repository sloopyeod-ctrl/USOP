import { useCallback, useRef, useState } from "react";

import { synchronizeWorkspace } from "../services/workspaceSynchronizationService";

const INITIAL_STATE = {
  generation: 0, reason: null, startedAt: null, completedAt: null,
  durationMs: null, status: "idle", isRefreshing: false, error: null,
  updatedProjections: [],
};

export default function useWorkspaceSynchronization() {
  const latestRequestedGenerationRef = useRef(0);
  const [synchronization, setSynchronization] = useState(INITIAL_STATE);

  const refresh = useCallback(async ({ organizationId, identityId, reason }) => {
    const requestedGeneration = latestRequestedGenerationRef.current + 1;
    latestRequestedGenerationRef.current = requestedGeneration;

    setSynchronization((current) => ({
      ...current, generation: requestedGeneration, reason,
      startedAt: new Date().toISOString(), completedAt: null, durationMs: null,
      status: "refreshing", isRefreshing: true, error: null, updatedProjections: [],
    }));

    try {
      const result = await synchronizeWorkspace({ organizationId, identityId, reason });
      if (requestedGeneration !== latestRequestedGenerationRef.current) return null;

      setSynchronization({
        generation: requestedGeneration, reason: result.refresh.reason,
        startedAt: result.refresh.started_at, completedAt: result.refresh.completed_at,
        durationMs: result.refresh.duration_ms, status: "succeeded",
        isRefreshing: false, error: null,
        updatedProjections: result.refresh.updated_projections,
      });
      return result;
    } catch (error) {
      if (requestedGeneration !== latestRequestedGenerationRef.current) return null;
      setSynchronization((current) => ({
        ...current, generation: requestedGeneration, reason,
        completedAt: new Date().toISOString(), status: "failed",
        isRefreshing: false,
        error: error?.response?.data?.detail || error?.message || "Unable to synchronize the workspace.",
        updatedProjections: [],
      }));
      throw error;
    }
  }, []);

  return { synchronization, refresh };
}
