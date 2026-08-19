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

export async function invitePlatformUser({
  organizationId,
  displayName,
  email,
  identityProvider,
  externalTenantId,
  externalSubjectId,
  identityIssuer = null,
}) {
  requireValue(organizationId, "Organization");

  const response = await api.post(
    "/api/v1/organizations/"
      + encodeURIComponent(organizationId)
      + "/platform-users/",
    {
      display_name: requireValue(displayName, "Display name"),
      email: requireValue(email, "Email"),
      identity_provider: requireValue(identityProvider, "Identity provider"),
      external_tenant_id: requireValue(externalTenantId, "External tenant ID"),
      external_subject_id: requireValue(externalSubjectId, "External subject ID"),
      identity_issuer: identityIssuer || null,
    },
  );

  return response.data ?? null;
}

async function mutatePlatformUserLifecycle({
  organizationId,
  platformUserId,
  action,
}) {
  requireValue(organizationId, "Organization");
  requireValue(platformUserId, "Platform User");
  requireValue(action, "Lifecycle action");

  const response = await api.post(
    "/api/v1/organizations/"
      + encodeURIComponent(organizationId)
      + "/platform-users/"
      + encodeURIComponent(platformUserId)
      + "/"
      + encodeURIComponent(action),
  );

  return response.data ?? null;
}

export function suspendPlatformUser(args) {
  return mutatePlatformUserLifecycle({
    ...args,
    action: "suspend",
  });
}

export function reactivatePlatformUser(args) {
  return mutatePlatformUserLifecycle({
    ...args,
    action: "reactivate",
  });
}

export function disablePlatformUser(args) {
  return mutatePlatformUserLifecycle({
    ...args,
    action: "disable",
  });
}


export async function listPlatformRoles({
  organizationId,
}) {
  requireValue(organizationId, "Organization");

  const response = await api.get(
    "/api/v1/organizations/"
      + encodeURIComponent(organizationId)
      + "/platform-roles/",
  );

  return Array.isArray(response.data)
    ? response.data
    : [];
}

export async function listPlatformUserRoleAssignments({
  organizationId,
  platformUserId,
}) {
  requireValue(organizationId, "Organization");
  requireValue(platformUserId, "Platform User");

  const response = await api.get(
    "/api/v1/organizations/"
      + encodeURIComponent(organizationId)
      + "/platform-users/"
      + encodeURIComponent(platformUserId)
      + "/roles",
  );

  return Array.isArray(response.data)
    ? response.data
    : [];
}

export async function assignPlatformUserRole({
  organizationId,
  platformUserId,
  platformRoleId,
  expiresAt = null,
}) {
  requireValue(organizationId, "Organization");
  requireValue(platformUserId, "Platform User");
  requireValue(platformRoleId, "Platform Role");

  const response = await api.post(
    "/api/v1/organizations/"
      + encodeURIComponent(organizationId)
      + "/platform-users/"
      + encodeURIComponent(platformUserId)
      + "/roles",
    {
      platform_role_id: platformRoleId,
      expires_at: expiresAt || null,
    },
  );

  return response.data ?? null;
}

export async function removePlatformUserRole({
  organizationId,
  platformUserId,
  platformRoleId,
}) {
  requireValue(organizationId, "Organization");
  requireValue(platformUserId, "Platform User");
  requireValue(platformRoleId, "Platform Role");

  await api.delete(
    "/api/v1/organizations/"
      + encodeURIComponent(organizationId)
      + "/platform-users/"
      + encodeURIComponent(platformUserId)
      + "/roles/"
      + encodeURIComponent(platformRoleId),
  );
}
