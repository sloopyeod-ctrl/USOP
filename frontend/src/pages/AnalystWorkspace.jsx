import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/usopApi";

import WorkspaceHeader from "../components/workspace/WorkspaceHeader";
import MissionStatusCard from "../components/workspace/MissionStatusCard";
import RiskSummaryCard from "../components/workspace/RiskSummaryCard";
import RemediationImpactCard from "../components/workspace/RemediationImpactCard";
import IdentityGraphPanel from "../components/workspace/IdentityGraphPanel";
import ImmediateActionsPanel from "../components/workspace/ImmediateActionsPanel";
import RecentActivityPanel from "../components/workspace/RecentActivityPanel";

import {
  Alert,
  Box,
  CircularProgress,
} from "@mui/material";

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

  const missingMfa = access.accounts.filter((account) => !account.mfa_enabled);

  const latestTimeline = timeline.slice(0, 6);
  const topRecommendations = recommendations.slice(0, 5);

  return (
    <Box>
      <WorkspaceHeader identity={identity} exposure={exposure} />

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
        <MissionStatusCard
          exposure={exposure}
          missingMfaCount={missingMfa.length}
          privilegedAccountCount={privilegedAccounts.length}
        />

        <RiskSummaryCard risk={risk} access={access} />

        <RemediationImpactCard recommendations={topRecommendations} />
      </Box>

      <Box sx={{ mb: 3 }}>
        <IdentityGraphPanel identityId={identityId} height="58vh" />
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
        <ImmediateActionsPanel recommendations={topRecommendations} />
        <RecentActivityPanel events={latestTimeline} />
      </Box>
    </Box>
  );
}