import { useMemo } from "react";
import useAttackReplay from "../../hooks/useAttackReplay";
import GraphRenderer from "./GraphRenderer";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";

import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";

function riskColorHex(riskLevel) {
  if (riskLevel === "Critical") return "#EF4444";
  if (riskLevel === "High") return "#F97316";
  if (riskLevel === "Medium") return "#F59E0B";
  return "#22C55E";
}

function riskChipColor(riskLevel) {
  if (riskLevel === "Critical") return "error";
  if (riskLevel === "High") return "warning";
  if (riskLevel === "Medium") return "info";
  return "success";
}

function displayNodeType(type) {
  if (type === "identity") return "Identity";
  if (type === "account") return "Account";
  if (type === "group") return "Group";
  if (type === "role") return "Role";
  return "Object";
}

function getConnectedIds(edges, selectedNodeId) {
  if (!selectedNodeId) return new Set();

  const connected = new Set([selectedNodeId]);

  edges.forEach((edge) => {
    if (edge.source === selectedNodeId) connected.add(edge.target);
    if (edge.target === selectedNodeId) connected.add(edge.source);
  });

  return connected;
}

function layoutNodes(nodes) {
  const positions = {};

  const identity = nodes.find((node) => node.type === "identity");
  const accounts = nodes.filter((node) => node.type === "account");
  const groups = nodes.filter((node) => node.type === "group");
  const roles = nodes.filter((node) => node.type === "role");

  if (identity) positions[identity.id] = { x: 420, y: 20 };

  accounts.forEach((node, index) => {
    positions[node.id] = { x: index * 250, y: 210 };
  });

  groups.forEach((node, index) => {
    positions[node.id] = { x: 420 + index * 290, y: 420 };
  });

  roles.forEach((node, index) => {
    positions[node.id] = { x: 275 + index * 290, y: 620 };
  });

  return positions;
}

function buildNodes(attackNodes, attackEdges, selectedNode, activeNodes) {
  const selectedId = selectedNode?.id;
  const replayActiveSet = new Set(activeNodes);

  const connectedIds = selectedId
    ? getConnectedIds(attackEdges, selectedId)
    : new Set(attackNodes.map((node) => node.id));

  const positions = layoutNodes(attackNodes);

  return attackNodes.map((node) => {
    const isSelected = node.id === selectedId;
    const isConnected = !selectedId || connectedIds.has(node.id);
    const isReplayActive = replayActiveSet.has(node.id);

    return {
      id: node.id,
      type: "attackPathNode",
      position: positions[node.id] || { x: 420, y: 820 },
      data: {
        details: node.details,
        nodeType: displayNodeType(node.type),
        attackPathNode: node,
        isSelected,
        isConnected,
        isReplayActive,
      },
    };
  });
}

function buildEdges(attackEdges, selectedNode, activeEdges) {
  const selectedId = selectedNode?.id;
  const replayEdgeSet = new Set(activeEdges);

  return attackEdges.map((edge, index) => {
    const edgeId = `${edge.source}-${edge.target}-${index}`;
    const replayId = `${edge.source}-${edge.target}`;
    const isReplayActive = replayEdgeSet.has(replayId);

    const isConnected =
      !selectedId || edge.source === selectedId || edge.target === selectedId;

    const color = isReplayActive
      ? "#22D3EE"
      : isConnected
        ? riskColorHex(edge.risk_level)
        : "#64748B";

    return {
      id: edgeId,
      source: edge.source,
      target: edge.target,
      animated: isReplayActive || (isConnected && edge.risk_level !== "Low"),
      label: `+${edge.risk_contribution}`,
      data: edge,
      style: {
        stroke: color,
        strokeWidth: isReplayActive ? 5 : isConnected ? 4 : 1.5,
        opacity: isReplayActive || isConnected ? 1 : 0.2,
      },
      labelStyle: {
        fill: color,
        fontWeight: 900,
        fontSize: 12,
      },
      labelBgStyle: {
        fill: "#111827",
        fillOpacity: 0.95,
      },
      labelBgPadding: [6, 4],
      labelBgBorderRadius: 6,
    };
  });
}

export default function IdentityGraphPanel({
  attackPath,
  selectedPath,
  height = "62vh",
  selectedNode,
  setSelectedNode,
}) {
  const rawNodes = attackPath?.attack_path?.nodes || [];
  const rawEdges = attackPath?.attack_path?.edges || [];

  const replayPath = selectedPath || attackPath?.summary?.ranked_paths?.[0] || null;

  const { playReplay, stopReplay, activeNodes, activeEdges, isPlaying } =
    useAttackReplay(replayPath);

  const nodes = useMemo(() => {
    if (!attackPath) return [];
    return buildNodes(rawNodes, rawEdges, selectedNode, activeNodes);
  }, [attackPath, rawNodes, rawEdges, selectedNode, activeNodes]);

  const edges = useMemo(() => {
    if (!attackPath) return [];
    return buildEdges(rawEdges, selectedNode, activeEdges);
  }, [attackPath, rawEdges, selectedNode, activeEdges]);

  if (!attackPath) return <CircularProgress />;
  if (!nodes.length) {
    return <Alert severity="warning">No attack path data found.</Alert>;
  }

  return (
    <Card>
      <CardContent>
        <Stack
          direction="row"
          spacing={2}
          sx={{
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Box>
            <Typography variant="h5" fontWeight={800}>
              Attack Path Graph
            </Typography>

            <Typography color="text.secondary">
              Replaying selected path:{" "}
              {replayPath ? replayPath.name : "No ranked path available"}
            </Typography>
          </Box>

          <Stack direction="row" spacing={1} alignItems="center">
            <Button
              variant={isPlaying ? "outlined" : "contained"}
              size="small"
              startIcon={isPlaying ? <StopIcon /> : <PlayArrowIcon />}
              onClick={isPlaying ? stopReplay : playReplay}
              disabled={!replayPath}
            >
              {isPlaying ? "Stop" : "Replay Selected Path"}
            </Button>

            {replayPath && (
              <Chip
                label={`Path #${replayPath.path_rank} • ${replayPath.likelihood}%`}
                color={riskChipColor(replayPath.risk_level)}
                size="small"
              />
            )}

            <Chip
              label={`${attackPath.attack_path.risk_level} Risk`}
              color={riskChipColor(attackPath.attack_path.risk_level)}
              size="small"
            />

            <Chip
              label={`${attackPath.summary.total_nodes} Nodes`}
              color="primary"
              size="small"
            />

            <Chip
              label={`${attackPath.summary.total_edges} Edges`}
              color="secondary"
              size="small"
            />
          </Stack>
        </Stack>

        <GraphRenderer
          graphKey={attackPath.identity.id}
          nodes={nodes}
          edges={edges}
          height={height}
          selectedNode={selectedNode}
          setSelectedNode={setSelectedNode}
        />
      </CardContent>
    </Card>
  );
}