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


export async function listDecisionPatterns({
  organizationId,
  identityId,
  recommendationId,
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

  const response = await api.get(
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
      + "/patterns/"
    ),
  );

  return Array.isArray(response.data)
    ? response.data
    : [];
}
