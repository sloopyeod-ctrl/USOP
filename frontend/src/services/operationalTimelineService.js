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


export async function getOperationalTimeline({
  organizationId,
  identityId = null,
  cursor = null,
  limit = 25,
  sortDirection = "descending",
}) {
  requireValue(
    organizationId,
    "Organization",
  );

  const params = {
    limit,
    sort_direction: sortDirection,
  };

  if (identityId) {
    params.identity_id = identityId;
  }

  if (cursor) {
    params.cursor = cursor;
  }

  const response = await api.get(
    (
      "/api/v1/organizations/"
      + encodeURIComponent(
        organizationId,
      )
      + "/operational-timeline/"
    ),
    {
      params,
    },
  );

  return response.data;
}
