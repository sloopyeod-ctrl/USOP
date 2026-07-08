import { Card, CardContent, Divider, Typography } from "@mui/material";

export default function RiskSummaryCard({ risk, access }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h5" fontWeight={800}>
          Risk Summary
        </Typography>

        <Typography variant="h3" fontWeight={900} sx={{ mt: 2 }}>
          {risk.score}
        </Typography>

        <Typography color="text.secondary">{risk.level} Risk</Typography>

        <Divider sx={{ my: 2 }} />

        <Typography>Findings: {risk.findings.length}</Typography>
        <Typography>Accounts: {access.accounts.length}</Typography>
        <Typography>Groups: {access.groups.length}</Typography>
        <Typography>Roles: {access.roles.length}</Typography>
      </CardContent>
    </Card>
  );
}