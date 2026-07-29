import api from "../api/usopApi";


function requireValue(
  value,
  fieldName,
) {
  if (
    value === null
    || value === undefined
    || value === ""
  ) {
    throw new Error(
      `${fieldName} is required.`,
    );
  }

  return value;
}


export async function createDecisionDraft({
  organizationId,
  identityId,
  recommendationId,
  decisionType,
  draftProfile = "default",
}) {
  requireValue(
    organizationId,
    "Organization",
  );

  requireValue(
    identityId,
    "Identity",
  );

  requireValue(
    recommendationId,
    "Recommendation",
  );

  requireValue(
    decisionType,
    "Decision type",
  );

  const response = await api.post(
    (
      "/api/v1/organizations/"
      + encodeURIComponent(
        organizationId,
      )
      + "/identities/"
      + encodeURIComponent(
        identityId,
      )
      + "/recommendations/"
      + encodeURIComponent(
        recommendationId,
      )
      + "/draft/"
    ),
    {
      decision_type: decisionType,
      draft_profile: draftProfile,
    },
  );

  return response.data;
}