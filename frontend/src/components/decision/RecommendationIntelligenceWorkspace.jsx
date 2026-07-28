import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import DecisionActionPanel from
  "./DecisionActionPanel";
import DecisionTimelinePanel from
  "./DecisionTimelinePanel";
import OrganizationGuidancePanel from
  "./OrganizationGuidancePanel";


function formatDateTime(value) {
  if (!value) {
    return null;
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return date.toLocaleString();
}


function dispositionColor(status) {
  if (
    status === "Accepted Permanently"
    || status === "Accepted Temporarily"
    || status === "False Positive"
  ) {
    return "success";
  }

  if (
    status === "Escalated"
    || status === "Deferred"
  ) {
    return "secondary";
  }

  if (status === "In Progress") {
    return "info";
  }

  if (status === "Review Due") {
    return "warning";
  }

  return "default";
}


function severityColor(value) {
  if (value === "Critical") {
    return "error";
  }

  if (value === "High") {
    return "warning";
  }

  if (
    value === "Medium"
    || value === "Moderate"
  ) {
    return "info";
  }

  if (value === "Low") {
    return "success";
  }

  return "default";
}


function IntelligenceField({
  label,
  value,
}) {
  if (
    value === null
    || value === undefined
    || value === ""
  ) {
    return null;
  }

  return (
    <Box>
      <Typography
        variant="caption"
        color="text.secondary"
        fontWeight={800}
        sx={{
          display: "block",
          textTransform: "uppercase",
          letterSpacing: 0.7,
          mb: 0.4,
        }}
      >
        {label}
      </Typography>

      <Typography
        variant="body2"
        sx={{
          color: "#E5E7EB",
          whiteSpace: "pre-wrap",
        }}
      >
        {String(value)}
      </Typography>
    </Box>
  );
}


function TechnicalContext({
  recommendation,
}) {
  const fields = [
    {
      label: "Evidence Type",
      value:
        recommendation.evidence_type,
    },
    {
      label: "Affected Role",
      value:
        recommendation.role_name,
    },
    {
      label: "Capability",
      value:
        recommendation.capability,
    },
    {
      label: "Scope",
      value:
        recommendation
          .scope_classification,
    },
    {
      label: "Assignment",
      value:
        recommendation
          .assignment_classification,
    },
    {
      label: "Estimated Effort",
      value:
        recommendation.estimated_effort,
    },
    {
      label: "Risk Reduction",
      value:
        recommendation.risk_reduction
          !== undefined
          ? recommendation.risk_reduction
          : null,
    },
  ];

  const availableFields =
    fields.filter(
      (field) =>
        field.value !== null
        && field.value !== undefined
        && field.value !== "",
    );

  return (
    <Stack spacing={1.5}>
      <Typography
        variant="h6"
        fontWeight={900}
      >
        Technical Context
      </Typography>

      {availableFields.length ? (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              sm: "1fr 1fr",
            },
            gap: 2,
          }}
        >
          {availableFields.map(
            (field) => (
              <IntelligenceField
                key={field.label}
                label={field.label}
                value={field.value}
              />
            ),
          )}
        </Box>
      ) : (
        <Typography
          variant="body2"
          color="text.secondary"
        >
          No additional technical context is
          currently projected for this
          recommendation.
        </Typography>
      )}
    </Stack>
  );
}


function CurrentDecision({
  disposition,
}) {
  const displayStatus =
    disposition?.display_status
    || "Open";

  const reviewDueAt =
    formatDateTime(
      disposition?.review_due_at,
    );

  const createdAt =
    formatDateTime(
      disposition?.created_at,
    );

  if (!disposition?.decision_id) {
    return (
      <Stack spacing={1.5}>
        <Typography
          variant="h6"
          fontWeight={900}
        >
          Current Organizational Decision
        </Typography>

        <Alert severity="info">
          No organizational decision has been
          recorded for this recommendation.
        </Alert>
      </Stack>
    );
  }

  return (
    <Stack spacing={2}>
      <Stack
        direction={{
          xs: "column",
          sm: "row",
        }}
        justifyContent="space-between"
        alignItems={{
          xs: "flex-start",
          sm: "center",
        }}
        spacing={1}
      >
        <Typography
          variant="h6"
          fontWeight={900}
        >
          Current Organizational Decision
        </Typography>

        <Chip
          label={displayStatus}
          color={dispositionColor(
            displayStatus,
          )}
          size="small"
        />
      </Stack>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "1fr 1fr",
          },
          gap: 2,
        }}
      >
        <IntelligenceField
          label="Decision Type"
          value={
            disposition.decision_type
          }
        />

        <IntelligenceField
          label="Recorded"
          value={createdAt}
        />

        <IntelligenceField
          label="Acceptance Type"
          value={
            disposition.acceptance_type
          }
        />

        <IntelligenceField
          label="Review Due"
          value={reviewDueAt}
        />

        <IntelligenceField
          label="Escalated To"
          value={
            disposition.escalated_to
          }
        />

        <IntelligenceField
          label="External Ticket"
          value={
            disposition
              .external_ticket_reference
          }
        />
      </Box>

      <IntelligenceField
        label="Justification"
        value={
          disposition.justification
        }
      />

      <IntelligenceField
        label="Analyst Notes"
        value={disposition.notes}
      />
    </Stack>
  );
}


export default function RecommendationIntelligenceWorkspace({
  organizationId,
  identityId,
  recommendation,
  onDecisionCreated = null,
}) {
  if (!recommendation) {
    return (
      <Alert severity="info">
        Select a recommendation to open its
        intelligence workspace.
      </Alert>
    );
  }

  const disposition =
    recommendation
      .organizational_disposition
    || {
      display_status: "Open",
      history_count: 0,
      history: [],
      is_actionable: true,
    };

  const history =
    disposition.history || [];

  return (
    <Stack spacing={3}>
      <Card
        sx={{
          border:
            "1px solid rgba(34, 211, 238, 0.30)",
        }}
      >
        <CardContent>
          <Stack spacing={2.5}>
            <Stack
              direction={{
                xs: "column",
                sm: "row",
              }}
              justifyContent="space-between"
              alignItems={{
                xs: "flex-start",
                sm: "center",
              }}
              spacing={1.5}
            >
              <Box>
                <Typography
                  variant="overline"
                  color="text.secondary"
                  fontWeight={800}
                >
                  Recommendation Intelligence
                </Typography>

                <Typography
                  variant="h5"
                  fontWeight={900}
                >
                  {recommendation.title}
                </Typography>
              </Box>

              <Stack
                direction="row"
                spacing={1}
                flexWrap="wrap"
                useFlexGap
              >
                <Chip
                  label={
                    recommendation
                      .recommendation_type
                    || "General"
                  }
                  size="small"
                  variant="outlined"
                />

                <Chip
                  label={
                    recommendation.severity
                    || "Unclassified"
                  }
                  size="small"
                  color={severityColor(
                    recommendation.severity,
                  )}
                />

                <Chip
                  label={
                    disposition.display_status
                  }
                  size="small"
                  color={dispositionColor(
                    disposition.display_status,
                  )}
                />
              </Stack>
            </Stack>

            <Divider />

            <Stack spacing={1}>
              <Typography
                variant="h6"
                fontWeight={900}
              >
                Recommendation
              </Typography>

              <Typography
                variant="body1"
                sx={{
                  color: "#CBD5E1",
                  lineHeight: 1.7,
                }}
              >
                {recommendation.description}
              </Typography>
            </Stack>

            <Divider />

            <TechnicalContext
              recommendation={
                recommendation
              }
            />

            <Divider />

            <CurrentDecision
              disposition={disposition}
            />

            <Divider />

            <Stack spacing={1.5}>
              <Stack
                direction={{
                  xs: "column",
                  sm: "row",
                }}
                justifyContent="space-between"
                alignItems={{
                  xs: "flex-start",
                  sm: "center",
                }}
                spacing={1}
              >
                <Typography
                  variant="h6"
                  fontWeight={900}
                >
                  Decision Timeline
                </Typography>

                <Chip
                  label={
                    `${history.length} event${
                      history.length === 1
                        ? ""
                        : "s"
                    }`
                  }
                  size="small"
                  variant="outlined"
                />
              </Stack>

              <DecisionTimelinePanel
                history={history}
              />
            </Stack>

            <Divider />

            <OrganizationGuidancePanel
              organizationId={organizationId}
              decisionRecordId={
                disposition.decision_id
              }
            />
          </Stack>
        </CardContent>
      </Card>

      <DecisionActionPanel
        key={
          recommendation.recommendation_id
        }
        organizationId={organizationId}
        identityId={identityId}
        recommendation={recommendation}
        onDecisionCreated={
          onDecisionCreated
        }
      />
    </Stack>
  );
}
