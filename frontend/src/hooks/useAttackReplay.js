import { useEffect, useRef, useState } from "react";

export default function useAttackReplay(nodes, edges) {
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

    if (!nodes.length) return;

    setIsPlaying(true);

    let step = 0;

    function animate() {
      if (step >= edges.length) {
        setIsPlaying(false);
        return;
      }

      const edge = edges[step];

      setActiveEdges((previous) => [...previous, edge.id]);

      setActiveNodes((previous) => [
        ...new Set([...previous, edge.source, edge.target]),
      ]);

      step++;

      timer.current = setTimeout(animate, 500);
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