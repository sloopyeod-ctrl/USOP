import {
  Box,
  Chip,
  Stack,
  Typography,
} from "@mui/material";


function formatDateTime(value) {
  if (!value) {
    return "Not recorded";
  }

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? "Not recorded"
    : date.toLocaleString();
}


function decisionColor(status) {
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


function timelineAccent(status) {
  if (
    status === "Accepted Permanently"
    || status === "Accepted Temporarily"
    || status === "False Positive"
  ) {
    return "success.main";
  }

  if (
    status === "Escalated"
    || status === "Deferred"
  ) {
    return "secondary.main";
  }

  if (status === "In Progress") {
    return "info.main";
  }

  if (status === "Review Due") {
    return "warning.main";
  }

  return "text.secondary";
}


function DetailField({
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
          letterSpacing: 0.6,
          mb: 0.35,
        }}
      >
        {label}
      </Typography>

      <Typography
        variant="body2"
        sx={{
          whiteSpace: "pre-wrap",
          lineHeight: 1.6,
        }}
      >
        {value}
      </Typography>
    </Box>
  );
}


function DecisionTimelineEvent({
  decision,
  index,
  isLast,
}) {
  const displayStatus =
    decision.display_status
    || "Recorded";

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns:
          "28px minmax(0, 1fr)",
        columnGap: 1.5,
      }}
    >
      <Box
        sx={{
          position: "relative",
          display: "flex",
          justifyContent: "center",
        }}
      >
        <Box
          sx={{
            mt: 0.6,
            width: 12,
            height: 12,
            borderRadius: "50%",
            backgroundColor:
              timelineAccent(
                displayStatus,
              ),
            boxShadow:
              "0 0 0 4px rgba(15, 23, 42, 0.95)",
            zIndex: 1,
          }}
        />

        {!isLast && (
          <Box
            sx={{
              position: "absolute",
              top: 18,
              bottom: -24,
              width: 2,
              backgroundColor:
                "rgba(148, 163, 184, 0.28)",
            }}
          />
        )}
      </Box>

      <Box sx={{ pb: isLast ? 0 : 3 }}>
        <Stack spacing={1.5}>
          <Stack
            direction={{
              xs: "column",
              sm: "row",
            }}
            spacing={1}
            justifyContent="space-between"
            alignItems={{
              xs: "flex-start",
              sm: "center",
            }}
          >
            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              flexWrap="wrap"
              useFlexGap
            >
              <Chip
                label={displayStatus}
                color={decisionColor(
                  displayStatus,
                )}
                size="small"
              />

              {index === 0 && (
                <Chip
                  label="Current"
                  color="primary"
                  size="small"
                  variant="outlined"
                />
              )}
            </Stack>

            <Typography
              variant="caption"
              color="text.secondary"
            >
              {formatDateTime(
                decision.created_at,
              )}
            </Typography>
          </Stack>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "1fr",
                md: "1fr 1fr",
              },
              gap: 1.75,
            }}
          >
            <DetailField
              label="Decision Type"
              value={
                decision.decision_type
              }
            />

            <DetailField
              label="Acceptance Type"
              value={
                decision.acceptance_type
              }
            />

            <DetailField
              label="Review Due"
              value={
                decision.review_due_at
                  ? formatDateTime(
                    decision.review_due_at,
                  )
                  : null
              }
            />

            <DetailField
              label="Escalated To"
              value={
                decision.escalated_to
              }
            />

            <DetailField
              label="External Ticket"
              value={
                decision
                  .external_ticket_reference
              }
            />
          </Box>

          <DetailField
            label="Justification"
            value={
              decision.justification
            }
          />

          <DetailField
            label="Analyst Notes"
            value={decision.notes}
          />
        </Stack>
      </Box>
    </Box>
  );
}


export default function DecisionTimelinePanel({
  history = [],
  emptyMessage = (
    "No organizational decisions have "
    + "been recorded for this recommendation."
  ),
}) {
  if (!history.length) {
    return (
      <Typography color="text.secondary">
        {emptyMessage}
      </Typography>
    );
  }

  return (
    <Stack spacing={0}>
      {history.map(
        (decision, index) => (
          <DecisionTimelineEvent
            key={
              decision.decision_id
              || `${index}`
            }
            decision={decision}
            index={index}
            isLast={
              index === history.length - 1
            }
          />
        ),
      )}
    </Stack>
  );
}
