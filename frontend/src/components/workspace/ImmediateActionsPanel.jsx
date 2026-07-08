import { Box, Card, CardContent, Chip, Divider, Stack, Typography } from "@mui/material";

function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";
  if (value === "Medium") return "info";
  return "success";
}

export default function ImmediateActionsPanel({ recommendations }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h5" fontWeight={800} gutterBottom>
          Immediate Actions
        </Typography>

        <Stack spacing={2}>
          {recommendations.map((rec, index) => (
            <Box key={`${rec.title}-${index}`}>
              <Stack direction="row" spacing={1} alignItems="center">
                <Chip label={`P${rec.priority}`} size="small" color="primary" />
                <Chip label={rec.severity} size="small" color={severityColor(rec.severity)} />
                <Typography fontWeight={800}>{rec.title}</Typography>
              </Stack>

              <Typography color="text.secondary" sx={{ mt: 1 }}>
                {rec.description}
              </Typography>

              <Typography variant="body2">
                Risk reduction: {rec.risk_reduction} • Effort: {rec.estimated_effort}
              </Typography>

              <Divider sx={{ mt: 2 }} />
            </Box>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}