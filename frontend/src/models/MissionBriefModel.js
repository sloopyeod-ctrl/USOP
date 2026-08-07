const WORKSPACE_STATUS = Object.freeze({
  idle: "Preparing",
  refreshing: "Synchronizing",
  succeeded: "Ready",
  failed: "Needs Attention",
});


function textOrNull(value) {
  if (typeof value !== "string") {
    return null;
  }

  const normalized = value.trim();

  return normalized || null;
}


function finiteNumberOrNull(value) {
  if (
    value === null
    || value === undefined
    || value === ""
  ) {
    return null;
  }

  const number = Number(value);

  return Number.isFinite(number)
    ? number
    : null;
}


function resolveIdentityName(identity) {
  return (
    textOrNull(identity?.display_name)
    || textOrNull(identity?.name)
    || textOrNull(identity?.user_principal_name)
    || textOrNull(identity?.id)
    || "Unknown identity"
  );
}


function resolvePriority({
  selectedRecommendation,
  decision,
  exposure,
}) {
  return (
    textOrNull(selectedRecommendation?.severity)
    || textOrNull(decision?.priority)
    || textOrNull(exposure?.rating)
    || "Unclassified"
  );
}


function resolveWorkspaceStatus(
  synchronization,
) {
  const status =
    textOrNull(synchronization?.status)
    || "idle";

  return WORKSPACE_STATUS[status]
    || "Preparing";
}


export function buildMissionBrief({
  identity,
  exposure,
  decision,
  selectedRecommendation,
  synchronization,
}) {
  const confidence = finiteNumberOrNull(
    decision?.confidence?.score,
  );

  const expectedImpact = finiteNumberOrNull(
    selectedRecommendation?.risk_reduction,
  );

  const synchronizationStatus =
    textOrNull(synchronization?.status)
    || "idle";

  return Object.freeze({
    identityName: resolveIdentityName(identity),

    mission: (
      "Reduce this identity's operational risk "
      + "by resolving the highest-priority "
      + "recommendation."
    ),

    priority: resolvePriority({
      selectedRecommendation,
      decision,
      exposure,
    }),

    primaryObjective: (
      textOrNull(selectedRecommendation?.title)
      || textOrNull(decision?.next_step)
      || "Review the available evidence."
    ),

    estimatedEffort: (
      textOrNull(
        selectedRecommendation?.estimated_effort,
      )
      || textOrNull(decision?.estimated_effort)
      || null
    ),

    operationalConfidence: confidence,

    expectedImpact,

    workspaceReady:
      synchronizationStatus === "succeeded",

    workspaceStatus:
      resolveWorkspaceStatus(
        synchronization,
      ),
  });
}
