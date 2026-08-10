import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/usopApi";

import KpiTile from "../components/cards/KpiTile";
import TopRiskCard from "../components/cards/TopRiskCard";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import CrisisAlertIcon from "@mui/icons-material/CrisisAlert";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import ReportProblemIcon from "@mui/icons-material/ReportProblem";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PeopleAltIcon from "@mui/icons-material/PeopleAlt";
import TimelineIcon from "@mui/icons-material/Timeline";
import CloudDoneIcon from "@mui/icons-material/CloudDone";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";


function pluralize(
  count,
  singular,
  plural = `${singular}s`,
) {
  return count === 1
    ? singular
    : plural;
}


export default function ExecutiveDashboard() {
  const [dashboard, setDashboard] =
    useState(null);

  const [error, setError] =
    useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("/executive-exposure-dashboard/")
      .then(
        (response) =>
          setDashboard(response.data),
      )
      .catch((err) => {
        console.error(err);

        setError(
          "Could not load dashboard data.",
        );
      });
  }, []);

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (!dashboard) {
    return <CircularProgress />;
  }

  const summary = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    total_identities: 0,
    ...(dashboard.summary ?? {}),
  };

  const topRisks =
    Array.isArray(dashboard.top_risks)
      ? dashboard.top_risks
      : [];

  const highestRisk =
    topRisks[0] || null;

  const criticalCount =
    summary?.critical || 0;

  const highCount =
    summary?.high || 0;

  const totalIdentities =
    summary?.total_identities || 0;

  const attentionCount =
    criticalCount + highCount;

  const operationalHeadline =
    criticalCount > 0
      ? (
        `${criticalCount} Critical `
        + pluralize(
          criticalCount,
          "Identity",
          "Identities",
        )
        + (
          criticalCount === 1
            ? " Requires Immediate Review"
            : " Require Immediate Review"
        )
      )
      : highCount > 0
        ? (
          `${highCount} High-Exposure `
          + pluralize(
            highCount,
            "Identity",
            "Identities",
          )
          + (
            highCount === 1
              ? " Requires Review"
              : " Require Review"
          )
        )
        : "No Critical Or High-Exposure Identities Require Review";

  function openHighestRisk() {
    if (!highestRisk?.identity_id) {
      return;
    }

    navigate(
      `/identity/${highestRisk.identity_id}`,
    );
  }

  return (
    <Box>
      <Card
        sx={{
          mb: 3,
          background:
            "linear-gradient("
            + "135deg,"
            + "#111827 0%,"
            + "#0B1220 58%,"
            + "#083344 100%"
            + ")",
          border:
            "1px solid #164E63",
        }}
      >
        <CardContent
          sx={{
            p: {
              xs: 2.5,
              md: 3,
            },
          }}
        >
          <Stack spacing={2.5}>
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
              <Box>
                <Typography
                  variant="overline"
                  sx={{
                    color: "#67E8F9",
                    fontWeight: 900,
                    letterSpacing: 1.1,
                  }}
                >
                  Today&apos;s Operational Summary
                </Typography>

                <Typography
                  variant="h4"
                  fontWeight={900}
                  sx={{
                    color: "#F8FAFC",
                    mt: 0.25,
                  }}
                >
                  {operationalHeadline}
                </Typography>

                <Typography
                  sx={{
                    color: "#94A3B8",
                    mt: 0.75,
                  }}
                >
                  {totalIdentities}{" "}
                  {pluralize(
                    totalIdentities,
                    "identity",
                    "identities",
                  )}{" "}
                  monitored across the active organization.
                </Typography>
              </Box>

              <Chip
                label="BETA"
                color="info"
                variant="outlined"
                sx={{
                  color: "#E2E8F0",
                  borderColor:
                    "rgba(34, 211, 238, 0.45)",
                  fontWeight: 900,
                }}
              />
            </Stack>

            <Divider
              sx={{
                borderColor:
                  "rgba(148, 163, 184, 0.18)",
              }}
            />

            <Stack
              direction={{
                xs: "column",
                md: "row",
              }}
              spacing={2}
              justifyContent="space-between"
              alignItems={{
                xs: "flex-start",
                md: "center",
              }}
            >
              <Stack
                direction="row"
                spacing={3}
                flexWrap="wrap"
                useFlexGap
              >
                <Box>
                  <Typography
                    variant="caption"
                    sx={{
                      color: "#94A3B8",
                      fontWeight: 800,
                      textTransform:
                        "uppercase",
                      letterSpacing: 0.7,
                    }}
                  >
                    Needs Attention
                  </Typography>

                  <Typography
                    variant="h5"
                    sx={{
                      color: "#F8FAFC",
                      fontWeight: 900,
                    }}
                  >
                    {attentionCount}
                  </Typography>
                </Box>

                <Box>
                  <Typography
                    variant="caption"
                    sx={{
                      color: "#94A3B8",
                      fontWeight: 800,
                      textTransform:
                        "uppercase",
                      letterSpacing: 0.7,
                    }}
                  >
                    Critical
                  </Typography>

                  <Typography
                    variant="h5"
                    sx={{
                      color: "#F87171",
                      fontWeight: 900,
                    }}
                  >
                    {criticalCount}
                  </Typography>
                </Box>

                <Box>
                  <Typography
                    variant="caption"
                    sx={{
                      color: "#94A3B8",
                      fontWeight: 800,
                      textTransform:
                        "uppercase",
                      letterSpacing: 0.7,
                    }}
                  >
                    High
                  </Typography>

                  <Typography
                    variant="h5"
                    sx={{
                      color: "#FBBF24",
                      fontWeight: 900,
                    }}
                  >
                    {highCount}
                  </Typography>
                </Box>
              </Stack>

              {highestRisk?.identity_id && (
                <Button
                  variant="contained"
                  endIcon={
                    <ArrowForwardIcon />
                  }
                  onClick={openHighestRisk}
                >
                  Open Investigation
                </Button>
              )}
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      <Typography
        variant="h5"
        fontWeight={800}
        gutterBottom
      >
        Security Posture
      </Typography>

      <Stack
        direction="row"
        spacing={2}
        sx={{
          mb: 3,
          flexWrap: "wrap",
        }}
      >
        <KpiTile
          icon={
            <CrisisAlertIcon
              color="error"
              fontSize="large"
            />
          }
          label="Critical Exposure"
          value={summary.critical}
          accent="#EF4444"
        />

        <KpiTile
          icon={
            <WarningAmberIcon
              color="warning"
              fontSize="large"
            />
          }
          label="High Exposure"
          value={summary.high}
          accent="#F59E0B"
        />

        <KpiTile
          icon={
            <ReportProblemIcon
              color="info"
              fontSize="large"
            />
          }
          label="Medium Exposure"
          value={summary.medium}
          accent="#38BDF8"
        />

        <KpiTile
          icon={
            <CheckCircleIcon
              color="success"
              fontSize="large"
            />
          }
          label="Low Exposure"
          value={summary.low}
          accent="#22C55E"
        />

        <KpiTile
          icon={
            <PeopleAltIcon
              color="primary"
              fontSize="large"
            />
          }
          label="Total Identities"
          value={summary.total_identities}
          accent="#22D3EE"
        />
      </Stack>

      <Typography
        variant="h5"
        fontWeight={800}
        gutterBottom
      >
        Most Exposed Identities
      </Typography>

      {topRisks.length > 0
        ? topRisks.map((identity) => (
          <TopRiskCard
            key={identity.identity_id}
            identity={identity}
            onClick={() =>
              navigate(
                `/identity/${identity.identity_id}`,
              )
            }
          />
        ))
        : (
          <Alert
            severity="success"
            sx={{ mb: 3 }}
          >
            No exposed identities require review.
          </Alert>
        )}

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
            sx={{ mb: 1 }}
          >
            <TimelineIcon color="primary" />

            <Typography
              variant="h5"
              fontWeight={800}
            >
              Exposure Trend
            </Typography>
          </Stack>

          <Typography
            color="text.secondary"
          >
            Historical exposure direction will
            appear here after sufficient
            operational snapshots have been
            collected. USOP does not display
            synthetic trend data in the beta
            experience.
          </Typography>
        </CardContent>
      </Card>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            lg: "1fr 1fr",
          },
          gap: 3,
          mt: 3,
        }}
      >
        <Card>
          <CardContent>
            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              sx={{ mb: 2 }}
            >
              <CrisisAlertIcon
                color={
                  criticalCount > 0
                    ? "error"
                    : "success"
                }
              />

              <Typography
                variant="h5"
                fontWeight={800}
              >
                Operational Priorities
              </Typography>
            </Stack>

            <Stack spacing={2}>
              <Box>
                <Typography
                  fontWeight={700}
                >
                  Critical exposure
                </Typography>

                <Typography
                  color="text.secondary"
                >
                  {criticalCount}{" "}
                  {pluralize(
                    criticalCount,
                    "identity",
                    "identities",
                  )}{" "}
                  currently classified as critical.
                </Typography>
              </Box>

              <Box>
                <Typography
                  fontWeight={700}
                >
                  High exposure
                </Typography>

                <Typography
                  color="text.secondary"
                >
                  {highCount}{" "}
                  {pluralize(
                    highCount,
                    "identity",
                    "identities",
                  )}{" "}
                  currently classified as high.
                </Typography>
              </Box>

              <Box>
                <Typography
                  fontWeight={700}
                >
                  Monitored population
                </Typography>

                <Typography
                  color="text.secondary"
                >
                  {totalIdentities} total{" "}
                  {pluralize(
                    totalIdentities,
                    "identity",
                    "identities",
                  )}{" "}
                  represented in the current
                  operational view.
                </Typography>
              </Box>
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              sx={{ mb: 2 }}
            >
              <CloudDoneIcon color="success" />

              <Typography
                variant="h5"
                fontWeight={800}
              >
                Connector Coverage
              </Typography>
            </Stack>

            <Stack spacing={1.5}>
              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="center"
                spacing={2}
              >
                <Typography>
                  Microsoft Entra ID
                </Typography>

                <Chip
                  label="Beta Scope"
                  color="success"
                  size="small"
                />
              </Stack>

              <Divider />

              <Box>
                <Typography
                  fontWeight={700}
                >
                  Additional providers
                </Typography>

                <Typography
                  color="text.secondary"
                >
                  AWS, Google Cloud, Okta, and
                  additional ingestion sources
                  are planned for the broader V1
                  provider catalog.
                </Typography>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
