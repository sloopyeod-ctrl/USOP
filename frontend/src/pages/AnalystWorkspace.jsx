import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/usopApi";

import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";

function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";
  if (value === "Medium") return "info";
  return "success";
}

export default function AnalystWorkspace() {
  const { identityId } = useParams();

  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get(`/identity-intelligence/${identityId}`)
      .then((response) => setData(response.data))
      .catch((err) => {
        console.error(err);
        setError("Could not load analyst workspace.");
      });
  }, [identityId]);

  if (error) return <Alert severity="error">{error}</Alert>;
  if (!data) return <CircularProgress />;

  const { identity, risk, exposure, access, recommendations, timeline } = data;

  const privilegedAccounts = access.accounts.filter(
    (account) => account.privilege_level === "Privileged"
  );

  const missingMfa = access.accounts.filter(
    (account) => !account.mfa_enabled
  );

  const latestTimeline = timeline.slice(0, 6);
  const topRecommendations = recommendations.slice(0, 5);

  return (
    <Box>
      <Card
        sx={{
          mb: 3,
          background:
            "linear-gradient(135deg, #111827 0%, #0B1220 60%, #7F1D1D 100%)",
          border: "1px solid #7F1D1D",
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
                Analyst Workspace
              </Typography>

              <Typography variant="h6" color="text.secondary">
                {identity.display_name} • {identity.primary_email}
              </Typography>
            </Box>

            <Chip
              label={`${exposure.rating} Exposure`}
              color={severityColor(exposure.rating)}
              sx={{ fontWeight: 900 }}
            />
          </Stack>
        </CardContent>
      </Card>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            lg: "1.1fr 1fr 1fr",
          },
          gap: 3,
          mb: 3,
        }}
      >
        <Card>
          <CardContent>
            <Typography variant="h5" fontWeight={800}>
              Mission Status
            </Typography>

            <Typography variant="h3" fontWeight={900} color="error.main" sx={{ mt: 2 }}>
              {exposure.score}
            </Typography>

            <Typography color="text.secondary">Exposure Score</Typography>

            <LinearProgress
              variant="determinate"
              value={Math.min(exposure.score, 100)}
              color={severityColor(exposure.rating)}
              sx={{ mt: 2, height: 12, borderRadius: 10 }}
            />

            <Typography sx={{ mt: 2 }} fontWeight={700}>
              Immediate Action Required
            </Typography>

            <Typography color="text.secondary">
              {missingMfa.length} MFA gaps • {privilegedAccounts.length} privileged accounts
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h5" fontWeight={800}>
              Risk Summary
            </Typography>

            <Typography variant="h3" fontWeight={900} sx={{ mt: 2 }}>
              {risk.score}
            </Typography>

            <Typography color="text.secondary">{risk.level} Risk</Typography>

            <Divider sx={{ my: 2 }} />

            <Typography>Findings: {risk.findings.length}</Typography>
            <Typography>Accounts: {access.accounts.length}</Typography>
            <Typography>Groups: {access.groups.length}</Typography>
            <Typography>Roles: {access.roles.length}</Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h5" fontWeight={800}>
              Remediation Impact
            </Typography>

            <Typography variant="h3" fontWeight={900} color="success.main" sx={{ mt: 2 }}>
              {topRecommendations.reduce(
                (total, rec) => total + rec.risk_reduction,
                0
              )}
            </Typography>

            <Typography color="text.secondary">
              Estimated risk reduction
            </Typography>

            <Divider sx={{ my: 2 }} />

            <Typography>
              Actions: {topRecommendations.length}
            </Typography>

            <Typography>
              Est. effort: {topRecommendations.length * 5}–{topRecommendations.length * 15} min
            </Typography>
          </CardContent>
        </Card>
      </Box>

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
        <Card>
          <CardContent>
            <Typography variant="h5" fontWeight={800} gutterBottom>
              Immediate Actions
            </Typography>

            <Stack spacing={2}>
              {topRecommendations.map((rec, index) => (
                <Box key={`${rec.title}-${index}`}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Chip label={`P${rec.priority}`} size="small" color="primary" />
                    <Chip
                      label={rec.severity}
                      size="small"
                      color={severityColor(rec.severity)}
                    />
                    <Typography fontWeight={800}>{rec.title}</Typography>
                  </Stack>

                  <Typography color="text.secondary" sx={{ mt: 1 }}>
                    {rec.description}
                  </Typography>

                  <Typography variant="body2">
                    Risk reduction: {rec.risk_reduction} • Effort: {rec.estimated_effort}
                  </Typography>

                  <Divider sx={{ mt: 2 }} />
                </Box>
              ))}
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h5" fontWeight={800} gutterBottom>
              Recent Activity
            </Typography>

            <Stack spacing={2}>
              {latestTimeline.map((event, index) => (
                <Box key={`${event.event_type}-${index}`}>
                  <Typography fontWeight={800}>{event.event_type}</Typography>
                  <Typography color="text.secondary">{event.message}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {new Date(event.timestamp).toLocaleString()}
                  </Typography>
                  <Divider sx={{ mt: 2 }} />
                </Box>
              ))}
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h5" fontWeight={800} gutterBottom>
              Accounts
            </Typography>

            <Stack spacing={2}>
              {access.accounts.map((account) => (
                <Box key={account.id}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography fontWeight={800}>{account.username}</Typography>

                    {account.privilege_level === "Privileged" && (
                      <Chip label="Privileged" size="small" color="error" />
                    )}

                    {!account.mfa_enabled && (
                      <Chip label="No MFA" size="small" color="warning" />
                    )}
                  </Stack>

                  <Typography color="text.secondary">
                    {account.system_name} • {account.account_type} • {account.status}
                  </Typography>

                  <Divider sx={{ mt: 2 }} />
                </Box>
              ))}
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h5" fontWeight={800} gutterBottom>
              Exposure Drivers
            </Typography>

            {Object.entries(exposure.breakdown).map(([key, value]) => (
              <Box key={key} sx={{ mb: 2 }}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography sx={{ textTransform: "capitalize" }}>
                    {key.replaceAll("_", " ")}
                  </Typography>
                  <Typography fontWeight={800}>{value}</Typography>
                </Stack>

                <LinearProgress
                  variant="determinate"
                  value={Math.min(value, 100)}
                  sx={{ mt: 1, height: 8, borderRadius: 10 }}
                />
              </Box>
            ))}
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}