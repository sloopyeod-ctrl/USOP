import { useEffect, useMemo, useState } from "react";
import api from "../../api/usopApi";

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

import { ReactFlow, Background, Controls, MiniMap } from "@xyflow/react";

import "@xyflow/react/dist/style.css";

const NODE_STYLES = {
  identity: {
    background: "#0E7490",
    color: "#E0F2FE",
    border: "2px solid #22D3EE",
  },
  account: {
    background: "#14532D",
    color: "#DCFCE7",
    border: "2px solid #22C55E",
  },
  privilegedAccount: {
    background: "#7F1D1D",
    color: "#FEE2E2",
    border: "2px solid #EF4444",
  },
  group: {
    background: "#78350F",
    color: "#FEF3C7",
    border: "2px solid #F59E0B",
  },
  role: {
    background: "#4C1D95",
    color: "#EDE9FE",
    border: "2px solid #A78BFA",
  },
};

function baseNodeStyle(type) {
  return {
    ...NODE_STYLES[type],
    borderRadius: 14,
    padding: 12,
    fontWeight: 800,
    width: 190,
    textAlign: "center",
    boxShadow: "0 10px 25px rgba(0,0,0,0.35)",
    transition: "all 0.2s ease-in-out",
  };
}

function edgeStyle(color = "#22D3EE") {
  return {
    stroke: color,
    strokeWidth: 2.5,
  };
}

function getConnectedIds(edges, selectedNodeId) {
  if (!selectedNodeId) return new Set();

  const connected = new Set([selectedNodeId]);

  edges.forEach((edge) => {
    if (edge.source === selectedNodeId) {
      connected.add(edge.target);
    }

    if (edge.target === selectedNodeId) {
      connected.add(edge.source);
    }
  });

  return connected;
}

export default function IdentityGraphPanel({
  identityId,
  height = "62vh",
  selectedNode,
  setSelectedNode,
}) {
  const [graph, setGraph] = useState(null);
  const [baseNodes, setBaseNodes] = useState([]);
  const [baseEdges, setBaseEdges] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get(`/identity-graph/${identityId}`)
      .then((response) => {
        setGraph(response.data);
        buildGraph(response.data);
      })
      .catch((err) => {
        console.error(err);
        setError("Unable to load identity graph.");
      });
  }, [identityId]);

  function buildGraph(data) {
    const graphNodes = [];
    const graphEdges = [];

    graphNodes.push({
      id: "identity",
      position: { x: 520, y: 20 },
      data: {
        label: `👤 ${data.identity.display_name}`,
        details: data.identity,
        nodeType: "Identity",
        styleType: "identity",
      },
      type: "input",
      style: baseNodeStyle("identity"),
    });

    data.accounts.forEach((account, index) => {
      const isPrivileged = account.privilege_level === "Privileged";
      const styleType = isPrivileged ? "privilegedAccount" : "account";

      graphNodes.push({
        id: account.id,
        position: { x: 120 + index * 245, y: 210 },
        data: {
          label: `${isPrivileged ? "🚨" : "💻"} ${account.username}`,
          details: account,
          nodeType: "Account",
          styleType,
        },
        style: baseNodeStyle(styleType),
      });

      graphEdges.push({
        id: `identity-${account.id}`,
        source: "identity",
        target: account.id,
        animated: isPrivileged,
        data: {
          color: isPrivileged ? "#EF4444" : "#22C55E",
        },
        style: edgeStyle(isPrivileged ? "#EF4444" : "#22C55E"),
      });
    });

    data.groups.forEach((group, index) => {
      graphNodes.push({
        id: group.group_id,
        position: { x: 260 + index * 320, y: 430 },
        data: {
          label: `👥 ${group.group_name}`,
          details: group,
          nodeType: "Group",
          styleType: "group",
        },
        style: baseNodeStyle("group"),
      });

      graphEdges.push({
        id: `${group.account_id}-${group.group_id}`,
        source: group.account_id,
        target: group.group_id,
        animated: group.privilege_level === "Privileged",
        data: {
          color: "#F59E0B",
        },
        style: edgeStyle("#F59E0B"),
      });
    });

    data.roles.forEach((role, index) => {
      graphNodes.push({
        id: role.role_id,
        position: { x: 620 + index * 260, y: 650 },
        data: {
          label: `🛡 ${role.role_name}`,
          details: role,
          nodeType: "Role",
          styleType: "role",
        },
        style: baseNodeStyle("role"),
      });

      graphEdges.push({
        id: `${role.account_id}-${role.role_id}`,
        source: role.account_id,
        target: role.role_id,
        animated: role.privilege_level === "Privileged",
        data: {
          color: "#A78BFA",
        },
        style: edgeStyle("#A78BFA"),
      });
    });

    setBaseNodes(graphNodes);
    setBaseEdges(graphEdges);
  }

  const highlightedNodes = useMemo(() => {
    const selectedId = selectedNode?.id;
    const connectedIds = getConnectedIds(baseEdges, selectedId);

    if (!selectedId) return baseNodes;

    return baseNodes.map((node) => {
      const isSelected = node.id === selectedId;
      const isConnected = connectedIds.has(node.id);

      return {
        ...node,
        style: {
          ...baseNodeStyle(node.data.styleType),
          opacity: isConnected ? 1 : 0.25,
          transform: isSelected ? "scale(1.08)" : "scale(1)",
          border: isSelected
            ? "3px solid #22D3EE"
            : baseNodeStyle(node.data.styleType).border,
          boxShadow: isSelected
            ? "0 0 0 3px rgba(34,211,238,0.25), 0 0 28px rgba(34,211,238,0.85)"
            : isConnected
              ? "0 0 18px rgba(34,211,238,0.35)"
              : "0 10px 25px rgba(0,0,0,0.20)",
        },
      };
    });
  }, [baseNodes, baseEdges, selectedNode]);

  const highlightedEdges = useMemo(() => {
    const selectedId = selectedNode?.id;

    if (!selectedId) return baseEdges;

    return baseEdges.map((edge) => {
      const isConnected =
        edge.source === selectedId || edge.target === selectedId;

      return {
        ...edge,
        animated: isConnected || edge.animated,
        style: {
          stroke: isConnected ? "#22D3EE" : edge.data?.color || "#64748B",
          strokeWidth: isConnected ? 4 : 1.5,
          opacity: isConnected ? 1 : 0.2,
        },
      };
    });
  }, [baseEdges, selectedNode]);

  if (error) return <Alert severity="error">{error}</Alert>;
  if (!graph || !baseNodes.length) return <CircularProgress />;

  return (
    <Card>
      <CardContent>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          sx={{ mb: 2 }}
        >
          <Box>
            <Typography variant="h5" fontWeight={800}>
              Identity Graph
            </Typography>
            <Typography color="text.secondary">
              Select a node to highlight connected relationships.
            </Typography>
          </Box>

          <Stack direction="row" spacing={1}>
            <Chip label={`${graph.accounts.length} Accounts`} color="success" size="small" />
            <Chip label={`${graph.groups.length} Groups`} color="warning" size="small" />
            <Chip label={`${graph.roles.length} Roles`} color="secondary" size="small" />
          </Stack>
        </Stack>

        <Box sx={{ height }}>
          <ReactFlow
            fitView
            nodes={highlightedNodes}
            edges={highlightedEdges}
            onNodeClick={(_, node) => setSelectedNode(node)}
            onPaneClick={() => setSelectedNode(null)}
          >
            <MiniMap nodeStrokeWidth={3} zoomable pannable />
            <Controls />
            <Background color="#1F2937" gap={18} />
          </ReactFlow>
        </Box>
      </CardContent>
    </Card>
  );
}