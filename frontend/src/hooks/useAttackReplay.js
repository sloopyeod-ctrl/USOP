import { useEffect, useRef, useState } from "react";

export default function useAttackReplay(rankedPath) {
  const timer = useRef();

  const [activeNodes, setActiveNodes] = useState([]);
  const [activeEdges, setActiveEdges] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    return () => clearTimeout(timer.current);
  }, []);

  function stopReplay() {
    clearTimeout(timer.current);
    setActiveNodes([]);
    setActiveEdges([]);
    setIsPlaying(false);
  }

  function playReplay() {
    stopReplay();

    if (!rankedPath?.steps?.length) return;

    setIsPlaying(true);

    let step = 0;

    function animate() {
      if (step >= rankedPath.steps.length) {
        setIsPlaying(false);
        return;
      }

      const current = rankedPath.steps[step];

      setActiveNodes((previous) => [
        ...new Set([...previous, current.node_id]),
      ]);

      if (step > 0) {
        const previousStep = rankedPath.steps[step - 1];

        setActiveEdges((previous) => [
          ...previous,
          `${previousStep.node_id}-${current.node_id}`,
        ]);
      }

      step++;

      timer.current = setTimeout(animate, 700);
    }

    animate();
  }

  return {
    playReplay,
    stopReplay,
    activeNodes,
    activeEdges,
    isPlaying,
  };
}