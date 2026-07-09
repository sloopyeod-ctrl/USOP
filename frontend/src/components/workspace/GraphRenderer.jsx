import { useMemo } from "react";
import { Box } from "@mui/material";
import { Background, Controls, ReactFlow } from "@xyflow/react";

import AttackPathNode from "./AttackPathNode";

import "@xyflow/react/dist/style.css";

const nodeTypes = {
  attackPathNode: AttackPathNode,
};

export default function GraphRenderer({
  nodes,
  edges,
  height = "62vh",
  graphKey,
  selectedNode,
  setSelectedNode,
}) {
  const animationAwareNodes = useMemo(() => {
    return (nodes || []).map((node) => ({
      ...node,
      data: {
        ...node.data,
        selected: selectedNode?.id === node.id,
        renderAnimation: node.data?.renderAnimation || null,
      },
    }));
  }, [nodes, selectedNode]);

  const animationAwareEdges = useMemo(() => {
    return (edges || []).map((edge) => ({
      ...edge,
      data: {
        ...edge.data,
        renderAnimation: edge.data?.renderAnimation || null,
      },
      animated:
        edge.data?.renderAnimation?.state === "added" ||
        edge.data?.renderAnimation?.state === "updated",
    }));
  }, [edges]);

  return (
    <Box sx={{ height }}>
      <ReactFlow
        key={graphKey}
        nodes={animationAwareNodes}
        edges={animationAwareEdges}
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
  );
}