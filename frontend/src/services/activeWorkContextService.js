const ACTIVE_WORK_CONTEXT_STORAGE_KEY =
  "usop.activeWorkContext";


function normalizeRequiredText(
  value,
) {
  if (typeof value !== "string") {
    return null;
  }

  return value.trim() || null;
}


export function saveActiveWorkContext({
  organizationId,
  workItemId,
  identityId,
  sourceType = null,
}) {
  const normalizedOrganizationId =
    normalizeRequiredText(organizationId);
  const normalizedWorkItemId =
    normalizeRequiredText(workItemId);
  const normalizedIdentityId =
    normalizeRequiredText(identityId);

  if (
    !normalizedOrganizationId
    || !normalizedWorkItemId
    || !normalizedIdentityId
  ) {
    throw new Error(
      "Active work context requires "
      + "Organization, work item, and Identity.",
    );
  }

  const context = {
    organizationId:
      normalizedOrganizationId,
    workItemId:
      normalizedWorkItemId,
    identityId:
      normalizedIdentityId,
    sourceType:
      normalizeRequiredText(sourceType),
  };

  localStorage.setItem(
    ACTIVE_WORK_CONTEXT_STORAGE_KEY,
    JSON.stringify(context),
  );

  return context;
}


export function getActiveWorkContext() {
  const serialized = localStorage.getItem(
    ACTIVE_WORK_CONTEXT_STORAGE_KEY,
  );

  if (!serialized) {
    return null;
  }

  try {
    const parsed = JSON.parse(serialized);

    const organizationId =
      normalizeRequiredText(
        parsed?.organizationId,
      );
    const workItemId =
      normalizeRequiredText(
        parsed?.workItemId,
      );
    const identityId =
      normalizeRequiredText(
        parsed?.identityId,
      );

    if (
      !organizationId
      || !workItemId
      || !identityId
    ) {
      clearActiveWorkContext();
      return null;
    }

    return {
      organizationId,
      workItemId,
      identityId,
      sourceType:
        normalizeRequiredText(
          parsed?.sourceType,
        ),
    };
  } catch {
    clearActiveWorkContext();
    return null;
  }
}


export function getMatchingActiveWorkContext({
  organizationId,
  identityId,
}) {
  const context = getActiveWorkContext();

  if (!context) {
    return null;
  }

  if (
    context.organizationId
      !== organizationId
    || context.identityId
      !== identityId
  ) {
    return null;
  }

  return context;
}


export function clearActiveWorkContext() {
  localStorage.removeItem(
    ACTIVE_WORK_CONTEXT_STORAGE_KEY,
  );
}
