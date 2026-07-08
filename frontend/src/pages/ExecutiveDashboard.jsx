import { useEffect, useState } from "react";
import api from "../api/usopApi";

import {
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Box,
  Alert,
  Stack,
} from "@mui/material";

export default function ExecutiveDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get("/executive-exposure-dashboard/")
      .then((response) => {
        console.log("Dashboard data:", response.data);
        setDashboard(response.data);
      })
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

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Executive Exposure Dashboard
      </Typography>

      <Stack direction="row" spacing={3} sx={{ mb: 4, flexWrap: "wrap" }}>
        <Card sx={{ minWidth: 220 }}>
          <CardContent>
            <Typography variant="h3" color="error.main">
              {summary.critical}
            </Typography>
            <Typography color="text.secondary">Critical Identities</Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 220 }}>
          <CardContent>
            <Typography variant="h3">
              {summary.high}
            </Typography>
            <Typography color="text.secondary">High Exposure</Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 220 }}>
          <CardContent>
            <Typography variant="h3">
              {summary.medium}
            </Typography>
            <Typography color="text.secondary">Medium Exposure</Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 220 }}>
          <CardContent>
            <Typography variant="h3">
              {summary.low}
            </Typography>
            <Typography color="text.secondary">Low Exposure</Typography>
          </CardContent>
        </Card>
      </Stack>

      <Typography variant="h5" fontWeight={600} gutterBottom>
        Top Exposed Identities
      </Typography>

      {dashboard.top_risks.map((identity) => (
        <Card key={identity.identity_id} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6">
              {identity.display_name}
            </Typography>

            <Typography color="text.secondary">
              {identity.primary_email}
            </Typography>

            <Typography sx={{ mt: 1 }}>
              Exposure: {identity.exposure_score} — {identity.exposure_rating}
            </Typography>

            <Typography>
              Risk: {identity.risk_score} — {identity.risk_level}
            </Typography>

            <Typography>
              Recommendations: {identity.recommendation_count}
            </Typography>

            <Typography>
              Policy Violations: {identity.policy_violations}
            </Typography>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}