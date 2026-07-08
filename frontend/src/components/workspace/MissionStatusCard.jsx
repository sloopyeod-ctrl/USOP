import { Card, CardContent, LinearProgress, Typography } from "@mui/material";

function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";
  if (value === "Medium") return "info";
  return "success";
}

export default function MissionStatusCard({
  exposure,
  missingMfaCount,
  privilegedAccountCount,
}) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h5" fontWeight={800}>
          Mission Status
        </Typography>

        <Typography variant="h3" fontWeight={900} color="error.main" sx={{ mt: 2 }}>
          {exposure.score}
        </Typography>

        <Typography color="text.secondary">Exposure Score</Typography>

        <LinearProgress
          variant="determinate"
          value={Math.min(exposure.score, 100)}
          color={severityColor(exposure.rating)}
          sx={{ mt: 2, height: 12, borderRadius: 10 }}
        />

        <Typography sx={{ mt: 2 }} fontWeight={700}>
          Immediate Action Required
        </Typography>

        <Typography color="text.secondary">
          {missingMfaCount} MFA gaps • {privilegedAccountCount} privileged accounts
        </Typography>
      </CardContent>
    </Card>
  );
}