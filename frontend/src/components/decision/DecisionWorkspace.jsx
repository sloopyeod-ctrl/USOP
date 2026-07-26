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
import RecommendationIntelligenceWorkspace from
  "./RecommendationIntelligenceWorkspace";


function firstActionableRecommendationId(
  recommendations,
) {
  const actionable =
    recommendations.find(
      (recommendation) =>
        recommendation
          ?.organizational_disposition
          ?.is_actionable
        !== false,
    );

  return (
    actionable?.recommendation_id
    || recommendations[0]
      ?.recommendation_id
    || null
  );
}


export default function DecisionWorkspace({
  decision,
  recommendations,
  organizationId,
  identityId,
  showEvidence = true,
  enableDecisionWorkflow = false,
  onDecisionCreated = null,
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
              recommendation
                .recommendation_id
              === requestedRecommendationId,
          );

        if (requestedSelectionExists) {
          return requestedRecommendationId;
        }

        return firstActionableRecommendationId(
          availableRecommendations,
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
            recommendation
              .recommendation_id
            === selectedRecommendationId,
        ) || null,
      [
        availableRecommendations,
        selectedRecommendationId,
      ],
    );


  async function handleDecisionCreated(
    record,
  ) {
    if (
      typeof onDecisionCreated
      === "function"
    ) {
      await onDecisionCreated(record);
    }

    setRequestedRecommendationId(null);
  }


  if (!decision) {
    return null;
  }


  return (
    <Stack spacing={3}>
      <DecisionSummaryCard
        decision={decision}
      />

      {showEvidence && (
        <DecisionEvidenceCard
          decision={decision}
        />
      )}

      {enableDecisionWorkflow && (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              xl: "minmax(360px, 0.85fr) "
                + "minmax(520px, 1.35fr)",
            },
            gap: 3,
            alignItems: "start",
          }}
        >
          <RecommendationPanel
            recommendations={
              availableRecommendations
            }
            selectedRecommendationId={
              selectedRecommendationId
            }
            onSelectRecommendation={(
              recommendationId,
            ) => {
              setRequestedRecommendationId(
                recommendationId,
              );
            }}
          />

          <RecommendationIntelligenceWorkspace
            organizationId={organizationId}
            identityId={identityId}
            recommendation={
              selectedRecommendation
            }
            onDecisionCreated={
              handleDecisionCreated
            }
          />
        </Box>
      )}

      {!enableDecisionWorkflow
        && !showEvidence && (
        <RecommendationPanel
          recommendations={
            availableRecommendations
          }
        />
      )}
    </Stack>
  );
}