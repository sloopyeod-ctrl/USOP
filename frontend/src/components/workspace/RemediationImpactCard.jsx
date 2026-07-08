import { Card, CardContent, Divider, Typography } from "@mui/material";

export default function RemediationImpactCard({ recommendations }) {
  const riskReduction = recommendations.reduce(
    (total, rec) => total + rec.risk_reduction,
    0
  );

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" fontWeight={800}>
          Remediation Impact
        </Typography>

        <Typography variant="h3" fontWeight={900} color="success.main" sx={{ mt: 2 }}>
          {riskReduction}
        </Typography>

        <Typography color="text.secondary">Estimated risk reduction</Typography>

        <Divider sx={{ my: 2 }} />

        <Typography>Actions: {recommendations.length}</Typography>

        <Typography>
          Est. effort: {recommendations.length * 5}–{recommendations.length * 15} min
        </Typography>
      </CardContent>
    </Card>
  );
}