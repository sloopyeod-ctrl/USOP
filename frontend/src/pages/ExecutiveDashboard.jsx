import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/usopApi";

import KpiTile from "../components/cards/KpiTile";
import TopRiskCard from "../components/cards/TopRiskCard";
import ExposureTrendChart from "../components/charts/ExposureTrendChart";

import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
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

export default function ExecutiveDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("/executive-exposure-dashboard/")
      .then((response) => setDashboard(response.data))
      .catch((err) => {
        console.error(err);
        setError("Could not load dashboard data.");
      });
  }, []);

  if (error) return <Alert severity="error">{error}</Alert>;

  if (!dashboard) return <CircularProgress />;

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
            "linear-gradient(135deg,#111827 0%,#0B1220 60%,#083344 100%)",
          border: "1px solid #164E63",
        }}
      >
        <CardContent>
          <Stack
            direction={{ xs: "column", md: "row" }}
            justifyContent="space-between"
            alignItems={{ xs: "flex-start", md: "center" }}
          >
            <Box>
              <Typography variant="h4" fontWeight={900}>
                USOP Command Center
              </Typography>

              <Typography color="text.secondary">
                Unified Security Operations Platform
              </Typography>
            </Box>

            <Chip label="LIVE" color="success" />
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
        <TopRiskCard
          key={identity.identity_id}
          identity={identity}
          onClick={() => navigate(`/identity/${identity.identity_id}`)}
        />
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
              <Box>
                <Typography fontWeight={700}>
                  Policy violation detected
                </Typography>

                <Typography color="text.secondary">
                  Privileged Accounts Require MFA
                </Typography>
              </Box>

              <Box>
                <Typography fontWeight={700}>
                  Identity risk analysis completed
                </Typography>

                <Typography color="text.secondary">
                  1 critical identity identified
                </Typography>
              </Box>

              <Box>
                <Typography fontWeight={700}>
                  Synchronization completed
                </Typography>

                <Typography color="text.secondary">
                  Entra connector processed successfully
                </Typography>
              </Box>
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
              {["Entra ID", "Azure", "AWS", "Okta", "GitHub"].map(
                (connector) => (
                  <Stack
                    key={connector}
                    direction="row"
                    justifyContent="space-between"
                  >
                    <Typography>{connector}</Typography>

                    <Chip
                      label="Healthy"
                      color="success"
                      size="small"
                    />
                  </Stack>
                )
              )}
            </Stack>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}