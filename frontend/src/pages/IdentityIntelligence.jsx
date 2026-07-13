import { useEffect, useState } from "react";
import {
  useNavigate,
  useParams,
} from "react-router-dom";

import api from "../api/usopApi";

import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";

import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import PsychologyIcon from "@mui/icons-material/Psychology";


function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";
  if (value === "Medium") return "info";
  return "success";
}


function KpiCard({
  label,
  value,
  color,
  helper,
}) {
  return (
    <Card
      sx={{
        minWidth: 180,
        flex: "1 1 180px",
      }}
    >
      <CardContent>
        <Typography
          variant="h4"
          fontWeight={800}
          color={color || "text.primary"}
        >
          {value}
        </Typography>

        <Typography color="text.secondary">
          {label}
        </Typography>

        {helper && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 1 }}
          >
            {helper}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}


export default function IdentityIntelligence() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [intelligence, setIntelligence] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) {
      setError("No identity was selected.");
      return;
    }

    localStorage.setItem(
      "usop.activeInvestigationIdentityId",
      id,
    );

    api
      .get(`/identity-intelligence/${id}`)
      .then((response) => {
        setIntelligence(response.data);
      })
      .catch((err) => {
        console.error(
          "Identity intelligence load failed:",
          err,
        );

        setError(
          "Could not load identity intelligence.",
        );
      });
  }, [id]);

  function openAnalystWorkspace() {
    navigate(`/workspace/${id}`);
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (!intelligence) {
    return <CircularProgress />;
  }

  const {
    identity,
    risk,
    exposure,
    access,
    recommendations,
    timeline,
  } = intelligence;

  const latestTimeline = timeline.slice(0, 10);
  const topRecommendations = recommendations.slice(0, 6);

  const privilegedAccounts = access.accounts.filter(
    (account) =>
      account.privilege_level === "Privileged",
  ).length;

  const missingMfaAccounts = access.accounts.filter(
    (account) => !account.mfa_enabled,
  ).length;

  return (
    <Box>
      <Card
        sx={{
          mb: 3,
          border: "1px solid #1F2933",
          background:
            exposure.rating === "Critical"
              ? "linear-gradient(135deg, #141B23 0%, #2A1114 100%)"
              : "background.paper",
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
            spacing={3}
          >
            <Box>
              <Stack
                direction="row"
                spacing={1}
                alignItems="center"
                sx={{ mb: 1 }}
              >
                <Typography
                  variant="h4"
                  fontWeight={900}
                >
                  {identity.display_name}
                </Typography>

                <Chip
                  label={`${exposure.rating} Exposure`}
                  color={severityColor(
                    exposure.rating,
                  )}
                  sx={{ fontWeight: 700 }}
                />
              </Stack>

              <Typography color="text.secondary">
                {identity.primary_email}
              </Typography>

              <Typography
                color="text.secondary"
                sx={{ mt: 1 }}
              >
                Identity Intelligence combines
                exposure, risk, access relationships,
                timeline activity, and recommended
                actions.
              </Typography>

              <Button
                variant="contained"
                startIcon={<PsychologyIcon />}
                onClick={openAnalystWorkspace}
                sx={{
                  mt: 2,
                  fontWeight: 800,
                }}
              >
                Open Analyst Workspace
              </Button>
            </Box>

            <Box sx={{ minWidth: 260 }}>
              <Typography
                variant="body2"
                color="text.secondary"
              >
                Exposure Score
              </Typography>

              <Stack
                direction="row"
                alignItems="center"
                spacing={2}
              >
                <Box sx={{ flexGrow: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(
                      exposure.score,
                      100,
                    )}
                    color={severityColor(
                      exposure.rating,
                    )}
                    sx={{
                      height: 12,
                      borderRadius: 12,
                    }}
                  />
                </Box>

                <Typography
                  variant="h4"
                  fontWeight={900}
                >
                  {exposure.score}
                </Typography>
              </Stack>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      <Stack
        direction="row"
        spacing={2}
        sx={{
          mb: 3,
          flexWrap: "wrap",
        }}
      >
        <KpiCard
          label="Risk Score"
          value={risk.score}
          helper={risk.level}
        />

        <KpiCard
          label="Accounts"
          value={access.accounts.length}
          helper={`${privilegedAccounts} privileged`}
        />

        <KpiCard
          label="MFA Gaps"
          value={missingMfaAccounts}
          color={
            missingMfaAccounts > 0
              ? "error.main"
              : "success.main"
          }
          helper="Accounts without MFA"
        />

        <KpiCard
          label="Recommendations"
          value={recommendations.length}
        />

        <KpiCard
          label="Groups"
          value={access.groups.length}
        />

        <KpiCard
          label="Roles"
          value={access.roles.length}
        />
      </Stack>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            lg: "1fr 1fr",
          },
          gap: 3,
        }}
      >
        <Stack spacing={3}>
          <Card>
            <CardContent>
              <Typography
                variant="h5"
                fontWeight={700}
                gutterBottom
              >
                Exposure Breakdown
              </Typography>

              {Object.entries(
                exposure.breakdown,
              ).map(([key, value]) => (
                <Box
                  key={key}
                  sx={{ mb: 2 }}
                >
                  <Stack
                    direction="row"
                    justifyContent="space-between"
                  >
                    <Typography
                      sx={{
                        textTransform: "capitalize",
                      }}
                    >
                      {key.replaceAll("_", " ")}
                    </Typography>

                    <Typography fontWeight={700}>
                      {value}
                    </Typography>
                  </Stack>

                  <LinearProgress
                    variant="determinate"
                    value={Math.min(value, 100)}
                    sx={{
                      mt: 1,
                      height: 8,
                      borderRadius: 8,
                    }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography
                variant="h5"
                fontWeight={700}
                gutterBottom
              >
                Access Summary
              </Typography>

              <Accordion defaultExpanded>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                >
                  <Typography fontWeight={700}>
                    Accounts (
                    {access.accounts.length})
                  </Typography>
                </AccordionSummary>

                <AccordionDetails>
                  {access.accounts.map(
                    (account) => (
                      <Box
                        key={account.id}
                        sx={{ mb: 2 }}
                      >
                        <Stack
                          direction="row"
                          spacing={1}
                          alignItems="center"
                        >
                          <Typography
                            fontWeight={700}
                          >
                            {account.username}
                          </Typography>

                          {account.privilege_level
                            === "Privileged" && (
                            <Chip
                              label="Privileged"
                              size="small"
                              color="error"
                            />
                          )}

                          {!account.mfa_enabled && (
                            <Chip
                              label="No MFA"
                              size="small"
                              color="warning"
                            />
                          )}
                        </Stack>

                        <Typography color="text.secondary">
                          {account.system_name}
                          {" | "}
                          {account.account_type}
                          {" | "}
                          {account.status}
                        </Typography>

                        <Divider sx={{ mt: 1 }} />
                      </Box>
                    ),
                  )}
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                >
                  <Typography fontWeight={700}>
                    Groups ({access.groups.length})
                  </Typography>
                </AccordionSummary>

                <AccordionDetails>
                  {access.groups.map(
                    (group, index) => (
                      <Box
                        key={`${group.group_id}-${index}`}
                        sx={{ mb: 2 }}
                      >
                        <Typography fontWeight={700}>
                          {group.group_name}
                        </Typography>

                        <Typography color="text.secondary">
                          Account: {group.username}
                        </Typography>

                        <Typography variant="body2">
                          Privilege:{" "}
                          {group.privilege_level
                            || "None"}
                        </Typography>

                        <Divider sx={{ mt: 1 }} />
                      </Box>
                    ),
                  )}
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                >
                  <Typography fontWeight={700}>
                    Roles ({access.roles.length})
                  </Typography>
                </AccordionSummary>

                <AccordionDetails>
                  {access.roles.map(
                    (role, index) => (
                      <Box
                        key={`${role.role_id}-${index}`}
                        sx={{ mb: 2 }}
                      >
                        <Typography fontWeight={700}>
                          {role.role_name}
                        </Typography>

                        <Typography color="text.secondary">
                          Account: {role.username}
                        </Typography>

                        <Typography variant="body2">
                          Privilege:{" "}
                          {role.privilege_level
                            || "None"}
                        </Typography>

                        <Divider sx={{ mt: 1 }} />
                      </Box>
                    ),
                  )}
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        </Stack>

        <Stack spacing={3}>
          <Card>
            <CardContent>
              <Typography
                variant="h5"
                fontWeight={700}
                gutterBottom
              >
                Immediate Actions
              </Typography>

              <Box
                sx={{
                  maxHeight: 520,
                  overflowY: "auto",
                  pr: 1,
                }}
              >
                {topRecommendations.map(
                  (recommendation, index) => (
                    <Box
                      key={`${recommendation.title}-${index}`}
                      sx={{ mb: 2 }}
                    >
                      <Stack
                        direction="row"
                        spacing={1}
                        alignItems="center"
                      >
                        <Chip
                          label={`P${recommendation.priority}`}
                          size="small"
                          color="primary"
                        />

                        <Chip
                          label={
                            recommendation.severity
                          }
                          size="small"
                          color={severityColor(
                            recommendation.severity,
                          )}
                        />

                        <Typography fontWeight={700}>
                          {recommendation.title}
                        </Typography>
                      </Stack>

                      <Typography
                        color="text.secondary"
                        sx={{ mt: 1 }}
                      >
                        {recommendation.description}
                      </Typography>

                      <Typography
                        variant="body2"
                        sx={{ mt: 0.5 }}
                      >
                        Risk reduction:{" "}
                        {recommendation.risk_reduction}
                        {" | "}
                        Effort:{" "}
                        {recommendation.estimated_effort}
                      </Typography>

                      <Divider sx={{ mt: 2 }} />
                    </Box>
                  ),
                )}
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography
                variant="h5"
                fontWeight={700}
                gutterBottom
              >
                Recent Timeline
              </Typography>

              <Box
                sx={{
                  maxHeight: 520,
                  overflowY: "auto",
                  pr: 1,
                }}
              >
                {latestTimeline.map(
                  (event, index) => (
                    <Box
                      key={`${event.event_type}-${index}`}
                      sx={{ mb: 2 }}
                    >
                      <Typography fontWeight={700}>
                        {event.event_type}
                      </Typography>

                      <Typography color="text.secondary">
                        {event.message}
                      </Typography>

                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        {new Date(
                          event.timestamp,
                        ).toLocaleString()}
                      </Typography>

                      <Divider sx={{ mt: 2 }} />
                    </Box>
                  ),
                )}
              </Box>
            </CardContent>
          </Card>
        </Stack>
      </Box>
    </Box>
  );
}
