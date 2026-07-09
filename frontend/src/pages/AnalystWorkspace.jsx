import { useEffect, useMemo, useState } from "react";
import { Alert, Box, CircularProgress } from "@mui/material";
import { useParams } from "react-router-dom";

import api from "../api/usopApi";
import useWorkspaceState from "../hooks/useWorkspaceState";

import WorkspaceHeader from "../components/workspace/WorkspaceHeader";
import MissionStatusCard from "../components/workspace/MissionStatusCard";
import RiskSummaryCard from "../components/workspace/RiskSummaryCard";
import RemediationImpactCard from "../components/workspace/RemediationImpactCard";
import AnimatedRiskMetrics from "../components/workspace/AnimatedRiskMetrics";

import IdentityGraphPanel from "../components/workspace/IdentityGraphPanel";
import MissionContextPanel from "../components/workspace/MissionContextPanel";
import ImmediateActionsPanel from "../components/workspace/ImmediateActionsPanel";
import RecentActivityPanel from "../components/workspace/RecentActivityPanel";
import AttackSimulationPanel from "../components/workspace/AttackSimulationPanel";

import DecisionRenderer from "../intelligence/DecisionRenderer";

import {
  applyGraphAnimationMetadata,
  GRAPH_ANIMATION_MODES,
} from "../services/graphAnimationService";

export default function AnalystWorkspace() {
  const { identityId } = useParams();

  const workspace = useWorkspaceState();

  const [data, setData] = useState(null);
  const [attackPath, setAttackPath] = useState(null);
  const [error, setError] = useState(null);

  const selectedNode = workspace.selection.node;
  const selectedPath = workspace.selection.path;
  const simulationResult = workspace.simulation.result;
  const isSimulating = workspace.simulation.running;
  const activeGraph = workspace.graph.current;
  const decisionIntelligence = workspace.decision.intelligence;

  useEffect(() => {
    Promise.all([
      api.get(`/identity-intelligence/${identityId}`),
      api.get(`/attack-path/${identityId}`),
    ])
      .then(([intel, attack]) => {
        setData(intel.data);
        setAttackPath(attack.data);
        workspace.setBaselineGraph(attack.data);

        if (attack.data.summary.ranked_paths.length) {
          workspace.selectPath(attack.data.summary.ranked_paths[0]);
        }
      })
      .catch((err) => {
        console.error(err);
        setError("Unable to load workspace.");
      });
  }, [identityId]);

  const animatedGraph = useMemo(() => {
    if (!activeGraph) return null;

    const mode = simulationResult
      ? GRAPH_ANIMATION_MODES.SIMULATION
      : GRAPH_ANIMATION_MODES.IDLE;

    return {
      ...activeGraph,
      nodes: applyGraphAnimationMetadata(activeGraph.nodes || [], mode),
      animationMode: mode,
    };
  }, [activeGraph, simulationResult]);

  async function runSimulation() {
    if (!selectedPath) return;

    const accountStep = selectedPath.steps.find(
      (step) => step.node_type === "account"
    );

    if (!accountStep) return;

    const actions = [
      {
        type: "enable_mfa",
        account_id: accountStep.node_id,
      },
    ];

    workspace.beginSimulation(actions);

    try {
      const response = await api.post("/attack-path/simulate", {
        identity_id: identityId,
        actions,
      });

      workspace.completeSimulation(response.data);
    } catch (err) {
      console.error(err);
      workspace.failSimulation("Unable to run attack path simulation.");
    }
  }

  if (error) return <Alert severity="error">{error}</Alert>;

  if (!data || !attackPath || !activeGraph || !animatedGraph) {
    return <CircularProgress />;
  }

  const { identity, exposure, risk, access, recommendations, timeline } = data;

  const riskMetrics = {
    riskScore: risk?.score || risk?.overall_score || exposure?.risk_score || 0,
    exposureScore: exposure?.score || exposure?.exposure_score || 0,
    confidenceScore:
      risk?.confidence || risk?.confidence_score || exposure?.confidence || 0,
  };

  return (
    <Box>
      <WorkspaceHeader identity={identity} exposure={exposure} />

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
          missingMfaCount={access.accounts.filter((a) => !a.mfa_enabled).length}
          privilegedAccountCount={
            access.accounts.filter((a) => a.privilege_level === "Privileged")
              .length
          }
        />

        <RiskSummaryCard risk={risk} access={access} />

        <RemediationImpactCard recommendations={recommendations} />
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
          attackPath={animatedGraph}
          selectedPath={selectedPath}
          selectedNode={selectedNode}
          setSelectedNode={workspace.selectNode}
        />

        <Box>
          <AnimatedRiskMetrics metrics={riskMetrics} />
          <MissionContextPanel node={selectedNode} />
        </Box>
      </Box>

      {decisionIntelligence && (
        <Box sx={{ mb: 3 }}>
          <DecisionRenderer decision={decisionIntelligence} />
        </Box>
      )}

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
          setSelectedPath={workspace.selectPath}
          runSimulation={runSimulation}
          simulationResult={simulationResult}
          isSimulating={isSimulating}
        />

        <ImmediateActionsPanel
          recommendations={recommendations}
          selectedNode={selectedNode}
        />

        <RecentActivityPanel events={timeline} selectedNode={selectedNode} />
      </Box>
    </Box>
  );
}