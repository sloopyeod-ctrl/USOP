import {
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Stack,
  Typography,
} from "@mui/material";


function formatDateTime(value) {
  if (!value) return "Not recorded";
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
  ) return "success";
  if (status === "Escalated" || status === "Deferred") return "secondary";
  if (status === "In Progress") return "info";
  if (status === "Review Due") return "warning";
  return "default";
}


function DetailField({ label, value }) {
  if (!value) return null;
  return (
    <Box>
      <Typography
        variant="caption"
        color="text.secondary"
        fontWeight={800}
        sx={{ textTransform: "uppercase", letterSpacing: 0.6 }}
      >
        {label}
      </Typography>
      <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
        {value}
      </Typography>
    </Box>
  );
}


export default function RecommendationHistoryDialog({
  open,
  onClose,
  recommendation,
}) {
  const disposition = recommendation?.organizational_disposition;
  const history = disposition?.history || [];

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>
        <Stack spacing={0.75}>
          <Typography variant="h5" fontWeight={900}>
            Decision History
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {recommendation?.title}
          </Typography>
        </Stack>
      </DialogTitle>

      <DialogContent dividers>
        {history.length ? (
          <Stack spacing={2.5}>
            {history.map((decision, index) => (
              <Box key={decision.decision_id || `${index}`}>
                <Stack spacing={1.5}>
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    spacing={1}
                    justifyContent="space-between"
                    alignItems={{ xs: "flex-start", sm: "center" }}
                  >
                    <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                      <Chip
                        label={decision.display_status || "Recorded"}
                        color={decisionColor(decision.display_status)}
                        size="small"
                      />
                      {index === 0 && (
                        <Chip label="Current" color="primary" size="small" variant="outlined" />
                      )}
                    </Stack>
                    <Typography variant="caption" color="text.secondary">
                      {formatDateTime(decision.created_at)}
                    </Typography>
                  </Stack>

                  <DetailField label="Justification" value={decision.justification} />
                  <DetailField label="Analyst Notes" value={decision.notes} />
                  <DetailField label="Acceptance Type" value={decision.acceptance_type} />
                  <DetailField
                    label="Review Due"
                    value={decision.review_due_at ? formatDateTime(decision.review_due_at) : null}
                  />
                  <DetailField label="Escalated To" value={decision.escalated_to} />
                  <DetailField label="External Ticket" value={decision.external_ticket_reference} />
                </Stack>
                {index < history.length - 1 && <Divider sx={{ mt: 2.5 }} />}
              </Box>
            ))}
          </Stack>
        ) : (
          <Typography color="text.secondary">
            No organizational decisions have been recorded for this recommendation.
          </Typography>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}
