import api from "../api/usopApi";


export async function listPendingDecisionWorkItems({
  organizationId,
  status = "Pending",
}) {
  const response = await api.get(
    (
      "/api/v1/organizations/"
      + encodeURIComponent(organizationId)
      + "/pending-decision-work-items/"
    ),
    {
      params: status
        ? { status }
        : undefined,
    },
  );

  return response.data;
}
