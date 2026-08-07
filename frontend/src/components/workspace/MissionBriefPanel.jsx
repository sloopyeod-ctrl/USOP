import {
  Box,
  Card,
  CardContent,
  Chip,
  Stack,
  Typography,
} from "@mui/material";

import FlagIcon from "@mui/icons-material/Flag";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import SyncIcon from "@mui/icons-material/Sync";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";


function priorityColor(priority) {
  if (priority === "Critical") {
    return "error";
  }

  if (priority === "High") {
    return "warning";
  }

  if (
    priority === "Medium"
    || priority === "Moderate"
  ) {
    return "info";
  }

  if (priority === "Low") {
    return "success";
  }

  return "default";
}


function workspacePresentation(status) {
  if (status === "Ready") {
    return {
      color: "success",
      icon: <CheckCircleIcon />,
    };
  }

  if (status === "Synchronizing") {
    return {
      color: "info",
      icon: <SyncIcon />,
    };
  }

  if (status === "Needs Attention") {
    return {
      color: "warning",
      icon: <WarningAmberIcon />,
    };
  }

  return {
    color: "default",
    icon: null,
  };
}


function BriefField({
  label,
  value,
  emphasize = false,
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
        sx={{
          display: "block",
          color: "#94A3B8",
          fontWeight: 900,
          textTransform: "uppercase",
          letterSpacing: 0.75,
          mb: 0.45,
        }}
      >
        {label}
      </Typography>

      <Typography
        variant={emphasize ? "h6" : "body1"}
        sx={{
          color: "#F8FAFC",
          fontWeight: emphasize ? 900 : 700,
          lineHeight: 1.45,
        }}
      >
        {value}
      </Typography>
    </Box>
  );
}


function formatConfidence(value) {
  if (
    value === null
    || value === undefined
  ) {
    return null;
  }

  return `${value}%`;
}


function formatExpectedImpact(value) {
  if (
    value === null
    || value === undefined
  ) {
    return null;
  }

  return `${value} risk reduction`;
}


export default function MissionBriefPanel({
  missionBrief,
}) {
  if (!missionBrief) {
    return null;
  }

  const workspace =
    workspacePresentation(
      missionBrief.workspaceStatus,
    );

  return (
    <Card
      sx={{
        border:
          "1px solid rgba(34, 211, 238, 0.34)",
        background:
          "linear-gradient(135deg, "
          + "rgba(8, 47, 73, 0.88) 0%, "
          + "rgba(15, 23, 42, 0.96) 55%, "
          + "rgba(30, 41, 59, 0.96) 100%)",
        boxShadow:
          "0 18px 40px rgba(2, 6, 23, 0.22)",
      }}
    >
      <CardContent
        sx={{
          p: {
            xs: 2.25,
            md: 3,
          },
        }}
      >
        <Stack spacing={2.75}>
          <Stack
            direction={{
              xs: "column",
              md: "row",
            }}
            spacing={1.5}
            justifyContent="space-between"
            alignItems={{
              xs: "flex-start",
              md: "center",
            }}
          >
            <Stack
              direction="row"
              spacing={1.25}
              alignItems="center"
            >
              <FlagIcon
                sx={{
                  color: "#22D3EE",
                }}
              />

              <Box>
                <Typography
                  variant="overline"
                  sx={{
                    color: "#67E8F9",
                    fontWeight: 900,
                    letterSpacing: 1.1,
                  }}
                >
                  Mission Brief
                </Typography>

                <Typography
                  variant="h5"
                  sx={{
                    color: "#F8FAFC",
                    fontWeight: 900,
                  }}
                >
                  {missionBrief.identityName}
                </Typography>
              </Box>
            </Stack>

            <Stack
              direction="row"
              spacing={1}
              flexWrap="wrap"
              useFlexGap
            >
              <Chip
                label={
                  missionBrief.priority
                }
                size="small"
                color={priorityColor(
                  missionBrief.priority,
                )}
                sx={{
                  fontWeight: 900,
                }}
              />

              <Chip
                icon={workspace.icon}
                label={
                  missionBrief.workspaceStatus
                }
                size="small"
                color={workspace.color}
                variant="outlined"
                sx={{
                  color: "#E2E8F0",
                  fontWeight: 800,
                  borderColor:
                    "rgba(148, 163, 184, 0.45)",
                  "& .MuiChip-icon": {
                    color: "inherit",
                  },
                }}
              />
            </Stack>
          </Stack>

          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              backgroundColor:
                "rgba(15, 23, 42, 0.58)",
              border:
                "1px solid rgba(148, 163, 184, 0.16)",
            }}
          >
            <BriefField
              label="Mission"
              value={missionBrief.mission}
              emphasize
            />
          </Box>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "1fr",
                md: "repeat(2, minmax(0, 1fr))",
                xl: "repeat(4, minmax(0, 1fr))",
              },
              gap: 2.25,
            }}
          >
            <BriefField
              label="Primary Objective"
              value={
                missionBrief.primaryObjective
              }
              emphasize
            />

            <BriefField
              label="Estimated Effort"
              value={
                missionBrief.estimatedEffort
              }
            />

            <BriefField
              label="Operational Confidence"
              value={formatConfidence(
                missionBrief
                  .operationalConfidence,
              )}
            />

            <BriefField
              label="Expected Impact"
              value={formatExpectedImpact(
                missionBrief.expectedImpact,
              )}
            />
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}
