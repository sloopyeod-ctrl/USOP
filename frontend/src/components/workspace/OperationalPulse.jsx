import {
  Alert, Box, Chip, CircularProgress, Collapse, Stack, Typography,
} from "@mui/material";

import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import SyncIcon from "@mui/icons-material/Sync";

import {
  buildOperationalPulseIntelligence,
} from "../../intelligence/OperationalPulseIntelligenceService";

function formatTime(value) {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toLocaleTimeString();
}

function statusIcon(model) {
  if (model.status === "refreshing") {
    return <CircularProgress size={20} />;
  }

  if (model.status === "failed") {
    return <WarningAmberIcon color="error" />;
  }

  return <CheckCircleIcon color="success" />;
}

function borderColor(severity) {
  if (severity === "error") {
    return "rgba(239, 68, 68, 0.42)";
  }
  if (severity === "success") {
    return "rgba(34, 197, 94, 0.36)";
  }
  return "rgba(34, 211, 238, 0.28)";
}

export default function OperationalPulse({ synchronization }) {
  const model = buildOperationalPulseIntelligence(synchronization);

  if (!model) {
    return null;
  }

  const completedTime = formatTime(model.refresh.completed_at);

  return (
    <Box
      sx={{
        mb: 2,
        px: 1.75,
        py: 1.5,
        borderRadius: 2,
        border: `1px solid ${borderColor(model.severity)}`,
        backgroundColor: "rgba(8, 47, 73, 0.18)",
      }}
    >
      <Stack spacing={1.25}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={1.25}
          alignItems={{ xs: "flex-start", md: "center" }}
          justifyContent="space-between"
        >
          <Stack direction="row" spacing={1} alignItems="center">
            {statusIcon(model)}
            <Box>
              <Typography
                variant="subtitle2"
                fontWeight={900}
                sx={{ color: "#F8FAFC" }}
              >
                Operational Pulse
              </Typography>

              <Typography
                variant="body2"
                fontWeight={800}
                sx={{ color: "#E2E8F0" }}
              >
                {model.title}
              </Typography>

              <Typography
                variant="caption"
                sx={{ color: "#94A3B8" }}
              >
                {model.summary}
              </Typography>
            </Box>
          </Stack>

          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {model.refresh.duration_ms !== null
              && model.status !== "refreshing" && (
              <Chip
                label={`${model.refresh.duration_ms} ms`}
                size="small"
                variant="outlined"
                sx={{
                  color: "#E2E8F0",
                  borderColor:
                    "rgba(148, 163, 184, 0.45)",
                }}
              />
            )}

            {completedTime && (
              <Chip
                label={`Updated ${completedTime}`}
                size="small"
                variant="outlined"
                sx={{
                  color: "#E2E8F0",
                  borderColor:
                    "rgba(148, 163, 184, 0.45)",
                }}
              />
            )}

            {model.status === "refreshing" && (
              <Chip
                icon={<SyncIcon />}
                label="Synchronizing"
                size="small"
                color="info"
                variant="outlined"
                sx={{
                  color: "#E2E8F0",
                  borderColor:
                    "rgba(148, 163, 184, 0.45)",
                }}
              />
            )}
          </Stack>
        </Stack>

        <Collapse in={model.messages.length > 0}>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {model.messages.map((message) => (
              <Chip
                key={message}
                icon={<CheckCircleIcon />}
                label={message}
                size="small"
                color="success"
                variant="outlined"
                sx={{
                  color: "#E2E8F0",
                  borderColor:
                    "rgba(148, 163, 184, 0.45)",
                }}
              />
            ))}
          </Stack>
        </Collapse>

        {model.recommendation && (
          <Alert severity="info">{model.recommendation}</Alert>
        )}

        {model.errors.map((message) => (
          <Alert key={message} severity="error">
            {message}
          </Alert>
        ))}
      </Stack>
    </Box>
  );
}
