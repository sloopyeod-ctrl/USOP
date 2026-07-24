import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import GppGoodIcon from
  "@mui/icons-material/GppGood";


function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";

  if (
    value === "Moderate"
    || value === "Medium"
  ) {
    return "info";
  }

  if (value === "Low") return "success";

  return "default";
}


export default function RecommendationPanel({
  recommendations = [],
  selectedRecommendationId = null,
  onSelectRecommendation = null,
}) {
  const groups = recommendations.reduce(
    (result, recommendation) => {
      const category =
        recommendation.recommendation_type
        || "General";

      if (!result[category]) {
        result[category] = [];
      }

      result[category].push(
        recommendation,
      );

      return result;
    },
    {},
  );

  const isSelectable =
    typeof onSelectRecommendation
    === "function";


  return (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
          >
            <GppGoodIcon color="primary" />

            <Box>
              <Typography
                variant="h5"
                fontWeight={900}
              >
                Recommended Actions
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
              >
                {isSelectable
                  ? (
                    "Select one recommendation for "
                    + "organizational disposition."
                  )
                  : (
                    "Deterministic actions grouped "
                    + "by security objective."
                  )}
              </Typography>
            </Box>
          </Stack>

          {Object.keys(groups).length ? (
            Object.entries(groups).map(
              ([category, items]) => (
                <Box key={category}>
                  <Stack
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                    sx={{ mb: 1.25 }}
                  >
                    <Typography
                      variant="subtitle1"
                      fontWeight={900}
                    >
                      {category}
                    </Typography>

                    <Chip
                      label={
                        `${items.length} action${
                          items.length === 1
                            ? ""
                            : "s"
                        }`
                      }
                      size="small"
                      variant="outlined"
                    />
                  </Stack>

                  <Stack spacing={1.25}>
                    {items.map(
                      (recommendation) => {
                        const recommendationId =
                          recommendation
                            .recommendation_id;

                        const isSelected =
                          recommendationId
                          === selectedRecommendationId;

                        return (
                          <Box
                            key={recommendationId}
                            role={
                              isSelectable
                                ? "button"
                                : undefined
                            }
                            tabIndex={
                              isSelectable
                                ? 0
                                : undefined
                            }
                            onClick={
                              isSelectable
                                ? () =>
                                  onSelectRecommendation(
                                    recommendationId,
                                  )
                                : undefined
                            }
                            onKeyDown={
                              isSelectable
                                ? (event) => {
                                  if (
                                    event.key
                                      === "Enter"
                                    || event.key
                                      === " "
                                  ) {
                                    event.preventDefault();

                                    onSelectRecommendation(
                                      recommendationId,
                                    );
                                  }
                                }
                                : undefined
                            }
                            sx={{
                              p: 1.75,
                              borderRadius: 2,
                              cursor: isSelectable
                                ? "pointer"
                                : "default",
                              border: isSelected
                                ? (
                                  "2px solid "
                                  + "#22D3EE"
                                )
                                : (
                                  "1px solid rgba("
                                  + "148, 163, 184, "
                                  + "0.16)"
                                ),
                              backgroundColor:
                                isSelected
                                  ? (
                                    "rgba("
                                    + "8, 47, 73, "
                                    + "0.55)"
                                  )
                                  : (
                                    "rgba("
                                    + "15, 23, 42, "
                                    + "0.30)"
                                  ),
                              transition:
                                "all 180ms ease",
                              "&:hover":
                                isSelectable
                                  ? {
                                    borderColor:
                                      "#22D3EE",
                                  }
                                  : {},
                            }}
                          >
                            <Stack spacing={1}>
                              <Stack
                                direction={{
                                  xs: "column",
                                  sm: "row",
                                }}
                                justifyContent={
                                  "space-between"
                                }
                                alignItems={{
                                  xs: "flex-start",
                                  sm: "center",
                                }}
                                spacing={1}
                              >
                                <Typography
                                  fontWeight={900}
                                >
                                  {
                                    recommendation
                                      .title
                                  }
                                </Typography>

                                <Stack
                                  direction="row"
                                  spacing={1}
                                >
                                  {isSelected && (
                                    <Chip
                                      label="Selected"
                                      size="small"
                                      color="primary"
                                    />
                                  )}

                                  <Chip
                                    label={
                                      `P${
                                        recommendation
                                          .priority
                                      }`
                                    }
                                    size="small"
                                    color="primary"
                                    variant="outlined"
                                  />

                                  <Chip
                                    label={
                                      recommendation
                                        .severity
                                    }
                                    size="small"
                                    color={severityColor(
                                      recommendation
                                        .severity,
                                    )}
                                  />
                                </Stack>
                              </Stack>

                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                {
                                  recommendation
                                    .description
                                }
                              </Typography>

                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Effort:{" "}
                                {
                                  recommendation
                                    .estimated_effort
                                }
                                {" · "}
                                Reduction potential:{" "}
                                {
                                  recommendation
                                    .risk_reduction
                                }
                              </Typography>
                            </Stack>
                          </Box>
                        );
                      },
                    )}
                  </Stack>

                  <Divider sx={{ mt: 2 }} />
                </Box>
              ),
            )
          ) : (
            <Typography color="text.secondary">
              No recommended actions are available.
            </Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}