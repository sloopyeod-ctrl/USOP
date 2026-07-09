import { useMemo, useReducer } from "react";
import { buildUsopGraph } from "../graph/GraphBuilder";
import { diffGraphs } from "../graph/services/GraphDiffService";
import { buildGraphIntelligence } from "../graph/services/GraphIntelligenceService";
import { buildDecisionIntelligence } from "../intelligence/DecisionIntelligenceService";

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
    baselineModel: null,
    currentModel: null,
    projectedModel: null,
    diff: null,
    intelligence: null,
    mode: GRAPH_MODES.BASELINE,
  },

  decision: {
    intelligence: null,
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
      const baselineModel = buildUsopGraph(action.payload);

      return {
        ...state,
        graph: {
          ...state.graph,
          baseline: action.payload,
          current: action.payload,
          projected: null,
          baselineModel,
          currentModel: baselineModel,
          projectedModel: null,
          diff: null,
          intelligence: null,
          mode: GRAPH_MODES.BASELINE,
        },
        decision: {
          intelligence: null,
        },
      };
    }

    case "SET_PROJECTED_GRAPH": {
      const projectedModel = buildUsopGraph(action.payload);
      const diff = diffGraphs(state.graph.currentModel, projectedModel);
      const graphIntelligence = buildGraphIntelligence(
        diff,
        state.simulation.result
      );

      const decisionIntelligence = buildDecisionIntelligence({
        graphIntelligence,
        simulationResult: state.simulation.result,
      });

      return {
        ...state,
        graph: {
          ...state.graph,
          projected: action.payload,
          current: action.payload,
          projectedModel,
          currentModel: projectedModel,
          diff,
          intelligence: graphIntelligence,
          mode: GRAPH_MODES.SIMULATION,
        },
        decision: {
          intelligence: decisionIntelligence,
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
      const projectedGraph = action.payload?.projected || null;
      const projectedModel = projectedGraph ? buildUsopGraph(projectedGraph) : null;

      const diff =
        projectedModel && state.graph.currentModel
          ? diffGraphs(state.graph.currentModel, projectedModel)
          : null;

      const graphIntelligence = buildGraphIntelligence(diff, action.payload);

      const decisionIntelligence = buildDecisionIntelligence({
        graphIntelligence,
        simulationResult: action.payload,
      });

      return {
        ...state,
        graph: {
          ...state.graph,
          projected: projectedGraph,
          current: projectedGraph || state.graph.current,
          projectedModel,
          currentModel: projectedModel || state.graph.currentModel,
          diff,
          intelligence: graphIntelligence,
          mode: GRAPH_MODES.SIMULATION,
        },
        decision: {
          intelligence: decisionIntelligence,
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
          currentModel: state.graph.baselineModel,
          projectedModel: null,
          diff: null,
          intelligence: null,
          mode: GRAPH_MODES.BASELINE,
        },
        decision: {
          intelligence: null,
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
      decision: state.decision,
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