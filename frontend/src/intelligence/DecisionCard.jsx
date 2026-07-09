import { Card, CardContent, Stack, Typography } from "@mui/material";

export default function DecisionCard({ title, subtitle, children }) {
  return (
    <Card
      sx={{
        border: "1px solid rgba(148, 163, 184, 0.18)",
      }}
    >
      <CardContent>
        <Stack spacing={1.5}>
          <Stack spacing={0.25}>
            <Typography variant="h6" fontWeight={800}>
              {title}
            </Typography>

            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Stack>

          {children}
        </Stack>
      </CardContent>
    </Card>
  );
}