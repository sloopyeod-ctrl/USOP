import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Collapse,
  Stack,
  Typography,
} from "@mui/material";

import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import SyncIcon from "@mui/icons-material/Sync";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";

import {
  buildOperationalPulseIntelligence,
} from "../../intelligence/OperationalPulseIntelligenceService";


function formatTime(value) {
  if (!value) {
    return null;
  }

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? null
    : date.toLocaleTimeString();
}


function statusIcon(model) {
  if (model.status === "refreshing") {
    return (
      <CircularProgress
        size={18}
        color="info"
      />
    );
  }

  if (model.status === "failed") {
    return (
      <WarningAmberIcon
        color="error"
        fontSize="small"
      />
    );
  }

  return (
    <CheckCircleIcon
      color="success"
      fontSize="small"
    />
  );
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


export default function OperationalPulse({
  synchronization,
}) {
  const model =
    buildOperationalPulseIntelligence(
      synchronization,
    );

  if (!model) {
    return null;
  }

  const completedTime =
    formatTime(model.refresh.completed_at);

  const detailId =
    "operational-pulse-details";

  return (
    <Box
      sx={{
        mb: 2,
        px: 1.5,
        py: 1.1,
        borderRadius: 2,
        border:
          `1px solid ${borderColor(
            model.severity,
          )}`,
        backgroundColor:
          "rgba(8, 47, 73, 0.18)",
      }}
    >
      <Stack spacing={0.75}>
        <Stack
          direction={{
            xs: "column",
            md: "row",
          }}
          spacing={1}
          alignItems={{
            xs: "flex-start",
            md: "center",
          }}
          justifyContent="space-between"
        >
          <Stack
            direction="row"
            spacing={0.9}
            alignItems="center"
          >
            {statusIcon(model)}

            <Box>
              <Typography
                variant="subtitle2"
                fontWeight={900}
                sx={{
                  color: "#F8FAFC",
                  lineHeight: 1.15,
                }}
              >
                Operational Pulse
              </Typography>

              <Typography
                variant="caption"
                sx={{
                  color: "#E2E8F0",
                  fontWeight: 800,
                }}
              >
                {model.title}
              </Typography>
            </Box>
          </Stack>

          <Stack
            direction="row"
            spacing={0.75}
            flexWrap="wrap"
            useFlexGap
            alignItems="center"
          >
            {model.refresh.duration_ms !== null
              && model.status !== "refreshing"
              && (
                <Chip
                  label={
                    `${model.refresh.duration_ms} ms`
                  }
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
                  "& .MuiChip-icon": {
                    color: "inherit",
                  },
                }}
              />
            )}
          </Stack>
        </Stack>

        <Typography
          variant="caption"
          sx={{
            color: "#94A3B8",
            lineHeight: 1.3,
          }}
        >
          {model.summary}
        </Typography>

        <details
          open={
            model.status === "failed"
              ? true
              : undefined
          }
          style={{
            color: "#E2E8F0",
          }}
        >
          <summary
            aria-controls={detailId}
            style={{
              cursor: "pointer",
              listStyle: "none",
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
              fontSize: "0.75rem",
              fontWeight: 800,
              color: "#67E8F9",
              userSelect: "none",
            }}
          >
            <ExpandMoreIcon
              fontSize="small"
            />

            Synchronization Details
          </summary>

          <Box
            id={detailId}
            sx={{
              mt: 1,
            }}
          >
            <Stack spacing={1}>
              <Collapse
                in={model.messages.length > 0}
              >
                <Stack
                  direction="row"
                  spacing={0.75}
                  flexWrap="wrap"
                  useFlexGap
                >
                  {model.messages.map(
                    (message) => (
                      <Chip
                        key={message}
                        icon={
                          <CheckCircleIcon />
                        }
                        label={message}
                        size="small"
                        color="success"
                        variant="outlined"
                        sx={{
                          color: "#E2E8F0",
                          "& .MuiChip-icon": {
                            color: "inherit",
                          },
                        }}
                      />
                    ),
                  )}
                </Stack>
              </Collapse>

              {model.recommendation && (
                <Alert severity="info">
                  {model.recommendation}
                </Alert>
              )}

              {model.errors.map(
                (message) => (
                  <Alert
                    key={message}
                    severity="error"
                  >
                    {message}
                  </Alert>
                ),
              )}
            </Stack>
          </Box>
        </details>
      </Stack>
    </Box>
  );
}
