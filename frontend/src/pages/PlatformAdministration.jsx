import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";

import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import BusinessIcon from "@mui/icons-material/Business";
import PeopleAltIcon from "@mui/icons-material/PeopleAlt";

import api from "../api/usopApi";


function DetailRow({
  label,
  value,
}) {
  return (
    <Stack
      direction="row"
      justifyContent="space-between"
      spacing={2}
    >
      <Typography color="text.secondary">
        {label}
      </Typography>

      <Typography
        fontWeight={700}
        textAlign="right"
      >
        {value || "Not configured"}
      </Typography>
    </Stack>
  );
}


export default function PlatformAdministration() {
  const [organizations, setOrganizations] = useState([]);
  const [
    selectedOrganizationId,
    setSelectedOrganizationId,
  ] = useState("");
  const [isLoadingOrganizations, setIsLoadingOrganizations] =
    useState(true);
  const [organizationError, setOrganizationError] =
    useState(null);

  useEffect(() => {
    let isCurrent = true;

    api
      .get("/api/v1/organizations/")
      .then((response) => {
        if (!isCurrent) return;

        const records = Array.isArray(response.data)
          ? response.data
          : [];

        setOrganizations(records);

        if (records.length === 1) {
          setSelectedOrganizationId(
            records[0].id,
          );
        }
      })
      .catch((error) => {
        if (!isCurrent) return;

        console.error(
          "Organization context load failed:",
          error,
        );

        setOrganizationError(
          "Could not load Organization context.",
        );
      })
      .finally(() => {
        if (isCurrent) {
          setIsLoadingOrganizations(false);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  const selectedOrganization = useMemo(
    () =>
      organizations.find(
        (organization) =>
          organization.id
          === selectedOrganizationId,
      ) || null,
    [
      organizations,
      selectedOrganizationId,
    ],
  );

  const organizationCount =
    organizations.length;

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
            lg: "minmax(320px, 420px) 1fr",
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

              {!isLoadingOrganizations && (
                <Chip
                  label={`${organizationCount} FOUND`}
                  size="small"
                  variant="outlined"
                />
              )}
            </Stack>

            <Divider sx={{ mb: 2 }} />

            {isLoadingOrganizations && (
              <Stack
                alignItems="center"
                spacing={2}
                sx={{ py: 5 }}
              >
                <CircularProgress size={32} />

                <Typography color="text.secondary">
                  Loading Organization context...
                </Typography>
              </Stack>
            )}

            {!isLoadingOrganizations
              && organizationError && (
              <Alert severity="error">
                {organizationError}
              </Alert>
            )}

            {!isLoadingOrganizations
              && !organizationError
              && organizationCount === 0 && (
              <Alert severity="warning">
                No USOP Organizations are configured.
                Create the initial Organization before
                Platform Users can be administered.
              </Alert>
            )}

            {!isLoadingOrganizations
              && !organizationError
              && organizationCount > 1 && (
              <FormControl
                fullWidth
                size="small"
                sx={{ mb: 3 }}
              >
                <InputLabel id="organization-select-label">
                  Organization
                </InputLabel>

                <Select
                  labelId="organization-select-label"
                  value={selectedOrganizationId}
                  label="Organization"
                  onChange={(event) =>
                    setSelectedOrganizationId(
                      event.target.value,
                    )
                  }
                >
                  {organizations.map(
                    (organization) => (
                      <MenuItem
                        key={organization.id}
                        value={organization.id}
                      >
                        {organization.name}
                      </MenuItem>
                    ),
                  )}
                </Select>
              </FormControl>
            )}

            {selectedOrganization && (
              <Stack spacing={1.5}>
                <Box>
                  <Typography
                    variant="h6"
                    fontWeight={900}
                  >
                    {selectedOrganization.name}
                  </Typography>

                  <Typography color="text.secondary">
                    {selectedOrganization.slug}
                  </Typography>
                </Box>

                <Divider />

                <DetailRow
                  label="Status"
                  value={selectedOrganization.status}
                />

                <DetailRow
                  label="Type"
                  value={
                    selectedOrganization
                      .organization_type
                  }
                />

                <DetailRow
                  label="Primary Domain"
                  value={
                    selectedOrganization
                      .primary_domain
                  }
                />

                <DetailRow
                  label="Time Zone"
                  value={
                    selectedOrganization
                      .time_zone
                  }
                />

                <DetailRow
                  label="Deployment"
                  value={
                    selectedOrganization
                      .deployment_identifier
                  }
                />
              </Stack>
            )}
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
                  {selectedOrganization
                    ? "Platform Users Not Yet Loaded"
                    : "Organization Required"}
                </Typography>

                <Typography color="text.secondary">
                  {selectedOrganization
                    ? (
                      "The next increment will load "
                      + "Organization-scoped Platform Users."
                    )
                    : (
                      "Configure or select an Organization "
                      + "before loading Platform Users."
                    )}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
