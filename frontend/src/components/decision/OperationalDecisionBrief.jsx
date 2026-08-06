import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";

import FactCheckIcon from
  "@mui/icons-material/FactCheck";
import SecurityIcon from
  "@mui/icons-material/Security";
import ScheduleIcon from
  "@mui/icons-material/Schedule";


function severityColor(value) {
  if (value === "Critical") {
    return "error";
  }

  if (value === "High") {
    return "warning";
  }

  if (
    value === "Moderate"
    || value === "Medium"
  ) {
    return "info";
  }

  if (value === "Low") {
    return "success";
  }

  return "default";
}


function confidenceColor(score) {
  if (score >= 80) {
    return "success";
  }

  if (score >= 50) {
    return "warning";
  }

  return "default";
}


function confidenceLabel(score) {
  if (score >= 80) {
    return "High";
  }

  if (score >= 50) {
    return "Moderate";
  }

  return "Developing";
}


function BriefField({
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
    <Box
      sx={{
        p: 1.75,
        borderRadius: 2,
        border:
          "1px solid rgba(148, 163, 184, 0.16)",
        backgroundColor:
          "rgba(15, 23, 42, 0.42)",
        minWidth: 0,
      }}
    >
      <Typography
        variant="caption"
        color="text.secondary"
        fontWeight={800}
        sx={{
          display: "block",
          textTransform: "uppercase",
          letterSpacing: 0.7,
          mb: 0.45,
        }}
      >
        {label}
      </Typography>

      <Typography
        variant="body2"
        fontWeight={800}
        sx={{
          color: "#E5E7EB",
          overflowWrap: "anywhere",
          whiteSpace: "pre-wrap",
        }}
      >
        {String(value)}
      </Typography>
    </Box>
  );
}


export default function OperationalDecisionBrief({
  recommendation,
  disposition,
  confidenceScore = null,
}) {
  const normalizedConfidence =
    Number.isFinite(Number(confidenceScore))
      ? Number(confidenceScore)
      : null;

  const technicalFields = [
    {
      label: "Evidence Type",
      value: recommendation.evidence_type,
    },
    {
      label: "Affected Role",
      value: recommendation.role_name,
    },
    {
      label: "Capability",
      value: recommendation.capability,
    },
    {
      label: "Scope",
      value:
        recommendation.scope_classification,
    },
    {
      label: "Assignment",
      value:
        recommendation.assignment_classification,
    },
    {
      label: "Estimated Effort",
      value: recommendation.estimated_effort,
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
    technicalFields.filter(
      (field) =>
        field.value !== null
        && field.value !== undefined
        && field.value !== "",
    );

  return (
    <Card
      sx={{
        border:
          "1px solid rgba(34, 211, 238, 0.34)",
        background:
          "linear-gradient("
          + "135deg, "
          + "rgba(17, 24, 39, 1) 0%, "
          + "rgba(8, 47, 73, 0.74) 100%"
          + ")",
      }}
    >
      <CardContent
        sx={{
          p: {
            xs: 2.5,
            md: 3,
          },
        }}
      >
        <Stack spacing={2.5}>
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
                sx={{
                  letterSpacing: 1.2,
                }}
              >
                Operational Decision Brief
              </Typography>

              <Typography
                variant="h5"
                fontWeight={900}
                sx={{
                  mt: 0.35,
                }}
              >
                {recommendation.title}
              </Typography>

              <Typography
                variant="body1"
                sx={{
                  mt: 1,
                  color: "#CBD5E1",
                  lineHeight: 1.7,
                  maxWidth: 860,
                }}
              >
                {recommendation.description}
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
                  disposition?.display_status
                  || "Open"
                }
                size="small"
                variant="outlined"
              />

              {normalizedConfidence !== null && (
                <Chip
                  icon={<FactCheckIcon />}
                  label={
                    `${confidenceLabel(
                      normalizedConfidence,
                    )} Confidence`
                  }
                  size="small"
                  color={confidenceColor(
                    normalizedConfidence,
                  )}
                />
              )}
            </Stack>
          </Stack>

          {normalizedConfidence !== null && (
            <Box>
              <Stack
                direction="row"
                justifyContent="space-between"
                sx={{
                  mb: 0.8,
                }}
              >
                <Typography
                  variant="body2"
                  color="text.secondary"
                  fontWeight={700}
                >
                  Operational confidence
                </Typography>

                <Typography fontWeight={900}>
                  {normalizedConfidence}%
                </Typography>
              </Stack>

              <LinearProgress
                variant="determinate"
                value={Math.min(
                  Math.max(
                    normalizedConfidence,
                    0,
                  ),
                  100,
                )}
                color={confidenceColor(
                  normalizedConfidence,
                )}
                sx={{
                  height: 9,
                  borderRadius: 10,
                }}
              />
            </Box>
          )}

          <Divider />

          <Stack spacing={1.25}>
            <Typography
              variant="h6"
              fontWeight={900}
            >
              Technical Context
            </Typography>

            {availableFields.length > 0 ? (
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: {
                    xs: "1fr",
                    sm: "1fr 1fr",
                    xl: "repeat(3, 1fr)",
                  },
                  gap: 1.25,
                }}
              >
                {availableFields.map(
                  (field) => (
                    <BriefField
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

          <Divider />

          <Stack
            direction={{
              xs: "column",
              sm: "row",
            }}
            spacing={1.5}
            alignItems={{
              xs: "flex-start",
              sm: "center",
            }}
          >
            <SecurityIcon color="primary" />

            <Box>
              <Typography
                variant="caption"
                color="text.secondary"
                fontWeight={800}
                sx={{
                  display: "block",
                  textTransform: "uppercase",
                  letterSpacing: 0.7,
                }}
              >
                Immediate Next Step
              </Typography>

              <Typography
                variant="body1"
                fontWeight={900}
              >
                {
                  recommendation.next_step
                  || recommendation.action
                  || (
                    "Review the evidence and record "
                    + "an accountable organizational "
                    + "decision."
                  )
                }
              </Typography>
            </Box>

            {recommendation.estimated_effort && (
              <Chip
                icon={<ScheduleIcon />}
                label={
                  recommendation.estimated_effort
                }
                size="small"
                variant="outlined"
                sx={{
                  ml: {
                    sm: "auto",
                  },
                }}
              />
            )}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
