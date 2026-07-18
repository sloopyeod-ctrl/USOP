import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import BusinessIcon from "@mui/icons-material/Business";
import PeopleAltIcon from "@mui/icons-material/PeopleAlt";


export default function PlatformAdministration() {
  return (
    <Box>
      <Card
        sx={{
          mb: 3,
          background:
            "linear-gradient(135deg, #111827 0%, #0B1220 60%, #083344 100%)",
          border: "1px solid #164E63",
        }}
      >
        <CardContent>
          <Stack
            direction={{
              xs: "column",
              md: "row",
            }}
            justifyContent="space-between"
            alignItems={{
              xs: "flex-start",
              md: "center",
            }}
            spacing={2}
          >
            <Stack
              direction="row"
              spacing={2}
              alignItems="center"
            >
              <AdminPanelSettingsIcon
                color="primary"
                sx={{ fontSize: 42 }}
              />

              <Box>
                <Typography
                  variant="h4"
                  fontWeight={900}
                >
                  Platform Administration
                </Typography>

                <Typography color="text.secondary">
                  Manage the USOP Organization and its
                  authorized Platform Users.
                </Typography>
              </Box>
            </Stack>

            <Chip
              label="READ ONLY"
              color="info"
              variant="outlined"
              sx={{ fontWeight: 800 }}
            />
          </Stack>
        </CardContent>
      </Card>

      <Alert
        severity="info"
        sx={{ mb: 3 }}
      >
        Administration is currently read-only. Authentication,
        invitations, role management, and commercial Seat
        allocation remain separate future capabilities.
      </Alert>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            lg: "minmax(280px, 360px) 1fr",
          },
          gap: 3,
        }}
      >
        <Card>
          <CardContent>
            <Stack
              direction="row"
              spacing={1.5}
              alignItems="center"
              sx={{ mb: 2 }}
            >
              <BusinessIcon color="primary" />

              <Typography
                variant="h5"
                fontWeight={800}
              >
                Organization
              </Typography>
            </Stack>

            <Divider sx={{ mb: 2 }} />

            <Typography
              color="text.secondary"
              sx={{ mb: 1 }}
            >
              Organization context has not been loaded.
            </Typography>

            <Typography variant="body2">
              The next increment will resolve the current
              Organization through the existing Organization API.
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
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
              spacing={2}
              sx={{ mb: 2 }}
            >
              <Stack
                direction="row"
                spacing={1.5}
                alignItems="center"
              >
                <PeopleAltIcon color="primary" />

                <Typography
                  variant="h5"
                  fontWeight={800}
                >
                  Platform Users
                </Typography>
              </Stack>

              <Chip
                label="0 USERS"
                size="small"
                variant="outlined"
              />
            </Stack>

            <Divider sx={{ mb: 2 }} />

            <Box
              sx={{
                minHeight: 220,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                border: "1px dashed #334155",
                borderRadius: 2,
                p: 3,
              }}
            >
              <Box>
                <Typography
                  fontWeight={800}
                  sx={{ mb: 1 }}
                >
                  No Platform Users Loaded
                </Typography>

                <Typography color="text.secondary">
                  Platform Users will appear after an
                  Organization context is resolved.
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
