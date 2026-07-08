import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/usopApi";

import KpiTile from "../components/cards/KpiTile";
import ExposureTrendChart from "../components/charts/ExposureTrendChart";

import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  LinearProgress,
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

function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";
  if (value === "Medium") return "info";
  return "success";
}

export default function ExecutiveDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("/executive-exposure-dashboard/")
      .then((response) => setDashboard(response.data))
      .catch((err) => {
        console.error("Dashboard load failed:", err);
        setError("Could not load dashboard data.");
      });
  }, []);

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!dashboard) {
    return <CircularProgress />;
  }

  const summary = dashboard.summary;

  const exposureTrend = [
    { day: "Mon", exposure: 62 },
    { day: "Tue", exposure: 70 },
    { day: "Wed", exposure: 76 },
    { day: "Thu", exposure: 84 },
    { day: "Fri", exposure: 91 },
    { day: "Sat", exposure: 97 },
    { day: "Sun", exposure: 100 },
  ];

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
            direction={{ xs: "column", md: "row" }}
            justifyContent="space-between"
            alignItems={{ xs: "flex-start", md: "center" }}
            spacing={2}
          >
            <Box>
              <Typography variant="h4" fontWeight={900}>
                USOP Command Center
              </Typography>
              <Typography color="text.secondary">
                Unified Security Operations Platform
              </Typography>
            </Box>

            <Chip label="LIVE" color="success" sx={{ fontWeight: 800 }} />
          </Stack>
        </CardContent>
      </Card>

      <Typography variant="h5" fontWeight={800} gutterBottom>
        Security Posture
      </Typography>

      <Stack direction="row" spacing={2} sx={{ mb: 3, flexWrap: "wrap" }}>
        <KpiTile
          icon={<CrisisAlertIcon color="error" fontSize="large" />}
          label="Critical Exposure"
          value={summary.critical}
          accent="#EF4444"
        />

        <KpiTile
          icon={<WarningAmberIcon color="warning" fontSize="large" />}
          label="High Exposure"
          value={summary.high}
          accent="#F59E0B"
        />

        <KpiTile
          icon={<ReportProblemIcon color="info" fontSize="large" />}
          label="Medium Exposure"
          value={summary.medium}
          accent="#38BDF8"
        />

        <KpiTile
          icon={<CheckCircleIcon color="success" fontSize="large" />}
          label="Low Exposure"
          value={summary.low}
          accent="#22C55E"
        />

        <KpiTile
          icon={<PeopleAltIcon color="primary" fontSize="large" />}
          label="Total Identities"
          value={summary.total_identities}
          accent="#22D3EE"
        />
      </Stack>

      <ExposureTrendChart data={exposureTrend} />

      <Typography variant="h5" fontWeight={800} gutterBottom>
        Most Exposed Identities
      </Typography>

      {dashboard.top_risks.map((identity) => (
        <Card
          key={identity.identity_id}
          onClick={() => navigate(`/identity/${identity.identity_id}`)}
          sx={{
            mb: 2,
            cursor: "pointer",
            transition: "0.2s",
            "&:hover": {
              transform: "translateY(-2px)",
              boxShadow: 8,
              borderColor: "primary.main",
            },
          }}
        >
          <CardContent>
            <Stack
              direction={{ xs: "column", md: "row" }}
              justifyContent="space-between"
              alignItems={{ xs: "flex-start", md: "center" }}
              spacing={3}
            >
              <Box sx={{ flexGrow: 1, width: "100%" }}>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                  <Typography variant="h6" fontWeight={900}>
                    {identity.display_name}
                  </Typography>

                  <Chip
                    label={identity.exposure_rating}
                    color={severityColor(identity.exposure_rating)}
                    size="small"
                    sx={{ fontWeight: 800 }}
                  />
                </Stack>

                <Typography color="text.secondary" sx={{ mb: 2 }}>
                  {identity.primary_email}
                </Typography>

                <Typography variant="body2" color="text.secondary">
                  Exposure Score
                </Typography>

                <Stack direction="row" alignItems="center" spacing={2}>
                  <Box sx={{ flexGrow: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min(identity.exposure_score, 100)}
                      color={severityColor(identity.exposure_rating)}
                      sx={{ height: 10, borderRadius: 10 }}
                    />
                  </Box>

                  <Typography fontWeight={900}>{identity.exposure_score}</Typography>
                </Stack>
              </Box>

              <Stack spacing={1} sx={{ minWidth: 210 }}>
                <Typography>
                  Risk: <strong>{identity.risk_score}</strong>
                </Typography>

                <Typography>
                  Recommendations: <strong>{identity.recommendation_count}</strong>
                </Typography>

                <Typography>
                  Policy Violations: <strong>{identity.policy_violations}</strong>
                </Typography>

                <Typography color="primary.main" fontWeight={800}>
                  Open Analyst Workspace →
                </Typography>
              </Stack>
            </Stack>
          </CardContent>
        </Card>
      ))}

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
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
              <TimelineIcon color="primary" />
              <Typography variant="h5" fontWeight={800}>
                Recent Activity
              </Typography>
            </Stack>

            <Stack spacing={2}>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography fontWeight={700}>Policy Violation</Typography>
                  <Typography color="text.secondary" variant="body2">
                    Privileged Accounts Require MFA
                  </Typography>
                </Box>
                <Chip label="Critical" color="error" size="small" />
              </Stack>

              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography fontWeight={700}>Identity Risk Analysis</Typography>
                  <Typography color="text.secondary" variant="body2">
                    Exposure recalculated
                  </Typography>
                </Box>
                <Typography color="text.secondary" variant="body2">
                  2 min ago
                </Typography>
              </Stack>

              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography fontWeight={700}>Entra Synchronization</Typography>
                  <Typography color="text.secondary" variant="body2">
                    Connector completed successfully
                  </Typography>
                </Box>
                <Chip label="Healthy" color="success" size="small" />
              </Stack>
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
              <CloudDoneIcon color="success" />
              <Typography variant="h5" fontWeight={800}>
                Connector Health
              </Typography>
            </Stack>

            <Stack spacing={1.5}>
              {["Entra ID", "Azure", "AWS", "Okta", "GitHub"].map((connector) => (
                <Stack
                  key={connector}
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography>{connector}</Typography>
                  <Chip label="Healthy" color="success" size="small" />
                </Stack>
              ))}
            </Stack>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}