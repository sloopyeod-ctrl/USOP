import { useEffect, useState } from "react";
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

import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
} from "@xyflow/react";

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

function nodeStyle(type) {
  return {
    ...NODE_STYLES[type],
    borderRadius: 14,
    padding: 12,
    fontWeight: 800,
    width: 190,
    textAlign: "center",
    boxShadow: "0 10px 25px rgba(0,0,0,0.35)",
  };
}

function edgeStyle(color = "#22D3EE") {
  return {
    stroke: color,
    strokeWidth: 2.5,
  };
}

export default function IdentityGraphPanel({ identityId, height = "62vh" }) {
  const [graph, setGraph] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
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
      },
      type: "input",
      style: nodeStyle("identity"),
    });

    data.accounts.forEach((account, index) => {
      const isPrivileged = account.privilege_level === "Privileged";

      graphNodes.push({
        id: account.id,
        position: { x: 120 + index * 245, y: 210 },
        data: {
          label: `${isPrivileged ? "🚨" : "💻"} ${account.username}`,
          details: account,
          nodeType: "Account",
        },
        style: nodeStyle(isPrivileged ? "privilegedAccount" : "account"),
      });

      graphEdges.push({
        id: `identity-${account.id}`,
        source: "identity",
        target: account.id,
        animated: isPrivileged,
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
        },
        style: nodeStyle("group"),
      });

      graphEdges.push({
        id: `${group.account_id}-${group.group_id}`,
        source: group.account_id,
        target: group.group_id,
        animated: group.privilege_level === "Privileged",
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
        },
        style: nodeStyle("role"),
      });

      graphEdges.push({
        id: `${role.account_id}-${role.role_id}`,
        source: role.account_id,
        target: role.role_id,
        animated: role.privilege_level === "Privileged",
        style: edgeStyle("#A78BFA"),
      });
    });

    setNodes(graphNodes);
    setEdges(graphEdges);
  }

  if (error) return <Alert severity="error">{error}</Alert>;
  if (!graph || !nodes.length) return <CircularProgress />;

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
              Accounts, groups, and role relationships.
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
            nodes={nodes}
            edges={edges}
            onNodeClick={(_, node) => setSelectedNode(node)}
          >
            <MiniMap nodeStrokeWidth={3} zoomable pannable />
            <Controls />
            <Background color="#1F2937" gap={18} />
          </ReactFlow>
        </Box>

        {selectedNode && (
          <Box sx={{ mt: 2 }}>
            <Chip label={selectedNode.data.nodeType} color="primary" size="small" />
            <Typography fontWeight={800} sx={{ mt: 1 }}>
              {selectedNode.data.label}
            </Typography>

            {Object.entries(selectedNode.data.details).slice(0, 6).map(([key, value]) => (
              <Typography key={key} variant="body2" color="text.secondary">
                {key.replaceAll("_", " ")}: {String(value ?? "None")}
              </Typography>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}