import {
  useEffect,
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

import AdminPanelSettingsIcon from
  "@mui/icons-material/AdminPanelSettings";
import BusinessIcon from
  "@mui/icons-material/Business";
import PeopleAltIcon from
  "@mui/icons-material/PeopleAlt";

import api from "../api/usopApi";
import useOrganizationContext from
  "../hooks/useOrganizationContext";


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
  const {
    organizations,
    activeOrganization:
      selectedOrganization,
    activeOrganizationId:
      selectedOrganizationId,
    setActiveOrganizationId:
      setSelectedOrganizationId,
    isLoadingOrganizations,
    organizationError,
  } = useOrganizationContext();

  const [
    platformUsers,
    setPlatformUsers,
  ] = useState([]);

  const [
    isLoadingPlatformUsers,
    setIsLoadingPlatformUsers,
  ] = useState(false);

  const [
    platformUserError,
    setPlatformUserError,
  ] = useState(null);


  useEffect(() => {
    let isCurrent = true;

    async function loadPlatformUsers() {
      if (!selectedOrganizationId) {
        setPlatformUsers([]);
        setPlatformUserError(null);
        setIsLoadingPlatformUsers(false);

        return;
      }

      await Promise.resolve();

      if (!isCurrent) {
        return;
      }

      setPlatformUsers([]);
      setPlatformUserError(null);
      setIsLoadingPlatformUsers(true);

      try {
        const response = await api.get(
          (
            "/api/v1/organizations/"
            + selectedOrganizationId
            + "/platform-users/"
          ),
        );

        if (!isCurrent) {
          return;
        }

        setPlatformUsers(
          Array.isArray(response.data)
            ? response.data
            : [],
        );
      } catch (error) {
        if (!isCurrent) {
          return;
        }

        console.error(
          "Platform User load failed:",
          error,
        );

        setPlatformUserError(
          "Could not load Platform Users.",
        );
      } finally {
        if (isCurrent) {
          setIsLoadingPlatformUsers(false);
        }
      }
    }

    loadPlatformUsers();

    return () => {
      isCurrent = false;
    };
  }, [selectedOrganizationId]);


  const organizationCount =
    organizations.length;


  return (
    <Box>
      <Card
        sx={{
          mb: 3,
          background:
            "linear-gradient("
            + "135deg, "
            + "#111827 0%, "
            + "#0B1220 60%, "
            + "#083344 100%"
            + ")",
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
        Administration is currently read-only.
        Authentication, invitations, role management,
        and commercial Seat allocation remain separate
        future capabilities.
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
                <InputLabel
                  id="organization-select-label"
                >
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
                  value={
                    selectedOrganization.status
                  }
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
                label={
                  `${platformUsers.length} USERS`
                }
                size="small"
                variant="outlined"
              />
            </Stack>

            <Divider sx={{ mb: 2 }} />

            {!selectedOrganization && (
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
                    Organization Required
                  </Typography>

                  <Typography color="text.secondary">
                    Configure or select an Organization
                    before loading Platform Users.
                  </Typography>
                </Box>
              </Box>
            )}

            {selectedOrganization
              && isLoadingPlatformUsers && (
              <Stack
                alignItems="center"
                spacing={2}
                sx={{ py: 7 }}
              >
                <CircularProgress size={32} />

                <Typography color="text.secondary">
                  Loading Platform Users...
                </Typography>
              </Stack>
            )}

            {selectedOrganization
              && !isLoadingPlatformUsers
              && platformUserError && (
              <Alert severity="error">
                {platformUserError}
              </Alert>
            )}

            {selectedOrganization
              && !isLoadingPlatformUsers
              && !platformUserError
              && platformUsers.length === 0 && (
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
                    No Platform Users Found
                  </Typography>

                  <Typography color="text.secondary">
                    This Organization has no Platform
                    Users. The first administrator
                    bootstrap has not yet been completed.
                  </Typography>
                </Box>
              </Box>
            )}

            {selectedOrganization
              && !isLoadingPlatformUsers
              && !platformUserError
              && platformUsers.length > 0 && (
              <Stack spacing={2}>
                {platformUsers.map(
                  (platformUser) => (
                    <Card
                      key={platformUser.id}
                      variant="outlined"
                    >
                      <CardContent>
                        <Stack
                          direction={{
                            xs: "column",
                            sm: "row",
                          }}
                          justifyContent="space-between"
                          spacing={2}
                        >
                          <Box>
                            <Typography
                              variant="h6"
                              fontWeight={900}
                            >
                              {
                                platformUser
                                  .display_name
                              }
                            </Typography>

                            <Typography
                              color="text.secondary"
                            >
                              {platformUser.email}
                            </Typography>
                          </Box>

                          <Chip
                            label={
                              platformUser.status
                            }
                            color={
                              platformUser.status
                              === "Active"
                                ? "success"
                                : "info"
                            }
                            size="small"
                          />
                        </Stack>

                        <Divider sx={{ my: 2 }} />

                        <Stack spacing={1}>
                          <DetailRow
                            label="Identity Provider"
                            value={
                              platformUser
                                .identity_provider
                            }
                          />

                          <DetailRow
                            label="Bootstrap User"
                            value={
                              platformUser
                                .created_via_bootstrap
                                ? "Yes"
                                : "No"
                            }
                          />

                          <DetailRow
                            label="Invited"
                            value={
                              platformUser.invited_at
                                ? new Date(
                                  platformUser
                                    .invited_at,
                                ).toLocaleString()
                                : "Never"
                            }
                          />

                          <DetailRow
                            label="Activated"
                            value={
                              platformUser.activated_at
                                ? new Date(
                                  platformUser
                                    .activated_at,
                                ).toLocaleString()
                                : "Not activated"
                            }
                          />

                          <DetailRow
                            label="Last Authentication"
                            value={
                              platformUser
                                .last_authenticated_at
                                ? new Date(
                                  platformUser
                                    .last_authenticated_at,
                                ).toLocaleString()
                                : "Never"
                            }
                          />
                        </Stack>
                      </CardContent>
                    </Card>
                  ),
                )}
              </Stack>
            )}
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
