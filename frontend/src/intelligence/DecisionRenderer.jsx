import {
  Alert,
  Box,
  Chip,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import DecisionCard from "./DecisionCard";
import DecisionMetric from "./DecisionMetric";

function riskChangeLabel(decision) {
  const original = decision?.risk?.original;
  const projected = decision?.risk?.projected;

  if (original === null || original === undefined) return "—";
  if (projected === null || projected === undefined) return `${original}`;

  return `${original} → ${projected}`;
}

function topFindings(findings = [], limit = 4) {
  return findings.slice(0, limit);
}

function severityColor(severity) {
  if (severity === "Critical") return "error";
  if (severity === "High") return "warning";
  if (severity === "Medium") return "info";
  if (severity === "Low") return "success";
  return "default";
}

export default function DecisionRenderer({ decision }) {
  if (!decision?.available) {
    return (
      <DecisionCard
        title="Decision Intelligence"
        subtitle="Run a simulation to generate decision intelligence."
      >
        <Alert severity="info">
          No decision intelligence is available yet.
        </Alert>
      </DecisionCard>
    );
  }

  const findings = topFindings(decision.findings);

  return (
    <DecisionCard
      title="Decision Intelligence"
      subtitle="USOP-generated reasoning based on graph, simulation, and risk context."
    >
      <Stack spacing={2}>
        <Alert
          severity={decision.risk?.hasReduction ? "success" : "info"}
          sx={{ fontWeight: 700 }}
        >
          {decision.executiveSummary}
        </Alert>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              md: "1fr 1fr",
            },
            gap: 1.5,
          }}
        >
          <DecisionMetric
            label="Overall Risk"
            value={riskChangeLabel(decision)}
            helperText="Original risk compared to projected risk."
          />

          <DecisionMetric
            label="Risk Reduction"
            value={decision.risk?.reduction}
            helperText="Projected reduction after selected remediation."
            chipLabel={decision.risk?.hasReduction ? "Reduced" : "Review"}
            chipColor={decision.risk?.hasReduction ? "success" : "default"}
          />

          <DecisionMetric
            label="Attack Relationships Removed"
            value={decision.metrics?.removedAttackRelationships}
            helperText="Relationships removed from the projected graph."
          />

          <DecisionMetric
            label="Graph Changes"
            value={decision.metrics?.totalChanges}
            helperText="Total node and edge changes detected."
          />
        </Box>

        <Divider />

        <Stack spacing={1}>
          <Typography variant="subtitle2" fontWeight={800}>
            Recommended Next Action
          </Typography>

          <Typography variant="body2" color="text.secondary">
            {decision.recommendedNextStep}
          </Typography>
        </Stack>

        <Divider />

        <Stack spacing={1}>
          <Typography variant="subtitle2" fontWeight={800}>
            Key Findings
          </Typography>

          {findings.length ? (
            <Stack spacing={1}>
              {findings.map((finding, index) => (
                <Box
                  key={`${finding.type}-${index}`}
                  sx={{
                    p: 1.25,
                    borderRadius: 2,
                    border: "1px solid rgba(148, 163, 184, 0.16)",
                  }}
                >
                  <Stack spacing={0.75}>
                    <Stack
                      direction="row"
                      spacing={1}
                      sx={{
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <Typography variant="body2" fontWeight={800}>
                        {finding.title}
                      </Typography>

                      <Chip
                        label={finding.severity || "Info"}
                        color={severityColor(finding.severity)}
                        size="small"
                      />
                    </Stack>

                    <Typography variant="caption" color="text.secondary">
                      {finding.description}
                    </Typography>
                  </Stack>
                </Box>
              ))}
            </Stack>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No detailed findings were generated for this decision.
            </Typography>
          )}
        </Stack>
      </Stack>
    </DecisionCard>
  );
}