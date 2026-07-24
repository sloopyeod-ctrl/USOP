import {
  Box,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";

function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";
  if (value === "Medium") return "info";
  return "success";
}

function filterRecommendations(recommendations, selectedNode) {
  if (!selectedNode) return recommendations;

  const details = selectedNode.data.details || {};
  const username = details.username;
  const groupName = details.group_name;
  const roleName = details.role_name;

  const filtered = recommendations.filter((rec) => {
    const text = `${rec.title} ${rec.description}`.toLowerCase();

    return (
      (username && text.includes(username.toLowerCase())) ||
      (groupName && text.includes(groupName.toLowerCase())) ||
      (roleName && text.includes(roleName.toLowerCase()))
    );
  });

  return filtered.length ? filtered : recommendations;
}

export default function ImmediateActionsPanel({ recommendations, selectedNode }) {
  const visibleRecommendations = filterRecommendations(recommendations, selectedNode);

  return (
    <Card>
      <CardContent>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          sx={{ mb: 2 }}
        >
          <Box>
            <Typography variant="h5" fontWeight={900}>
              Immediate Actions
            </Typography>

            <Typography color="text.secondary">
              Showing {visibleRecommendations.length} of {recommendations.length} recommendations
            </Typography>
          </Box>

          {selectedNode && (
            <Chip
              label={`Context: ${selectedNode.data.nodeType}`}
              color="primary"
              size="small"
              sx={{ fontWeight: 800 }}
            />
          )}
        </Stack>

        <Stack spacing={2}>
          {visibleRecommendations.map((rec, index) => (
            <Card
              key={`${rec.title}-${index}`}
              sx={{
                background: "linear-gradient(135deg, #111827 0%, #0B1220 100%)",
                border:
                  rec.severity === "Critical"
                    ? "1px solid #7F1D1D"
                    : "1px solid #1F2937",
              }}
            >
              <CardContent>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                  <Chip label={`P${rec.priority}`} size="small" color="primary" />
                  <Chip
                    label={rec.severity}
                    size="small"
                    color={severityColor(rec.severity)}
                  />
                  <Typography fontWeight={900}>{rec.title}</Typography>
                </Stack>

                <Typography color="text.secondary" sx={{ mb: 2 }}>
                  {rec.description}
                </Typography>

                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Risk Reduction
                  </Typography>
                  <Typography fontWeight={900}>{rec.risk_reduction}</Typography>
                </Stack>

                <LinearProgress
                  variant="determinate"
                  value={Math.min(rec.risk_reduction * 3, 100)}
                  color={severityColor(rec.severity)}
                  sx={{ mt: 1, mb: 2, height: 8, borderRadius: 10 }}
                />

                <Typography variant="body2" color="text.secondary">
                  Estimated effort: {rec.estimated_effort}
                </Typography>
               
              </CardContent>
            </Card>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}