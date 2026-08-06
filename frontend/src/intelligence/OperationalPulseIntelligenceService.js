const PROJECTION_MESSAGES = {
  "identity-intelligence": "Identity intelligence refreshed",
  "attack-path": "Attack-path context recalculated",
  graph: "Relationship graph recalculated",
  recommendations: "Recommendations refreshed",
  risk: "Risk posture recalculated",
  "mission-status": "Mission status refreshed",
  "operational-timeline": "Operational history synchronized",
};

function reasonSummary(reason) {
  if (reason === "decision-recorded") {
    return {
      title: "Decision recorded",
      summary: (
        "The accountable decision was saved "
        + "and the operational workspace was refreshed."
      ),
      action: (
        "Review the updated recommendations, "
        + "risk posture, and operational history."
      ),
    };
  }

  if (reason === "workspace-loaded") {
    return {
      title: "Workspace ready",
      summary: (
        "Current operational context was loaded "
        + "for this identity."
      ),
      action: null,
    };
  }

  return {
    title: "Workspace synchronized",
    summary: "The current operational state was refreshed.",
    action: null,
  };
}

function projectionMessage(projection) {
  return PROJECTION_MESSAGES[projection] || `${projection} refreshed`;
}

export function buildOperationalPulseIntelligence(synchronization) {
  if (!synchronization) {
    return null;
  }

  const {
    reason, generation, startedAt, completedAt, durationMs,
    status, isRefreshing, error, updatedProjections = [],
  } = synchronization;

  const reasonContent = reasonSummary(reason);

  if (isRefreshing) {
    return Object.freeze({
      title: "Synchronizing workspace",
      summary: (
        "USOP is refreshing the operational "
        + "context for this identity."
      ),
      status: "refreshing",
      severity: "info",
      messages: Object.freeze([]),
      recommendation: null,
      warnings: Object.freeze([]),
      errors: Object.freeze([]),
      refresh: Object.freeze({
        generation,
        reason,
        started_at: startedAt,
        completed_at: completedAt,
        duration_ms: durationMs,
      }),
    });
  }

  if (status === "failed") {
    return Object.freeze({
      title: "Workspace synchronization failed",
      summary: (
        "The last accountable action may have completed, "
        + "but the workspace could not confirm the refreshed "
        + "operational state."
      ),
      status: "failed",
      severity: "error",
      messages: Object.freeze([]),
      recommendation: (
        "Retry the workspace refresh before making "
        + "another operational decision."
      ),
      warnings: Object.freeze([]),
      errors: Object.freeze([error || "Synchronization failed."]),
      refresh: Object.freeze({
        generation,
        reason,
        started_at: startedAt,
        completed_at: completedAt,
        duration_ms: durationMs,
      }),
    });
  }

  if (status !== "succeeded") {
    return null;
  }

  return Object.freeze({
    title: reasonContent.title,
    summary: reasonContent.summary,
    status: "succeeded",
    severity: "success",
    messages: Object.freeze(updatedProjections.map(projectionMessage)),
    recommendation: reasonContent.action,
    warnings: Object.freeze([]),
    errors: Object.freeze([]),
    refresh: Object.freeze({
      generation,
      reason,
      started_at: startedAt,
      completed_at: completedAt,
      duration_ms: durationMs,
    }),
  });
}
