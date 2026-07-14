import {
  Box,
  Stack,
} from "@mui/material";

import DecisionSummaryCard from "./DecisionSummaryCard";
import DecisionEvidenceCard from "./DecisionEvidenceCard";
import RecommendationPanel from "./RecommendationPanel";


export default function DecisionWorkspace({
  decision,
  recommendations,
  showDetails = true,
}) {
  if (!decision) {
    return null;
  }

  return (
    <Stack spacing={3}>
      <DecisionSummaryCard
        decision={decision}
      />

      {showDetails && (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              xl: "1.15fr 0.85fr",
            },
            gap: 3,
          }}
        >
          <DecisionEvidenceCard
            decision={decision}
          />

          <RecommendationPanel
            recommendations={
              recommendations ||
              decision.recommended_actions ||
              []
            }
          />
        </Box>
      )}
    </Stack>
  );
}
