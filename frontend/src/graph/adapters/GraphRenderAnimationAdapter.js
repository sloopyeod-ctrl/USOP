/**
 * ============================================================================
 * USOP Graph Render Animation Adapter
 * ============================================================================
 *
 * Purpose
 * -------
 * Converts graph transition intelligence into renderer-friendly metadata.
 *
 * This adapter does not calculate security meaning.
 * It does not own graph intelligence.
 * It does not render UI.
 *
 * It prepares graph nodes and edges so rendering components can display
 * transition-aware visual states.
 * ============================================================================
 */

export const GRAPH_RENDER_ANIMATION_STATE = {
  STABLE: "stable",
  ADDED: "added",
  REMOVED: "removed",
  MOVED: "moved",
  UPDATED: "updated",
};

function buildTransitionLookup(transition = null) {
  return {
    addedNodeIds: new Set((transition?.addedNodes || []).map((node) => node.id)),
    removedNodeIds: new Set(
      (transition?.removedNodes || []).map((node) => node.id)
    ),
    movedNodeIds: new Set((transition?.movedNodes || []).map((node) => node.id)),
    updatedNodeIds: new Set(
      (transition?.updatedNodes || []).map((node) => node.id)
    ),
    addedEdgeIds: new Set((transition?.addedEdges || []).map((edge) => edge.id)),
    removedEdgeIds: new Set(
      (transition?.removedEdges || []).map((edge) => edge.id)
    ),
  };
}

function resolveNodeAnimationState(node, lookup) {
  if (lookup.addedNodeIds.has(node.id)) {
    return GRAPH_RENDER_ANIMATION_STATE.ADDED;
  }

  if (lookup.removedNodeIds.has(node.id)) {
    return GRAPH_RENDER_ANIMATION_STATE.REMOVED;
  }

  if (lookup.movedNodeIds.has(node.id)) {
    return GRAPH_RENDER_ANIMATION_STATE.MOVED;
  }

  if (lookup.updatedNodeIds.has(node.id)) {
    return GRAPH_RENDER_ANIMATION_STATE.UPDATED;
  }

  return GRAPH_RENDER_ANIMATION_STATE.STABLE;
}

function resolveEdgeAnimationState(edge, lookup) {
  if (lookup.addedEdgeIds.has(edge.id)) {
    return GRAPH_RENDER_ANIMATION_STATE.ADDED;
  }

  if (lookup.removedEdgeIds.has(edge.id)) {
    return GRAPH_RENDER_ANIMATION_STATE.REMOVED;
  }

  return GRAPH_RENDER_ANIMATION_STATE.STABLE;
}

export function applyRenderAnimationMetadata({
  graph = null,
  transition = null,
  animationMode = "idle",
}) {
  if (!graph) return null;

  const lookup = buildTransitionLookup(transition);

  return {
    ...graph,
    nodes: (graph.nodes || []).map((node) => {
      const state = resolveNodeAnimationState(node, lookup);

      return {
        ...node,
        data: {
          ...node.data,
          renderAnimation: {
            state,
            mode: animationMode,
            transitionSummary: transition?.summary || null,
            generatedAt: transition?.generatedAt || null,
          },
        },
      };
    }),
    edges: (graph.edges || []).map((edge) => {
      const state = resolveEdgeAnimationState(edge, lookup);

      return {
        ...edge,
        data: {
          ...edge.data,
          renderAnimation: {
            state,
            mode: animationMode,
            transitionSummary: transition?.summary || null,
            generatedAt: transition?.generatedAt || null,
          },
        },
      };
    }),
  };
}