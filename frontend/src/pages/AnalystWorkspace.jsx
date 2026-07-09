import { useEffect, useState } from "react";
import { Alert, Box, CircularProgress } from "@mui/material";
import { useParams } from "react-router-dom";

import api from "../api/usopApi";

import WorkspaceHeader from "../components/workspace/WorkspaceHeader";
import MissionStatusCard from "../components/workspace/MissionStatusCard";
import RiskSummaryCard from "../components/workspace/RiskSummaryCard";
import RemediationImpactCard from "../components/workspace/RemediationImpactCard";

import IdentityGraphPanel from "../components/workspace/IdentityGraphPanel";
import MissionContextPanel from "../components/workspace/MissionContextPanel";
import ImmediateActionsPanel from "../components/workspace/ImmediateActionsPanel";
import RecentActivityPanel from "../components/workspace/RecentActivityPanel";
import AttackSimulationPanel from "../components/workspace/AttackSimulationPanel";

export default function AnalystWorkspace() {
  const { identityId } = useParams();

  const [data, setData] = useState(null);
  const [attackPath, setAttackPath] = useState(null);

  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedPath, setSelectedPath] = useState(null);

  const [simulationResult, setSimulationResult] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get(`/identity-intelligence/${identityId}`),
      api.get(`/attack-path/${identityId}`),
    ])
      .then(([intel, attack]) => {
        setData(intel.data);
        setAttackPath(attack.data);

        if (attack.data.summary.ranked_paths.length) {
          setSelectedPath(attack.data.summary.ranked_paths[0]);
        }
      })
      .catch((err) => {
        console.error(err);
        setError("Unable to load workspace.");
      });
  }, [identityId]);

  async function runSimulation() {
    if (!selectedPath) return;

    const accountStep = selectedPath.steps.find(
      (step) => step.node_type === "account"
    );

    if (!accountStep) return;

    setIsSimulating(true);

    try {
      const response = await api.post("/attack-path/simulate", {
        identity_id: identityId,
        actions: [
          {
            type: "enable_mfa",
            account_id: accountStep.node_id,
          },
        ],
      });

      setSimulationResult(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSimulating(false);
    }
  }

  if (error) return <Alert severity="error">{error}</Alert>;

  if (!data || !attackPath) return <CircularProgress />;

  const { identity, exposure, risk, access, recommendations, timeline } = data;

  return (
    <Box>

      <WorkspaceHeader
        identity={identity}
        exposure={exposure}
      />

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            lg: "1fr 1fr 1fr",
          },
          gap: 3,
          mb: 3,
        }}
      >
        <MissionStatusCard
          exposure={exposure}
          missingMfaCount={
            access.accounts.filter((a) => !a.mfa_enabled).length
          }
          privilegedAccountCount={
            access.accounts.filter(
              (a) => a.privilege_level === "Privileged"
            ).length
          }
        />

        <RiskSummaryCard
          risk={risk}
          access={access}
        />

        <RemediationImpactCard
          recommendations={recommendations}
        />
      </Box>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            xl: "2fr 360px",
          },
          gap: 3,
          mb: 3,
        }}
      >
        <IdentityGraphPanel
          identityId={identityId}
          selectedNode={selectedNode}
          setSelectedNode={setSelectedNode}
        />

        <MissionContextPanel
          node={selectedNode}
        />
      </Box>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            lg: "420px 1fr 1fr",
          },
          gap: 3,
        }}
      >
        <AttackSimulationPanel
          rankedPaths={attackPath.summary.ranked_paths}
          selectedPath={selectedPath}
          setSelectedPath={setSelectedPath}
          runSimulation={runSimulation}
          simulationResult={simulationResult}
          isSimulating={isSimulating}
        />

        <ImmediateActionsPanel
          recommendations={recommendations}
          selectedNode={selectedNode}
        />

        <RecentActivityPanel
          events={timeline}
          selectedNode={selectedNode}
        />
      </Box>

    </Box>
  );
}