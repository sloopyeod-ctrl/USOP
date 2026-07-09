import { useMemo, useReducer } from "react";

const GRAPH_MODES = {
  BASELINE: "baseline",
  SIMULATION: "simulation",
  REPLAY: "replay",
  INVESTIGATION: "investigation",
  EXECUTIVE: "executive",
};

const initialState = {
  graph: {
    baseline: null,
    current: null,
    projected: null,
    mode: GRAPH_MODES.BASELINE,
  },

  simulation: {
    running: false,
    result: null,
    actions: [],
    error: null,
  },

  selection: {
    node: null,
    path: null,
  },

  replay: {
    playing: false,
    activeNodes: [],
    activeEdges: [],
  },
};

function workspaceReducer(state, action) {
  switch (action.type) {
    case "SET_BASELINE_GRAPH": {
      return {
        ...state,
        graph: {
          ...state.graph,
          baseline: action.payload,
          current: action.payload,
          projected: null,
          mode: GRAPH_MODES.BASELINE,
        },
      };
    }

    case "SET_PROJECTED_GRAPH": {
      return {
        ...state,
        graph: {
          ...state.graph,
          projected: action.payload,
          current: action.payload,
          mode: GRAPH_MODES.SIMULATION,
        },
      };
    }

    case "SET_GRAPH_MODE": {
      return {
        ...state,
        graph: {
          ...state.graph,
          mode: action.payload,
        },
      };
    }

    case "SELECT_NODE": {
      return {
        ...state,
        selection: {
          ...state.selection,
          node: action.payload,
        },
      };
    }

    case "SELECT_PATH": {
      return {
        ...state,
        selection: {
          ...state.selection,
          path: action.payload,
        },
      };
    }

    case "BEGIN_SIMULATION": {
      return {
        ...state,
        simulation: {
          ...state.simulation,
          running: true,
          actions: action.payload || [],
          error: null,
        },
      };
    }

    case "COMPLETE_SIMULATION": {
      return {
        ...state,
        graph: {
          ...state.graph,
          projected: action.payload?.projected || null,
          current: action.payload?.projected || state.graph.current,
          mode: GRAPH_MODES.SIMULATION,
        },
        simulation: {
          ...state.simulation,
          running: false,
          result: action.payload,
          error: null,
        },
      };
    }

    case "FAIL_SIMULATION": {
      return {
        ...state,
        simulation: {
          ...state.simulation,
          running: false,
          error: action.payload || "Simulation failed.",
        },
      };
    }

    case "RESET_SIMULATION": {
      return {
        ...state,
        graph: {
          ...state.graph,
          current: state.graph.baseline,
          projected: null,
          mode: GRAPH_MODES.BASELINE,
        },
        simulation: {
          running: false,
          result: null,
          actions: [],
          error: null,
        },
        selection: {
          ...state.selection,
          node: null,
        },
        replay: {
          playing: false,
          activeNodes: [],
          activeEdges: [],
        },
      };
    }

    case "START_REPLAY": {
      return {
        ...state,
        replay: {
          ...state.replay,
          playing: true,
        },
        graph: {
          ...state.graph,
          mode: GRAPH_MODES.REPLAY,
        },
      };
    }

    case "STOP_REPLAY": {
      return {
        ...state,
        replay: {
          ...state.replay,
          playing: false,
          activeNodes: [],
          activeEdges: [],
        },
        graph: {
          ...state.graph,
          mode: state.simulation.result
            ? GRAPH_MODES.SIMULATION
            : GRAPH_MODES.BASELINE,
        },
      };
    }

    default:
      return state;
  }
}

export default function useWorkspaceState() {
  const [state, dispatch] = useReducer(workspaceReducer, initialState);

  return useMemo(
    () => ({
      state,

      graph: state.graph,
      simulation: state.simulation,
      selection: state.selection,
      replay: state.replay,

      setBaselineGraph: (graph) =>
        dispatch({
          type: "SET_BASELINE_GRAPH",
          payload: graph,
        }),

      setProjectedGraph: (graph) =>
        dispatch({
          type: "SET_PROJECTED_GRAPH",
          payload: graph,
        }),

      setGraphMode: (mode) =>
        dispatch({
          type: "SET_GRAPH_MODE",
          payload: mode,
        }),

      selectNode: (node) =>
        dispatch({
          type: "SELECT_NODE",
          payload: node,
        }),

      selectPath: (path) =>
        dispatch({
          type: "SELECT_PATH",
          payload: path,
        }),

      beginSimulation: (actions = []) =>
        dispatch({
          type: "BEGIN_SIMULATION",
          payload: actions,
        }),

      completeSimulation: (result) =>
        dispatch({
          type: "COMPLETE_SIMULATION",
          payload: result,
        }),

      failSimulation: (message) =>
        dispatch({
          type: "FAIL_SIMULATION",
          payload: message,
        }),

      resetSimulation: () =>
        dispatch({
          type: "RESET_SIMULATION",
        }),

      startReplay: () =>
        dispatch({
          type: "START_REPLAY",
        }),

      stopReplay: () =>
        dispatch({
          type: "STOP_REPLAY",
        }),

      GRAPH_MODES,
    }),
    [state]
  );
}