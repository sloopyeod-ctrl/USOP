import { Box, Card, CardContent, Chip, Stack, Typography } from "@mui/material";

function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";
  if (value === "Medium") return "info";
  return "success";
}

export default function WorkspaceHeader({ identity, exposure }) {
  return (
    <Card
      sx={{
        mb: 3,
        background:
          "linear-gradient(135deg, #111827 0%, #0B1220 60%, #7F1D1D 100%)",
        border: "1px solid #7F1D1D",
      }}
    >
      <CardContent>
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          sx={{
            justifyContent: "space-between",
            alignItems: { xs: "flex-start", md: "center" },
          }}
        >
          <Box>
            <Typography variant="h4" fontWeight={900}>
              Analyst Workspace
            </Typography>

            <Typography variant="h6" color="text.secondary">
              {identity.display_name} • {identity.primary_email}
            </Typography>
          </Box>

          <Chip
            label={`${exposure.rating} Exposure`}
            color={severityColor(exposure.rating)}
            sx={{ fontWeight: 900 }}
          />
        </Stack>
      </CardContent>
    </Card>
  );
}