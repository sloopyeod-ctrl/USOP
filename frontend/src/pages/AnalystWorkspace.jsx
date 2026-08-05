import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Alert,
  Box,
  CircularProgress,
} from "@mui/material";

import {
  useParams,
} from "react-router-dom";

import api from "../api/usopApi";
import useWorkspaceSynchronization from
  "../hooks/useWorkspaceSynchronization";
import useOrganizationContext from
  "../hooks/useOrganizationContext";
import useWorkspaceState from
  "../hooks/useWorkspaceState";

import WorkspaceHeader from
  "../components/workspace/WorkspaceHeader";
import OrganizationContextBanner from
  "../components/workspace/OrganizationContextBanner";
import OperationalPulse from
  "../components/workspace/OperationalPulse";
import {
  DecisionWorkspace,
} from "../components/decision";
import MissionStatusCard from
  "../components/workspace/MissionStatusCard";
import RiskSummaryCard from
  "../components/workspace/RiskSummaryCard";
import RemediationImpactCard from
  "../components/workspace/RemediationImpactCard";
import AnimatedRiskMetrics from
  "../components/workspace/AnimatedRiskMetrics";

import IdentityGraphPanel from
  "../components/workspace/IdentityGraphPanel";
import MissionContextPanel from
  "../components/workspace/MissionContextPanel";
import ImmediateActionsPanel from
  "../components/workspace/ImmediateActionsPanel";
import {
  OperationalTimelinePanel,
} from "../components/timeline";
import AttackSimulationPanel from
  "../components/workspace/AttackSimulationPanel";

import DecisionRenderer from
  "../intelligence/DecisionRenderer";

import {
  applyGraphAnimationMetadata,
  GRAPH_ANIMATION_MODES,
} from "../services/graphAnimationService";
import {
  WORKSPACE_REFRESH_REASONS,
} from "../services/workspaceSynchronizationService";


export default function AnalystWorkspace() {
  const { identityId } = useParams();

  const {
    activeOrganization,
    activeOrganizationId,
    isLoadingOrganizations,
    organizationError,
  } = useOrganizationContext();

  const workspace = useWorkspaceState();

  const {
    synchronization,
    refresh: synchronizeWorkspace,
  } = useWorkspaceSynchronization();

  const [data, setData] = useState(null);

  const [
    timelineRefreshKey,
    setTimelineRefreshKey,
  ] = useState(0);

  const [
    attackPath,
    setAttackPath,
  ] = useState(null);

  const [error, setError] =
    useState(null);

  const selectedNode =
    workspace.selection.node;

  const selectedPath =
    workspace.selection.path;

  const simulationResult =
    workspace.simulation.result;

  const isSimulating =
    workspace.simulation.running;

  const activeGraph =
    workspace.graph.current;

  const decisionIntelligence =
    workspace.decision.intelligence;


  function applyWorkspaceData(
    workspaceData,
  ) {
    if (!workspaceData) {
      return;
    }

    const {
      intelligence,
      attack_path: refreshedAttackPath,
    } = workspaceData;

    setError(null);
    setData(intelligence);
    setAttackPath(
      refreshedAttackPath,
    );

    workspace.setBaselineGraph(
      refreshedAttackPath,
    );

    const rankedPaths =
      refreshedAttackPath
        ?.summary
        ?.ranked_paths
      || [];

    if (rankedPaths.length) {
      workspace.selectPath(
        rankedPaths[0],
      );
    }
  }


  useEffect(() => {
    if (
      !identityId
      || !activeOrganizationId
    ) {
      return undefined;
    }

    let isCurrent = true;

    localStorage.setItem(
      "usop.activeInvestigationIdentityId",
      identityId,
    );

    synchronizeWorkspace({
      identityId,
      organizationId:
        activeOrganizationId,
      reason:
        WORKSPACE_REFRESH_REASONS
          .WORKSPACE_LOADED,
    })
      .then((workspaceData) => {
        if (!isCurrent) {
          return;
        }

        applyWorkspaceData(
          workspaceData,
        );
      })
      .catch((requestError) => {
        if (!isCurrent) {
          return;
        }

        console.error(requestError);

        setError(
          "Unable to load workspace.",
        );
      });

    return () => {
      isCurrent = false;
    };

    // Workspace actions are intentionally excluded.
    // Including the state-backed workspace object would
    // refetch intelligence after graph interactions.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    identityId,
    activeOrganizationId,
  ]);


  const animatedGraph = useMemo(() => {
    if (!activeGraph) {
      return null;
    }

    const mode = simulationResult
      ? GRAPH_ANIMATION_MODES.SIMULATION
      : GRAPH_ANIMATION_MODES.IDLE;

    return {
      ...activeGraph,
      nodes: applyGraphAnimationMetadata(
        activeGraph.nodes || [],
        mode,
      ),
      animationMode: mode,
    };
  }, [
    activeGraph,
    simulationResult,
  ]);


  async function runSimulation() {
    if (!selectedPath) {
      return;
    }

    const accountStep =
      selectedPath.steps.find(
        (step) =>
          step.node_type === "account",
      );

    if (!accountStep) {
      return;
    }

    const actions = [
      {
        type: "enable_mfa",
        account_id: accountStep.node_id,
      },
    ];

    workspace.beginSimulation(actions);

    try {
      const response = await api.post(
        "/attack-path/simulate",
        {
          identity_id: identityId,
          actions,
        },
      );

      workspace.completeSimulation(
        response.data,
      );
    } catch (requestError) {
      console.error(requestError);

      workspace.failSimulation(
        "Unable to run attack path simulation.",
      );
    }
  }


  async function handleDecisionCreated() {
    if (
      !identityId
      || !activeOrganizationId
    ) {
      return;
    }

    try {
      const workspaceData =
        await synchronizeWorkspace({
          identityId,
          organizationId:
            activeOrganizationId,
          reason:
            WORKSPACE_REFRESH_REASONS
              .DECISION_RECORDED,
        });

      applyWorkspaceData(
        workspaceData,
      );

      setTimelineRefreshKey(
        (current) => current + 1,
      );
    } catch (requestError) {
      console.error(requestError);

      setError(
        "Decision recorded, but the workspace "
        + "could not be refreshed.",
      );
    }
  }


  if (!identityId) {
    return (
      <Alert severity="error">
        No identity was selected.
      </Alert>
    );
  }

  if (organizationError) {
    return (
      <Alert severity="error">
        {organizationError}
      </Alert>
    );
  }

  if (
    isLoadingOrganizations
    || !activeOrganizationId
  ) {
    return <CircularProgress />;
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (
    !data
    || !attackPath
    || !activeGraph
    || !animatedGraph
  ) {
    return <CircularProgress />;
  }


  const {
    identity,
    exposure,
    risk,
    access,
    recommendations,
    decision,
  } = data;

  const accounts =
    access?.accounts || [];

  const rankedPaths =
    attackPath?.summary?.ranked_paths
    || [];

  const riskMetrics = {
    riskScore:
      risk?.score
      || risk?.overall_score
      || exposure?.risk_score
      || 0,

    exposureScore:
      exposure?.score
      || exposure?.exposure_score
      || 0,

    confidenceScore:
      risk?.confidence
      || risk?.confidence_score
      || exposure?.confidence
      || 0,
  };


  return (
    <Box
      data-organization-id={
        activeOrganizationId
      }
      data-identity-id={identityId}
    >
      <WorkspaceHeader
        identity={identity}
        exposure={exposure}
      />

      <OperationalPulse
        synchronization={
          synchronization
        }
      />

      <OrganizationContextBanner
        activeOrganization={
          activeOrganization
        }
        isLoadingOrganizations={
          isLoadingOrganizations
        }
        organizationError={
          organizationError
        }
      />

      <Box sx={{ mb: 3 }}>
        <DecisionWorkspace
          decision={decision}
          recommendations={
            recommendations
          }
          organizationId={
            activeOrganizationId
          }
          identityId={identityId}
          showEvidence={false}
          enableDecisionWorkflow
          onDecisionCreated={
            handleDecisionCreated
          }
        />
      </Box>

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
            accounts.filter(
              (account) =>
                !account.mfa_enabled,
            ).length
          }
          privilegedAccountCount={
            accounts.filter(
              (account) =>
                account.privilege_level
                === "Privileged",
            ).length
          }
        />

        <RiskSummaryCard
          risk={risk}
          access={access}
        />

        <RemediationImpactCard
          recommendations={
            recommendations
          }
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
          attackPath={animatedGraph}
          selectedPath={selectedPath}
          selectedNode={selectedNode}
          setSelectedNode={
            workspace.selectNode
          }
          transition={
            workspace.graph.transition
          }
          animationMode={
            workspace.graph.mode
          }
        />

        <Box>
          <AnimatedRiskMetrics
            metrics={riskMetrics}
          />

          <MissionContextPanel
            node={selectedNode}
          />
        </Box>
      </Box>

      {decisionIntelligence && (
        <Box sx={{ mb: 3 }}>
          <DecisionRenderer
            decision={
              decisionIntelligence
            }
          />
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
          rankedPaths={rankedPaths}
          selectedPath={selectedPath}
          setSelectedPath={
            workspace.selectPath
          }
          runSimulation={runSimulation}
          resetSimulation={
            workspace.resetSimulation
          }
          simulationResult={
            simulationResult
          }
          isSimulating={isSimulating}
        />

        <ImmediateActionsPanel
          recommendations={
            recommendations
          }
          selectedNode={selectedNode}
        />

        <OperationalTimelinePanel
          organizationId={
            activeOrganizationId
          }
          identityId={identityId}
          refreshKey={
            timelineRefreshKey
          }
        />
      </Box>
    </Box>
  );
}
