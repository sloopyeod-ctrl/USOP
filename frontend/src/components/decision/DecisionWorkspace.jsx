import {
  useMemo,
  useState,
} from "react";

import {
  Box,
  Stack,
} from "@mui/material";

import DecisionSummaryCard from
  "./DecisionSummaryCard";
import DecisionEvidenceCard from
  "./DecisionEvidenceCard";
import RecommendationPanel from
  "./RecommendationPanel";
import DecisionActionPanel from
  "./DecisionActionPanel";


export default function DecisionWorkspace({
  decision,
  recommendations,
  showEvidence = true,
  enableDecisionWorkflow = false,
}) {
  const availableRecommendations =
    useMemo(
      () =>
        recommendations
        || decision?.recommended_actions
        || [],
      [
        recommendations,
        decision?.recommended_actions,
      ],
    );

  const [
    requestedRecommendationId,
    setRequestedRecommendationId,
  ] = useState(null);

  const selectedRecommendationId =
    useMemo(
      () => {
        if (!enableDecisionWorkflow) {
          return null;
        }

        const requestedSelectionExists =
          availableRecommendations.some(
            (recommendation) =>
              recommendation.recommendation_id
              === requestedRecommendationId,
          );

        if (requestedSelectionExists) {
          return requestedRecommendationId;
        }

        return (
          availableRecommendations[0]
            ?.recommendation_id
          || null
        );
      },
      [
        availableRecommendations,
        enableDecisionWorkflow,
        requestedRecommendationId,
      ],
    );

  const selectedRecommendation =
    useMemo(
      () =>
        availableRecommendations.find(
          (recommendation) =>
            recommendation.recommendation_id
            === selectedRecommendationId,
        ) || null,
      [
        availableRecommendations,
        selectedRecommendationId,
      ],
    );


  if (!decision) {
    return null;
  }


  return (
    <Stack spacing={3}>
      <DecisionSummaryCard
        decision={decision}
      />

      {(showEvidence
        || enableDecisionWorkflow) && (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              xl: showEvidence
                ? "1fr 1fr"
                : "1fr",
            },
            gap: 3,
          }}
        >
          {showEvidence && (
            <DecisionEvidenceCard
              decision={decision}
            />
          )}

          <Stack spacing={3}>
            <RecommendationPanel
              recommendations={
                availableRecommendations
              }
              selectedRecommendationId={
                selectedRecommendationId
              }
              onSelectRecommendation={
                enableDecisionWorkflow
                  ? setRequestedRecommendationId
                  : null
              }
            />

            {enableDecisionWorkflow && (
              <DecisionActionPanel
                recommendation={
                  selectedRecommendation
                }
              />
            )}
          </Stack>
        </Box>
      )}
    </Stack>
  );
}