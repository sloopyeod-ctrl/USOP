import React from "react";
import { Box, Card, CardContent, Typography, LinearProgress } from "@mui/material";

function clamp(value, min = 0, max = 100) {
  return Math.max(min, Math.min(max, value || 0));
}

export default function AnimatedRiskMetrics({ metrics = {} }) {
  const riskScore = clamp(metrics.riskScore ?? metrics.overallRisk ?? 0);
  const exposureScore = clamp(metrics.exposureScore ?? 0);
  const confidenceScore = clamp(metrics.confidenceScore ?? metrics.confidence ?? 0);

  const rows = [
    { label: "Risk Score", value: riskScore },
    { label: "Exposure Score", value: exposureScore },
    { label: "Confidence", value: confidenceScore },
  ];

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
          Animated Risk Metrics
        </Typography>

        {rows.map((row) => (
          <Box key={row.label} sx={{ mb: 1.5 }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
              <Typography variant="caption">{row.label}</Typography>
              <Typography variant="caption" sx={{ fontWeight: 700 }}>
                {row.value}
              </Typography>
            </Box>

            <LinearProgress
              variant="determinate"
              value={row.value}
              sx={{
                height: 8,
                borderRadius: 4,
                transition: "all 500ms ease-in-out",
              }}
            />
          </Box>
        ))}
      </CardContent>
    </Card>
  );
}