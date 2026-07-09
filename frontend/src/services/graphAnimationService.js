/**
 * Graph Animation Service
 *
 * Purpose:
 * - Own graph animation timing and transition behavior
 * - Keep animation logic out of pages
 * - Allow graph renderers to consume animation-ready state
 *
 * Development rule:
 * Engines produce intelligence.
 * Renderers display intelligence.
 * Animation services prepare visual transitions.
 */

export const GRAPH_ANIMATION_MODES = {
  IDLE: "idle",
  MORPH: "morph",
  SIMULATION: "simulation",
  RESET: "reset",
};

export const GRAPH_ANIMATION_DURATION = {
  FAST: 250,
  NORMAL: 500,
  SLOW: 850,
};

export function getAnimationConfig(mode = GRAPH_ANIMATION_MODES.IDLE) {
  switch (mode) {
    case GRAPH_ANIMATION_MODES.MORPH:
      return {
        duration: GRAPH_ANIMATION_DURATION.NORMAL,
        easing: "ease-in-out",
      };

    case GRAPH_ANIMATION_MODES.SIMULATION:
      return {
        duration: GRAPH_ANIMATION_DURATION.SLOW,
        easing: "ease-out",
      };

    case GRAPH_ANIMATION_MODES.RESET:
      return {
        duration: GRAPH_ANIMATION_DURATION.FAST,
        easing: "ease-in",
      };

    case GRAPH_ANIMATION_MODES.IDLE:
    default:
      return {
        duration: 0,
        easing: "linear",
      };
  }
}

export function applyGraphAnimationMetadata(nodes = [], mode = GRAPH_ANIMATION_MODES.IDLE) {
  const config = getAnimationConfig(mode);

  return nodes.map((node) => ({
    ...node,
    data: {
      ...node.data,
      animation: {
        mode,
        duration: config.duration,
        easing: config.easing,
        animated: mode !== GRAPH_ANIMATION_MODES.IDLE,
      },
    },
  }));
}

export function resetGraphAnimationMetadata(nodes = []) {
  return nodes.map((node) => ({
    ...node,
    data: {
      ...node.data,
      animation: {
        mode: GRAPH_ANIMATION_MODES.IDLE,
        duration: 0,
        easing: "linear",
        animated: false,
      },
    },
  }));
}

export function createAnimatedGraphState({
  nodes = [],
  edges = [],
  mode = GRAPH_ANIMATION_MODES.IDLE,
}) {
  return {
    nodes: applyGraphAnimationMetadata(nodes, mode),
    edges,
    animationMode: mode,
    animationConfig: getAnimationConfig(mode),
    animatedAt: new Date().toISOString(),
  };
}