import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";

import BusinessIcon from
  "@mui/icons-material/Business";


export default function OrganizationContextBanner({
  activeOrganization,
  isLoadingOrganizations,
  organizationError,
}) {
  if (isLoadingOrganizations) {
    return (
      <Alert
        severity="info"
        icon={<CircularProgress size={18} />}
        sx={{ mb: 3 }}
      >
        Loading the active Organization context...
      </Alert>
    );
  }

  if (organizationError) {
    return (
      <Alert
        severity="error"
        sx={{ mb: 3 }}
      >
        {organizationError}
      </Alert>
    );
  }

  if (!activeOrganization) {
    return (
      <Alert
        severity="warning"
        sx={{ mb: 3 }}
      >
        Select an active Organization before recording
        accountable analyst decisions.
      </Alert>
    );
  }

  return (
    <Box
      sx={{
        mb: 3,
        px: 2,
        py: 1.5,
        borderRadius: 2,
        border:
          "1px solid rgba(34, 211, 238, 0.28)",
        backgroundColor:
          "rgba(8, 47, 73, 0.30)",
      }}
    >
      <Stack
        direction={{
          xs: "column",
          sm: "row",
        }}
        justifyContent="space-between"
        alignItems={{
          xs: "flex-start",
          sm: "center",
        }}
        spacing={1.5}
      >
        <Stack
          direction="row"
          spacing={1.25}
          alignItems="center"
        >
          <BusinessIcon color="primary" />

          <Box>
            <Typography
              variant="caption"
              sx={{
                color: "#94A3B8",
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: 0.8,
             }}
            >
              Active Organization
            </Typography>
            <Typography
              fontWeight={900}
              sx={{ color: "#E5E7EB" }}
            >
              {activeOrganization.name}
            </Typography>
          </Box>
        </Stack>

        <Stack
          direction="row"
          spacing={1}
          flexWrap="wrap"
          useFlexGap
        >
          <Chip
            label={
                activeOrganization.status
                || "Status unavailable"
            }
            color={
                activeOrganization.status === "Active"
                ? "success"
                : "default"
            }
            size="small"
            variant="outlined"
            sx={{
                color: "#E5E7EB",
                borderColor: "#475569",
            }}
            />

            <Chip
            label={
                activeOrganization.slug
                || activeOrganization.id
            }
            size="small"
            variant="outlined"
            sx={{
                color: "#E5E7EB",
                borderColor: "#475569",
            }}
          />
        </Stack>
      </Stack>
    </Box>
  );
}