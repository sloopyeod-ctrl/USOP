import { Box, Typography } from "@mui/material";
import { Handle, Position } from "@xyflow/react";

function riskColorHex(riskLevel) {
  if (riskLevel === "Critical") return "#EF4444";
  if (riskLevel === "High") return "#F97316";
  if (riskLevel === "Medium") return "#F59E0B";
  return "#22C55E";
}

function nodeIcon(type) {
  if (type === "identity") return "👤";
  if (type === "account") return "💻";
  if (type === "group") return "👥";
  if (type === "role") return "🛡";
  return "●";
}

export default function AttackPathNode({ data }) {
  const node = data.attackPathNode;
  const riskColor = riskColorHex(node.risk_level);

  const glow = data.isReplayActive
    ? "0 0 0 4px rgba(34,211,238,0.35), 0 0 36px rgba(34,211,238,0.95)"
    : data.isSelected
      ? "0 0 0 3px rgba(34,211,238,0.25), 0 0 28px rgba(34,211,238,0.85)"
      : data.isConnected
        ? `0 0 20px ${riskColor}66`
        : "0 10px 25px rgba(0,0,0,0.20)";

  return (
    <Box
      sx={{
        width: 220,
        minHeight: 78,
        p: 1.2,
        borderRadius: 2,
        textAlign: "center",
        background: "#111827",
        color: "#E5E7EB",
        border:
          data.isReplayActive || data.isSelected
            ? "3px solid #22D3EE"
            : `2px solid ${riskColor}`,
        opacity: data.isConnected ? 1 : 0.35,
        transform:
          data.isReplayActive || data.isSelected ? "scale(1.05)" : "scale(1)",
        boxShadow: glow,
        transition: "all 0.2s ease-in-out",
      }}
    >
      <Handle type="target" position={Position.Top} />

      <Typography fontSize={13} fontWeight={900}>
        {nodeIcon(node.type)} {node.label}
      </Typography>

      <Typography fontSize={11} fontWeight={900} sx={{ color: riskColor, mt: 0.5 }}>
        {node.risk_level} • +{node.risk_contribution}
      </Typography>

      <Typography fontSize={10} sx={{ color: "#9CA3AF", mt: 0.5 }}>
        Criticality {node.criticality}
      </Typography>

      <Handle type="source" position={Position.Bottom} />
    </Box>
  );
}