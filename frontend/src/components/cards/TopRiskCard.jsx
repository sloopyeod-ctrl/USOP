import { Box, Card, CardContent, Chip, LinearProgress, Stack, Typography } from "@mui/material";

function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";
  if (value === "Medium") return "info";
  return "success";
}

export default function TopRiskCard({ identity, onClick }) {
  return (
    <Card
      onClick={onClick}
      sx={{
        mb: 2,
        cursor: "pointer",
        transition: "0.2s",
        "&:hover": {
          transform: "translateY(-2px)",
          boxShadow: 8,
          borderColor: "primary.main",
        },
      }}
    >
      <CardContent>
        <Stack
          direction={{ xs: "column", md: "row" }}
          justifyContent="space-between"
          alignItems={{ xs: "flex-start", md: "center" }}
          spacing={3}
        >
          <Box sx={{ flexGrow: 1, width: "100%" }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="h6" fontWeight={900}>
                {identity.display_name}
              </Typography>

              <Chip
                label={identity.exposure_rating}
                color={severityColor(identity.exposure_rating)}
                size="small"
                sx={{ fontWeight: 800 }}
              />
            </Stack>

            <Typography color="text.secondary" sx={{ mb: 2 }}>
              {identity.primary_email}
            </Typography>

            <Typography variant="body2" color="text.secondary">
              Exposure Score
            </Typography>

            <Stack direction="row" alignItems="center" spacing={2}>
              <Box sx={{ flexGrow: 1 }}>
                <LinearProgress
                  variant="determinate"
                  value={Math.min(identity.exposure_score, 100)}
                  color={severityColor(identity.exposure_rating)}
                  sx={{ height: 10, borderRadius: 10 }}
                />
              </Box>

              <Typography fontWeight={900}>{identity.exposure_score}</Typography>
            </Stack>
          </Box>

          <Stack spacing={1} sx={{ minWidth: 210 }}>
            <Typography>
              Risk: <strong>{identity.risk_score}</strong>
            </Typography>

            <Typography>
              Recommendations: <strong>{identity.recommendation_count}</strong>
            </Typography>

            <Typography>
              Policy Violations: <strong>{identity.policy_violations}</strong>
            </Typography>

            <Typography color="primary.main" fontWeight={800}>
              Open Analyst Workspace →
            </Typography>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}