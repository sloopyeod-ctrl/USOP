import { Box, Card, CardContent, Chip, Divider, Stack, Typography } from "@mui/material";

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
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h5" fontWeight={800}>
            Immediate Actions
          </Typography>

          {selectedNode && (
            <Chip
              label={`Context: ${selectedNode.data.nodeType}`}
              color="primary"
              size="small"
            />
          )}
        </Stack>

        <Stack spacing={2}>
          {visibleRecommendations.map((rec, index) => (
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