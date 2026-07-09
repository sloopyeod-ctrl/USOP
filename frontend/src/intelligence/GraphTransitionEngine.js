/**
 * ============================================================================
 * USOP Graph Transition Engine
 * ============================================================================
 *
 * Purpose
 * -------
 * Produces transition intelligence describing how one graph evolves into
 * another. Rendering components consume this transition metadata to animate
 * graph changes without embedding comparison logic in the UI.
 *
 * Architecture
 * ------------
 * Backend Intelligence
 *      ↓
 * Workspace State Engine
 *      ↓
 * Graph Diff Engine
 *      ↓
 * Graph Transition Engine   <-- This Engine
 *      ↓
 * Graph Animation Service
 *      ↓
 * React Flow Renderer
 *
 * This engine never performs rendering.
 * It only produces transition intelligence.
 * ============================================================================
 */

export function buildGraphTransition(previousGraph = {}, nextGraph = {}) {
  const previousNodes = previousGraph.nodes || [];
  const nextNodes = nextGraph.nodes || [];

  const previousEdges = previousGraph.edges || [];
  const nextEdges = nextGraph.edges || [];

  const previousNodeMap = new Map(previousNodes.map((n) => [n.id, n]));
  const nextNodeMap = new Map(nextNodes.map((n) => [n.id, n]));

  const previousEdgeMap = new Map(previousEdges.map((e) => [e.id, e]));
  const nextEdgeMap = new Map(nextEdges.map((e) => [e.id, e]));

  const addedNodes = [];
  const removedNodes = [];
  const movedNodes = [];
  const updatedNodes = [];

  const addedEdges = [];
  const removedEdges = [];

  nextNodes.forEach((node) => {
    const previous = previousNodeMap.get(node.id);

    if (!previous) {
      addedNodes.push(node);
      return;
    }

    const moved =
      previous.position?.x !== node.position?.x ||
      previous.position?.y !== node.position?.y;

    if (moved) {
      movedNodes.push({
        id: node.id,
        from: previous.position,
        to: node.position,
      });
    }

    if (
      JSON.stringify(previous.data) !== JSON.stringify(node.data)
    ) {
      updatedNodes.push(node);
    }
  });

  previousNodes.forEach((node) => {
    if (!nextNodeMap.has(node.id)) {
      removedNodes.push(node);
    }
  });

  nextEdges.forEach((edge) => {
    if (!previousEdgeMap.has(edge.id)) {
      addedEdges.push(edge);
    }
  });

  previousEdges.forEach((edge) => {
    if (!nextEdgeMap.has(edge.id)) {
      removedEdges.push(edge);
    }
  });

  return {
    transitionType: "graph-update",

    addedNodes,
    removedNodes,
    movedNodes,
    updatedNodes,

    addedEdges,
    removedEdges,

    summary: {
      nodesAdded: addedNodes.length,
      nodesRemoved: removedNodes.length,
      nodesMoved: movedNodes.length,
      nodesUpdated: updatedNodes.length,

      edgesAdded: addedEdges.length,
      edgesRemoved: removedEdges.length,
    },

    generatedAt: new Date().toISOString(),
  };
}