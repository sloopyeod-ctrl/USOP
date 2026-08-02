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


export async function getPlatformHealth() {
  const response = await api.get(
    "/health",
  );

  return response.data ?? null;
}


export async function listRegisteredConnectors() {
  const response = await api.get(
    "/connectors/",
  );

  return Array.isArray(response.data)
    ? response.data
    : [];
}


export async function listProviderCatalog() {
  const response = await api.get(
    "/connectors/providers",
  );

  return Array.isArray(response.data)
    ? response.data
    : [];
}

export async function listConnectorHealth() {
  const response = await api.get(
    "/connectors/health",
  );

  return Array.isArray(response.data)
    ? response.data
    : [];
}

export async function listPlatformUsers({
  organizationId,
}) {
  requireValue(
    organizationId,
    "Organization",
  );

  const response = await api.get(
    (
      "/api/v1/organizations/"
      + encodeURIComponent(
        organizationId,
      )
      + "/platform-users/"
    ),
  );

  return Array.isArray(response.data)
    ? response.data
    : [];
}
