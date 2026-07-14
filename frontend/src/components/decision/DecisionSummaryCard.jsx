import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";

import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import FactCheckIcon from "@mui/icons-material/FactCheck";
import ScheduleIcon from "@mui/icons-material/Schedule";
import SecurityIcon from "@mui/icons-material/Security";


function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";
  if (
    value === "Moderate" ||
    value === "Medium"
  ) {
    return "info";
  }

  if (value === "Low") return "success";

  return "default";
}


function SummaryMetric({
  icon,
  label,
  value,
  helper,
}) {
  return (
    <Box
      sx={{
        p: 2,
        borderRadius: 2,
        border:
          "1px solid rgba(148, 163, 184, 0.16)",
        backgroundColor:
          "rgba(15, 23, 42, 0.45)",
        minHeight: 118,
      }}
    >
      <Stack spacing={1}>
        <Stack
          direction="row"
          spacing={1}
          alignItems="center"
        >
          {icon}

          <Typography
            variant="caption"
            color="text.secondary"
            fontWeight={800}
            sx={{
              textTransform: "uppercase",
              letterSpacing: 0.8,
            }}
          >
            {label}
          </Typography>
        </Stack>

        <Typography
          variant="h6"
          fontWeight={900}
        >
          {value}
        </Typography>

        {helper && (
          <Typography
            variant="caption"
            color="text.secondary"
          >
            {helper}
          </Typography>
        )}
      </Stack>
    </Box>
  );
}


export default function DecisionSummaryCard({
  decision,
}) {
  if (!decision?.available) {
    return (
      <Alert severity="info">
        Decision intelligence is not available for
        this investigation.
      </Alert>
    );
  }

  const confidenceScore =
    decision.confidence?.score ?? 0;

  const authorization =
    decision.authorization ?? {};

  return (
    <Card
      sx={{
        border:
          decision.priority === "Critical"
            ? "1px solid rgba(239, 68, 68, 0.70)"
            : "1px solid rgba(34, 211, 238, 0.35)",
        background:
          decision.priority === "Critical"
            ? (
              "linear-gradient(" +
              "135deg, " +
              "rgba(17, 24, 39, 1) 0%, " +
              "rgba(50, 17, 20, 0.96) 100%" +
              ")"
            )
            : (
              "linear-gradient(" +
              "135deg, " +
              "rgba(17, 24, 39, 1) 0%, " +
              "rgba(8, 47, 73, 0.74) 100%" +
              ")"
            ),
      }}
    >
      <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
        <Stack spacing={3}>
          <Stack
            direction={{
              xs: "column",
              md: "row",
            }}
            justifyContent="space-between"
            alignItems={{
              xs: "flex-start",
              md: "center",
            }}
            spacing={2}
          >
            <Box>
              <Typography
                variant="overline"
                color="primary.main"
                fontWeight={900}
                sx={{ letterSpacing: 1.4 }}
              >
                Decision Intelligence
              </Typography>

              <Typography
                variant="h4"
                fontWeight={900}
                sx={{ mt: 0.5 }}
              >
                {decision.summary?.title}
              </Typography>

              <Typography
                color="text.secondary"
                sx={{
                  mt: 1,
                  maxWidth: 820,
                }}
              >
                {decision.summary?.description}
              </Typography>
            </Box>

            <Stack
              direction="row"
              spacing={1}
              flexWrap="wrap"
              useFlexGap
            >
              <Chip
                icon={<SecurityIcon />}
                label={`${decision.priority} Priority`}
                color={severityColor(
                  decision.priority,
                )}
                sx={{
                  fontWeight: 900,
                  textTransform: "uppercase",
                }}
              />

              <Chip
                icon={<FactCheckIcon />}
                label={`${confidenceScore}% Evidence Confidence`}
                color={
                  confidenceScore >= 80
                    ? "success"
                    : confidenceScore >= 50
                      ? "warning"
                      : "default"
                }
                variant="outlined"
                sx={{ fontWeight: 800 }}
              />
            </Stack>
          </Stack>

          <Box>
            <Stack
              direction="row"
              justifyContent="space-between"
              sx={{ mb: 1 }}
            >
              <Typography
                variant="body2"
                color="text.secondary"
                fontWeight={700}
              >
                Evidence completeness
              </Typography>

              <Typography fontWeight={900}>
                {confidenceScore}%
              </Typography>
            </Stack>

            <LinearProgress
              variant="determinate"
              value={Math.min(
                Math.max(confidenceScore, 0),
                100,
              )}
              color={
                confidenceScore >= 80
                  ? "success"
                  : confidenceScore >= 50
                    ? "warning"
                    : "error"
              }
              sx={{
                height: 10,
                borderRadius: 10,
              }}
            />
          </Box>

          <Divider />

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "1fr",
                sm: "1fr 1fr",
                xl: "2fr 1fr 1fr 1fr",
              },
              gap: 1.5,
            }}
          >
            <SummaryMetric
              icon={
                <AssignmentTurnedInIcon
                  color="primary"
                  fontSize="small"
                />
              }
              label="Recommended Next Action"
              value={
                decision.next_step ||
                "Review the available evidence."
              }
              helper={
                "Highest-priority deterministic action"
              }
            />

            <SummaryMetric
              icon={
                <ScheduleIcon
                  color="primary"
                  fontSize="small"
                />
              }
              label="Estimated Effort"
              value={
                decision.estimated_effort ||
                "Analyst review required"
              }
            />

            <SummaryMetric
              icon={
                <SecurityIcon
                  color="primary"
                  fontSize="small"
                />
              }
              label="High-Impact Roles"
              value={
                authorization
                  .privileged_role_count ?? 0
              }
              helper={
                `${authorization
                  .tenant_wide_assignment_count ?? 0} ` +
                "tenant-wide"
              }
            />

            <SummaryMetric
              icon={
                <FactCheckIcon
                  color="primary"
                  fontSize="small"
                />
              }
              label="Direct Assignments"
              value={
                authorization
                  .direct_assignment_count ?? 0
              }
              helper={
                `${authorization.role_count ?? 0} ` +
                "total role assignments"
              }
            />
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}
