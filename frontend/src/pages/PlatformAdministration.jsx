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

import AdminPanelSettingsIcon from
  "@mui/icons-material/AdminPanelSettings";
import ApiIcon from
  "@mui/icons-material/Api";
import BusinessIcon from
  "@mui/icons-material/Business";
import CheckCircleIcon from
  "@mui/icons-material/CheckCircle";
import WarningAmberIcon from
  "@mui/icons-material/WarningAmber";
import PeopleAltIcon from
  "@mui/icons-material/PeopleAlt";
import StorageIcon from
  "@mui/icons-material/Storage";

import useOrganizationContext from
  "../hooks/useOrganizationContext";
import {
  getPlatformHealth,
  listPlatformUsers,
  listRegisteredConnectors,
} from "../services/platformOperationsService";


function DetailRow({
  label,
  value,
}) {
  return (
    <Stack
      direction="row"
      justifyContent="space-between"
      alignItems="flex-start"
      spacing={2}
    >
      <Typography color="text.secondary">
        {label}
      </Typography>

      <Typography
        fontWeight={700}
        textAlign="right"
        sx={{
          overflowWrap: "anywhere",
        }}
      >
        {value || "Not configured"}
      </Typography>
    </Stack>
  );
}


function SummaryMetric({
  label,
  value,
  emphasis = false,
}) {
  return (
    <Box>
      <Typography
        variant="body2"
        color="text.secondary"
      >
        {label}
      </Typography>

      <Typography
        variant={emphasis ? "h4" : "h6"}
        fontWeight={900}
      >
        {value}
      </Typography>
    </Box>
  );
}


function StatusChip({
  status,
  healthy,
}) {
  if (healthy === true) {
    return (
      <Chip
        icon={<CheckCircleIcon />}
        label={status || "Healthy"}
        color="success"
        size="small"
        sx={{ fontWeight: 800 }}
      />
    );
  }

  if (healthy === false) {
    return (
      <Chip
        icon={<WarningAmberIcon />}
        label={status || "Unavailable"}
        color="error"
        size="small"
        sx={{ fontWeight: 800 }}
      />
    );
  }

  return (
    <Chip
      label={status || "Unknown"}
      variant="outlined"
      size="small"
      sx={{ fontWeight: 800 }}
    />
  );
}


function OperationalSummaryCard({
  icon,
  title,
  status,
  healthy,
  isLoading = false,
  error = null,
  children,
}) {
  return (
    <Card
      sx={{
        height: "100%",
        border: (
          healthy === false
            ? "1px solid rgba(239,68,68,.55)"
            : "1px solid rgba(148,163,184,.18)"
        ),
      }}
    >
      <CardContent>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="flex-start"
          spacing={2}
          sx={{ mb: 2 }}
        >
          <Stack
            direction="row"
            spacing={1.25}
            alignItems="center"
          >
            {icon}

            <Typography
              variant="h6"
              fontWeight={900}
            >
              {title}
            </Typography>
          </Stack>

          {!isLoading && (
            <StatusChip
              status={status}
              healthy={healthy}
            />
          )}
        </Stack>

        <Divider sx={{ mb: 2 }} />

        {isLoading && (
          <Stack
            direction="row"
            spacing={1.5}
            alignItems="center"
            sx={{ py: 2 }}
          >
            <CircularProgress size={24} />

            <Typography color="text.secondary">
              Loading current state...
            </Typography>
          </Stack>
        )}

        {!isLoading && error && (
          <Alert severity="error">
            {error}
          </Alert>
        )}

        {!isLoading && !error && children}
      </CardContent>
    </Card>
  );
}


function formatDateTime(value) {
  if (!value) {
    return "Never";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unavailable";
  }

  return date.toLocaleString();
}


function countPlatformUsersByStatus(
  platformUsers,
  status,
) {
  return platformUsers.filter(
    (platformUser) =>
      platformUser.status === status,
  ).length;
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
    platformHealth,
    setPlatformHealth,
  ] = useState(null);

  const [
    registeredConnectors,
    setRegisteredConnectors,
  ] = useState([]);

  const [
    isLoadingPlatformUsers,
    setIsLoadingPlatformUsers,
  ] = useState(false);

  const [
    isLoadingPlatformHealth,
    setIsLoadingPlatformHealth,
  ] = useState(true);

  const [
    isLoadingConnectors,
    setIsLoadingConnectors,
  ] = useState(true);

  const [
    platformUserError,
    setPlatformUserError,
  ] = useState(null);

  const [
    platformHealthError,
    setPlatformHealthError,
  ] = useState(null);

  const [
    connectorError,
    setConnectorError,
  ] = useState(null);


  useEffect(() => {
    let isCurrent = true;

    async function loadPlatformOperations() {
      setIsLoadingPlatformHealth(true);
      setIsLoadingConnectors(true);
      setPlatformHealthError(null);
      setConnectorError(null);

      const [
        healthResult,
        connectorResult,
      ] = await Promise.allSettled([
        getPlatformHealth(),
        listRegisteredConnectors(),
      ]);

      if (!isCurrent) {
        return;
      }

      if (healthResult.status === "fulfilled") {
        setPlatformHealth(
          healthResult.value,
        );
      } else {
        console.error(
          "Platform health load failed:",
          healthResult.reason,
        );

        setPlatformHealth(null);
        setPlatformHealthError(
          "USOP API health could not be verified.",
        );
      }

      if (
        connectorResult.status
        === "fulfilled"
      ) {
        setRegisteredConnectors(
          connectorResult.value,
        );
      } else {
        console.error(
          "Connector inventory load failed:",
          connectorResult.reason,
        );

        setRegisteredConnectors([]);
        setConnectorError(
          "Registered connectors could not be loaded.",
        );
      }

      setIsLoadingPlatformHealth(false);
      setIsLoadingConnectors(false);
    }

    loadPlatformOperations();

    return () => {
      isCurrent = false;
    };
  }, []);


  useEffect(() => {
    let isCurrent = true;

    async function loadUsers() {
      if (!selectedOrganizationId) {
        setPlatformUsers([]);
        setPlatformUserError(null);
        setIsLoadingPlatformUsers(false);

        return;
      }

      setPlatformUsers([]);
      setPlatformUserError(null);
      setIsLoadingPlatformUsers(true);

      try {
        const records = await listPlatformUsers({
          organizationId:
            selectedOrganizationId,
        });

        if (!isCurrent) {
          return;
        }

        setPlatformUsers(records);
      } catch (error) {
        if (!isCurrent) {
          return;
        }

        console.error(
          "Platform User load failed:",
          error,
        );

        setPlatformUserError(
          "Platform Users could not be loaded.",
        );
      } finally {
        if (isCurrent) {
          setIsLoadingPlatformUsers(false);
        }
      }
    }

    loadUsers();

    return () => {
      isCurrent = false;
    };
  }, [selectedOrganizationId]);


  const organizationCount =
    organizations.length;

  const activePlatformUserCount =
    useMemo(
      () =>
        countPlatformUsersByStatus(
          platformUsers,
          "Active",
        ),
      [platformUsers],
    );

  const invitedPlatformUserCount =
    useMemo(
      () =>
        countPlatformUsersByStatus(
          platformUsers,
          "Invited",
        ),
      [platformUsers],
    );

  const disabledPlatformUserCount =
    useMemo(
      () =>
        countPlatformUsersByStatus(
          platformUsers,
          "Disabled",
        ),
      [platformUsers],
    );

  const apiHealthy =
    platformHealth?.status === "healthy";

  const organizationHealthy =
    selectedOrganization?.status === "Active";

  const platformUserSummaryHealthy =
    Boolean(selectedOrganization)
    && !platformUserError;

  const connectorInventoryHealthy =
    !connectorError;


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
                  Platform Operations
                </Typography>

                <Typography color="text.secondary">
                  Understand the operational state of
                  USOP before beginning the day.
                </Typography>
              </Box>
            </Stack>

            <StatusChip
              status={
                apiHealthy
                  ? "PLATFORM AVAILABLE"
                  : "ATTENTION REQUIRED"
              }
              healthy={apiHealthy}
            />
          </Stack>
        </CardContent>
      </Card>

      <Typography
        variant="h5"
        fontWeight={900}
        sx={{ mb: 0.5 }}
      >
        Operational Overview
      </Typography>

      <Typography
        color="text.secondary"
        sx={{ mb: 2.5 }}
      >
        Current platform state from live USOP
        services. Detailed administration remains
        available below.
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            md: "repeat(2, minmax(0, 1fr))",
            xl: "repeat(4, minmax(0, 1fr))",
          },
          gap: 2,
          mb: 4,
        }}
      >
        <OperationalSummaryCard
          icon={<ApiIcon color="primary" />}
          title="USOP API"
          status={
            platformHealth?.status
              || (
                platformHealthError
                  ? "Unavailable"
                  : "Unknown"
              )
          }
          healthy={
            platformHealthError
              ? false
              : apiHealthy
          }
          isLoading={isLoadingPlatformHealth}
          error={platformHealthError}
        >
          <Stack spacing={1.5}>
            <SummaryMetric
              label="Version"
              value={
                platformHealth?.version
                || "Not reported"
              }
              emphasis
            />

            <Typography color="text.secondary">
              The API is responding and reporting its
              current application version.
            </Typography>
          </Stack>
        </OperationalSummaryCard>

        <OperationalSummaryCard
          icon={<BusinessIcon color="primary" />}
          title="Organization"
          status={
            selectedOrganization?.status
            || (
              organizationError
                ? "Unavailable"
                : "Not selected"
            )
          }
          healthy={
            organizationError
              ? false
              : (
                selectedOrganization
                  ? organizationHealthy
                  : null
              )
          }
          isLoading={isLoadingOrganizations}
          error={organizationError}
        >
          {selectedOrganization ? (
            <Stack spacing={1.5}>
              <SummaryMetric
                label="Active Organization"
                value={selectedOrganization.name}
                emphasis
              />

              <DetailRow
                label="Type"
                value={
                  selectedOrganization
                    .organization_type
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
          ) : (
            <Alert severity="warning">
              No active Organization is selected.
            </Alert>
          )}
        </OperationalSummaryCard>

        <OperationalSummaryCard
          icon={<PeopleAltIcon color="primary" />}
          title="Platform Users"
          status={
            platformUserError
              ? "Unavailable"
              : (
                selectedOrganization
                  ? `${platformUsers.length} Total`
                  : "Organization required"
              )
          }
          healthy={
            platformUserError
              ? false
              : (
                selectedOrganization
                  ? platformUserSummaryHealthy
                  : null
              )
          }
          isLoading={isLoadingPlatformUsers}
          error={platformUserError}
        >
          {selectedOrganization ? (
            <Stack
              direction="row"
              justifyContent="space-between"
              spacing={2}
            >
              <SummaryMetric
                label="Active"
                value={activePlatformUserCount}
                emphasis
              />

              <SummaryMetric
                label="Invited"
                value={invitedPlatformUserCount}
              />

              <SummaryMetric
                label="Disabled"
                value={disabledPlatformUserCount}
              />
            </Stack>
          ) : (
            <Alert severity="info">
              Select an Organization to evaluate its
              Platform Users.
            </Alert>
          )}
        </OperationalSummaryCard>

        <OperationalSummaryCard
          icon={<StorageIcon color="primary" />}
          title="Connectors"
          status={
            connectorError
              ? "Unavailable"
              : `${registeredConnectors.length} Registered`
          }
          healthy={
            connectorError
              ? false
              : connectorInventoryHealthy
          }
          isLoading={isLoadingConnectors}
          error={connectorError}
        >
          {registeredConnectors.length > 0 ? (
            <Stack spacing={1.25}>
              <SummaryMetric
                label="Available Providers"
                value={registeredConnectors.length}
                emphasis
              />

              <Stack
                direction="row"
                spacing={1}
                useFlexGap
                flexWrap="wrap"
              >
                {registeredConnectors.map(
                  (connectorName) => (
                    <Chip
                      key={connectorName}
                      label={connectorName}
                      variant="outlined"
                      size="small"
                    />
                  ),
                )}
              </Stack>

              <Typography
                variant="body2"
                color="text.secondary"
              >
                Registration confirms availability.
                Runtime connector health will be added
                when that API contract is exposed.
              </Typography>
            </Stack>
          ) : (
            <Alert severity="warning">
              No connector providers are registered.
            </Alert>
          )}
        </OperationalSummaryCard>
      </Box>

      <Divider sx={{ mb: 3 }} />

      <Typography
        variant="h5"
        fontWeight={900}
        sx={{ mb: 0.5 }}
      >
        Administration Details
      </Typography>

      <Typography
        color="text.secondary"
        sx={{ mb: 2.5 }}
      >
        Review the active Organization and its
        authorized USOP Platform Users.
      </Typography>

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
                label={`${platformUsers.length} USERS`}
                size="small"
                variant="outlined"
              />
            </Stack>

            <Divider sx={{ mb: 2 }} />

            {!selectedOrganization && (
              <Alert severity="info">
                Select an Organization before loading
                Platform Users.
              </Alert>
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
              <Alert severity="warning">
                This Organization has no Platform Users.
              </Alert>
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
                            label={platformUser.status}
                            color={
                              platformUser.status
                              === "Active"
                                ? "success"
                                : (
                                  platformUser.status
                                  === "Disabled"
                                    ? "error"
                                    : "info"
                                )
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
                            value={formatDateTime(
                              platformUser.invited_at,
                            )}
                          />

                          <DetailRow
                            label="Activated"
                            value={
                              platformUser.activated_at
                                ? formatDateTime(
                                  platformUser
                                    .activated_at,
                                )
                                : "Not activated"
                            }
                          />

                          <DetailRow
                            label="Last Authentication"
                            value={formatDateTime(
                              platformUser
                                .last_authenticated_at,
                            )}
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


