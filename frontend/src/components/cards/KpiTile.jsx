import { Box, Card, CardContent, Stack, Typography } from "@mui/material";

export default function KpiTile({ icon, label, value, accent }) {
  return (
    <Card
      sx={{
        minWidth: 210,
        flex: "1 1 210px",
        background: `linear-gradient(135deg, #111827 0%, ${accent}22 100%)`,
        borderTop: `3px solid ${accent}`,
      }}
    >
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>{icon}</Box>
          <Typography variant="h3" fontWeight={900}>
            {value}
          </Typography>
        </Stack>

        <Typography color="text.secondary" sx={{ mt: 1 }}>
          {label}
        </Typography>
      </CardContent>
    </Card>
  );
}