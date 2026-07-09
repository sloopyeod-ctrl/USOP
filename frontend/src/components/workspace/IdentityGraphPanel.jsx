import { useEffect, useMemo, useState } from "react";
import api from "../../api/usopApi";
import useAttackReplay from "../../hooks/useAttackReplay";

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

import {
  Background,
  Controls,
  Handle,
  Position,
  ReactFlow,
} from "@xyflow/react";

import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";

import "@xyflow/react/dist/style.css";

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

function nodeIcon(type) {
  if (type === "identity") return "👤";
  if (type === "account") return "💻";
  if (type === "group") return "👥";
  if (type === "role") return "🛡";
  return "●";
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

function AttackPathNode({ data }) {
  const node = data.attackPathNode;
  const riskColor = riskColorHex(node.risk_level);

  const glow = data.isReplayActive
    ? "0 0 0 4px rgba(34,211,238,0.35), 0 0 36px rgba(34,211,238,0.95)"
    : data.isSelected
      ? "0 0 0 3px rgba(34,211,238,0.25), 0 0 28px rgba(34,211,238,0.85)"
      : data.isConnected
        ? `0 0 20px ${riskColor}66`
        : "0 10px 25px rgba(0,0,0,0.20)";

  return (
    <Box
      sx={{
        width: 220,
        minHeight: 78,
        p: 1.2,
        borderRadius: 2,
        textAlign: "center",
        background: "#111827",
        color: "#E5E7EB",
        border:
          data.isReplayActive || data.isSelected
            ? "3px solid #22D3EE"
            : `2px solid ${riskColor}`,
        opacity: data.isConnected ? 1 : 0.35,
        transform:
          data.isReplayActive || data.isSelected ? "scale(1.05)" : "scale(1)",
        boxShadow: glow,
        transition: "all 0.2s ease-in-out",
      }}
    >
      <Handle type="target" position={Position.Top} />

      <Typography fontSize={13} fontWeight={900}>
        {nodeIcon(node.type)} {node.label}
      </Typography>

      <Typography fontSize={11} fontWeight={900} sx={{ color: riskColor, mt: 0.5 }}>
        {node.risk_level} • +{node.risk_contribution}
      </Typography>

      <Typography fontSize={10} sx={{ color: "#9CA3AF", mt: 0.5 }}>
        Criticality {node.criticality}
      </Typography>

      <Handle type="source" position={Position.Bottom} />
    </Box>
  );
}

const nodeTypes = {
  attackPathNode: AttackPathNode,
};

function layoutNodes(nodes) {
  const positions = {};

  const identity = nodes.find((node) => node.type === "identity");
  const accounts = nodes.filter((node) => node.type === "account");
  const groups = nodes.filter((node) => node.type === "group");
  const roles = nodes.filter((node) => node.type === "role");

  if (identity) {
    positions[identity.id] = { x: 420, y: 20 };
  }

  accounts.forEach((node, index) => {
    positions[node.id] = {
      x: 0 + index * 250,
      y: 210,
    };
  });

  groups.forEach((node, index) => {
    positions[node.id] = {
      x: 420 + index * 290,
      y: 420,
    };
  });

  roles.forEach((node, index) => {
    positions[node.id] = {
      x: 275 + index * 290,
      y: 620,
    };
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
    const isReplayActive = replayEdgeSet.has(edgeId);

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
  identityId,
  height = "62vh",
  selectedNode,
  setSelectedNode,
}) {
  const [attackPath, setAttackPath] = useState(null);
  const [error, setError] = useState(null);

  const rawNodes = attackPath?.attack_path?.nodes || [];
  const rawEdges = attackPath?.attack_path?.edges || [];

  const replayEdges = useMemo(
    () =>
      rawEdges.map((edge, index) => ({
        ...edge,
        id: `${edge.source}-${edge.target}-${index}`,
      })),
    [rawEdges]
  );

  const {
    playReplay,
    stopReplay,
    activeNodes,
    activeEdges,
    isPlaying,
  } = useAttackReplay(rawNodes, replayEdges);

  useEffect(() => {
    setSelectedNode(null);
    stopReplay();

    api
      .get(`/attack-path/${identityId}`)
      .then((response) => setAttackPath(response.data))
      .catch((err) => {
        console.error(err);
        setError("Unable to load attack path graph.");
      });
  }, [identityId, setSelectedNode]);

  const nodes = useMemo(() => {
    if (!attackPath) return [];

    return buildNodes(
      rawNodes,
      rawEdges,
      selectedNode,
      activeNodes
    );
  }, [attackPath, rawNodes, rawEdges, selectedNode, activeNodes]);

  const edges = useMemo(() => {
    if (!attackPath) return [];

    return buildEdges(rawEdges, selectedNode, activeEdges);
  }, [attackPath, rawEdges, selectedNode, activeEdges]);

  if (error) return <Alert severity="error">{error}</Alert>;
  if (!attackPath || !nodes.length) return <CircularProgress />;

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
              Risk-weighted identity relationships and attack-path contribution.
            </Typography>
          </Box>

          <Stack direction="row" spacing={1} alignItems="center">
            <Button
              variant={isPlaying ? "outlined" : "contained"}
              size="small"
              startIcon={isPlaying ? <StopIcon /> : <PlayArrowIcon />}
              onClick={isPlaying ? stopReplay : playReplay}
            >
              {isPlaying ? "Stop" : "Replay Attack"}
            </Button>

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

        <Box sx={{ height }}>
          <ReactFlow
            key={attackPath.identity.id}
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            defaultViewport={{ x: 50, y: 55, zoom: 0.72 }}
            minZoom={0.35}
            maxZoom={1.4}
            onNodeClick={(_, node) => setSelectedNode(node)}
            onPaneClick={() => setSelectedNode(null)}
            proOptions={{ hideAttribution: true }}
          >
            <Controls />
            <Background color="#1F2937" gap={18} />
          </ReactFlow>
        </Box>
      </CardContent>
    </Card>
  );
}