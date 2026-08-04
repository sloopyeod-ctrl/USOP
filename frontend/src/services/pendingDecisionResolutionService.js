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


function normalizeOptionalText(value) {
  const normalizedValue =
    value?.trim?.() || "";

  return normalizedValue || null;
}


function normalizeReviewDate(value) {
  if (!value) {
    return null;
  }

  const reviewDate = new Date(value);

  if (
    Number.isNaN(
      reviewDate.getTime(),
    )
  ) {
    throw new Error(
      "Review date is invalid.",
    );
  }

  return reviewDate.toISOString();
}


export async function resolvePendingDecision({
  organizationId,
  workItemId,
  recommendationId,
  decisionType,
  justification = "",
  notes = "",
  acceptanceType = null,
  reviewDueAt = "",
  actionTaken = "",
  escalatedTo = "",
  externalTicketReference = "",
  actor = null,
}) {
  requireValue(
    organizationId,
    "Organization",
  );
  requireValue(
    workItemId,
    "Work item",
  );
  requireValue(
    recommendationId,
    "Recommendation",
  );
  requireValue(
    decisionType,
    "Decision type",
  );

  const payload = {
    decision_type: decisionType,
    justification:
      normalizeOptionalText(
        justification,
      ),
    notes:
      normalizeOptionalText(notes),
    acceptance_type:
      decisionType === "AcceptRisk"
        ? acceptanceType
        : null,
    review_due_at:
      decisionType === "AcceptRisk"
        ? normalizeReviewDate(
          reviewDueAt,
        )
        : null,
    action_taken:
      normalizeOptionalText(
        actionTaken,
      ),
    escalated_to:
      decisionType === "Escalate"
        ? normalizeOptionalText(
          escalatedTo,
        )
        : null,
    external_ticket_reference:
      normalizeOptionalText(
        externalTicketReference,
      ),
    actor:
      normalizeOptionalText(actor),
  };

  const response = await api.post(
    (
      "/api/v1/organizations/"
      + encodeURIComponent(
        organizationId,
      )
      + "/pending-decision-work-items/"
      + encodeURIComponent(workItemId)
      + "/recommendations/"
      + encodeURIComponent(
        recommendationId,
      )
      + "/decision"
    ),
    payload,
  );

  return response.data;
}
