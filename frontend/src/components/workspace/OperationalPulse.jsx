import { Box, Chip, CircularProgress, Stack, Typography } from "@mui/material";
import SyncIcon from "@mui/icons-material/Sync";

function formatTime(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toLocaleTimeString();
}

function reasonLabel(reason) {
  if (reason === "decision-recorded") return "Decision recorded";
  if (reason === "workspace-loaded") return "Workspace loaded";
  return "Workspace synchronized";
}

export default function OperationalPulse({ synchronization }) {
  if (!synchronization) return null;
  const { reason, completedAt, durationMs, status, isRefreshing, updatedProjections = [] } = synchronization;

  return (
    <Box sx={{ mb: 2, px: 1.75, py: 1.25, borderRadius: 2, border: "1px solid rgba(34, 211, 238, 0.24)", backgroundColor: "rgba(8, 47, 73, 0.18)" }}>
      <Stack direction={{ xs: "column", md: "row" }} spacing={1.25} alignItems={{ xs: "flex-start", md: "center" }} justifyContent="space-between">
        <Stack direction="row" spacing={1} alignItems="center">
          {isRefreshing ? <CircularProgress size={18} /> : <SyncIcon color={status === "failed" ? "error" : "primary"} />}
          <Box>
            <Typography variant="subtitle2" fontWeight={900}>Operational Pulse</Typography>
            <Typography variant="caption" color="text.secondary">
              {isRefreshing ? "Synchronizing operational state..." : reasonLabel(reason)}
            </Typography>
          </Box>
        </Stack>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {!isRefreshing && status === "succeeded" && (
            <Chip label={`${updatedProjections.length} projections updated`} size="small" color="success" variant="outlined" />
          )}
          {!isRefreshing && durationMs !== null && <Chip label={`${durationMs} ms`} size="small" variant="outlined" />}
          {!isRefreshing && formatTime(completedAt) && <Chip label={`Updated ${formatTime(completedAt)}`} size="small" variant="outlined" />}
          {status === "failed" && <Chip label="Synchronization failed" size="small" color="error" />}
        </Stack>
      </Stack>
    </Box>
  );
}
