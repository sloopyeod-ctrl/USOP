import { Box, Chip, Stack, Typography } from "@mui/material";

function formatValue(value) {
  if (value === null || value === undefined) return "—";
  return value;
}

export default function DecisionMetric({
  label,
  value,
  helperText,
  chipLabel,
  chipColor = "default",
}) {
  return (
    <Box
      sx={{
        p: 1.5,
        borderRadius: 2,
        border: "1px solid rgba(148, 163, 184, 0.16)",
        backgroundColor: "rgba(15, 23, 42, 0.35)",
      }}
    >
      <Stack spacing={0.5}>
        <Stack
          direction="row"
          spacing={1}
          sx={{
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Typography variant="caption" color="text.secondary" fontWeight={700}>
            {label}
          </Typography>

          {chipLabel && (
            <Chip label={chipLabel} color={chipColor} size="small" />
          )}
        </Stack>

        <Typography variant="h5" fontWeight={900}>
          {formatValue(value)}
        </Typography>

        {helperText && (
          <Typography variant="caption" color="text.secondary">
            {helperText}
          </Typography>
        )}
      </Stack>
    </Box>
  );
}