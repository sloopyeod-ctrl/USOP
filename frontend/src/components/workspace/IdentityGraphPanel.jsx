import { useMemo } from "react";
import useAttackReplay from "../../hooks/useAttackReplay";
import GraphRenderer from "./GraphRenderer";

import { buildUsopGraph } from "../../graph/GraphBuilder";
import {
  buildReactFlowEdges,
  buildReactFlowNodes,
} from "../../graph/GraphReactFlowAdapter";
import { riskChipColor } from "../../graph/GraphTypes";
import { applyRenderAnimationMetadata } from "../../graph/adapters/GraphRenderAnimationAdapter";

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

export default function IdentityGraphPanel({
  attackPath,
  selectedPath,
  height = "62vh",
  selectedNode,
  setSelectedNode,
  transition = null,
  animationMode = "idle",
}) {
  const usopGraph = useMemo(() => {
    if (!attackPath) return null;
    return buildUsopGraph(attackPath);
  }, [attackPath]);

  const replayPath = selectedPath || attackPath?.summary?.ranked_paths?.[0] || null;

  const { playReplay, stopReplay, activeNodes, activeEdges, isPlaying } =
    useAttackReplay(replayPath);

  const nodes = useMemo(() => {
    if (!usopGraph) return [];
    return buildReactFlowNodes(usopGraph, selectedNode, activeNodes);
  }, [usopGraph, selectedNode, activeNodes]);

  const edges = useMemo(() => {
    if (!usopGraph) return [];
    return buildReactFlowEdges(usopGraph, selectedNode, activeEdges);
  }, [usopGraph, selectedNode, activeEdges]);

  const animatedRenderGraph = useMemo(() => {
    return applyRenderAnimationMetadata({
      graph: {
        nodes,
        edges,
      },
      transition,
      animationMode,
    });
  }, [nodes, edges, transition, animationMode]);

  const renderNodes = animatedRenderGraph?.nodes || [];
  const renderEdges = animatedRenderGraph?.edges || [];

  if (!attackPath || !usopGraph) return <CircularProgress />;

  if (!renderNodes.length) {
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
              label={`${usopGraph.riskLevel} Risk`}
              color={riskChipColor(usopGraph.riskLevel)}
              size="small"
            />

            <Chip
              label={`${usopGraph.summary?.total_nodes || renderNodes.length} Nodes`}
              color="primary"
              size="small"
            />

            <Chip
              label={`${usopGraph.summary?.total_edges || renderEdges.length} Edges`}
              color="secondary"
              size="small"
            />
          </Stack>
        </Stack>

        <GraphRenderer
          graphKey={usopGraph.id}
          nodes={renderNodes}
          edges={renderEdges}
          height={height}
          selectedNode={selectedNode}
          setSelectedNode={setSelectedNode}
        />
      </CardContent>
    </Card>
  );
}