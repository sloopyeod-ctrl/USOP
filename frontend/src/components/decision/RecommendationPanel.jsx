import { useState } from "react";

import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import GppGoodIcon from "@mui/icons-material/GppGood";
import HistoryIcon from "@mui/icons-material/History";
import CheckCircleIcon from
  "@mui/icons-material/CheckCircle";
import ScheduleIcon from "@mui/icons-material/Schedule";
import EscalatorWarningIcon from "@mui/icons-material/EscalatorWarning";
import BuildCircleOutlinedIcon from "@mui/icons-material/BuildCircleOutlined";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";

import RecommendationHistoryDialog from "./RecommendationHistoryDialog";


function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";
  if (value === "Moderate" || value === "Medium") return "info";
  if (value === "Low") return "success";
  return "default";
}


function dispositionPresentation(disposition) {
  const displayStatus = disposition?.display_status || "Open";

  if (displayStatus === "Accepted Permanently" || displayStatus === "False Positive") {
    return {
      chipColor: "success",
      borderColor: "rgba(34, 197, 94, 0.75)",
      backgroundColor: "rgba(20, 83, 45, 0.32)",
      icon: <CheckCircleIcon />,
    };
  }

  if (displayStatus === "Accepted Temporarily") {
    return {
      chipColor: "success",
      borderColor: "rgba(134, 239, 172, 0.75)",
      backgroundColor: "rgba(22, 101, 52, 0.20)",
      icon: <ScheduleIcon />,
    };
  }

  if (displayStatus === "Escalated" || displayStatus === "Deferred") {
    return {
      chipColor: "secondary",
      borderColor: "rgba(168, 85, 247, 0.75)",
      backgroundColor: "rgba(88, 28, 135, 0.28)",
      icon: <EscalatorWarningIcon />,
    };
  }

  if (displayStatus === "In Progress") {
    return {
      chipColor: "info",
      borderColor: "rgba(56, 189, 248, 0.75)",
      backgroundColor: "rgba(7, 89, 133, 0.28)",
      icon: <BuildCircleOutlinedIcon />,
    };
  }

  if (displayStatus === "Review Due") {
    return {
      chipColor: "warning",
      borderColor: "rgba(251, 191, 36, 0.85)",
      backgroundColor: "rgba(120, 53, 15, 0.30)",
      icon: <WarningAmberIcon />,
    };
  }

  return {
    chipColor: "default",
    borderColor: "rgba(148, 163, 184, 0.16)",
    backgroundColor: "rgba(15, 23, 42, 0.30)",
    icon: null,
  };
}


function formatReviewDate(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toLocaleDateString();
}


export default function RecommendationPanel({
  recommendations = [],
  selectedRecommendationId = null,
  onSelectRecommendation = null,
}) {
  const [historyRecommendation, setHistoryRecommendation] = useState(null);

  const groups = recommendations.reduce((result, recommendation) => {
    const category = recommendation.recommendation_type || "General";
    if (!result[category]) result[category] = [];
    result[category].push(recommendation);
    return result;
  }, {});

  const isSelectable = typeof onSelectRecommendation === "function";

  return (
    <>
      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Stack direction="row" spacing={1} alignItems="center">
              <GppGoodIcon color="primary" />
              <Box>
                <Typography variant="h5" fontWeight={900}>
                  Recommended Actions
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {isSelectable
                    ? "Select an action to review its organizational disposition."
                    : "Deterministic actions grouped by security objective."}
                </Typography>
              </Box>
            </Stack>

            {Object.keys(groups).length ? (
              Object.entries(groups).map(([category, items]) => (
                <Box key={category}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.25 }}>
                    <Typography variant="subtitle1" fontWeight={900}>
                      {category}
                    </Typography>
                    <Chip
                      label={`${items.length} action${items.length === 1 ? "" : "s"}`}
                      size="small"
                      variant="outlined"
                    />
                  </Stack>

                  <Stack spacing={1.25}>
                    {items.map((recommendation) => {
                      const recommendationId = recommendation.recommendation_id;
                      const disposition = recommendation.organizational_disposition;
                      const presentation = dispositionPresentation(disposition);
                      const reviewDate = formatReviewDate(disposition?.review_due_at);
                      const historyCount = disposition?.history_count || 0;
                      const isSelected = recommendationId === selectedRecommendationId;

                      return (
                        <Box
                          key={recommendationId}
                          role={isSelectable ? "button" : undefined}
                          tabIndex={isSelectable ? 0 : undefined}
                          onClick={isSelectable ? () => onSelectRecommendation(recommendationId) : undefined}
                          onKeyDown={isSelectable ? (event) => {
                            if (event.key === "Enter" || event.key === " ") {
                              event.preventDefault();
                              onSelectRecommendation(recommendationId);
                            }
                          } : undefined}
                          sx={{
                            p: 1.75,
                            borderRadius: 2,
                            cursor: isSelectable ? "pointer" : "default",
                            border: isSelected
                              ? "2px solid #22D3EE"
                              : `1px solid ${presentation.borderColor}`,
                            backgroundColor: isSelected
                              ? "rgba(8, 47, 73, 0.55)"
                              : presentation.backgroundColor,
                            transition: "all 180ms ease",
                            "&:hover": isSelectable ? { borderColor: "#22D3EE" } : {},
                          }}
                        >
                          <Stack spacing={1}>
                            <Stack
                              direction={{ xs: "column", sm: "row" }}
                              justifyContent="space-between"
                              alignItems={{ xs: "flex-start", sm: "center" }}
                              spacing={1}
                            >
                              <Typography fontWeight={900}>
                                {recommendation.title}
                              </Typography>

                              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                                {isSelected && <Chip label="Selected" size="small" color="primary" />}
                                <Chip label={`P${recommendation.priority}`} size="small" color="primary" variant="outlined" />
                                <Chip label={recommendation.severity} size="small" color={severityColor(recommendation.severity)} />
                                <Chip
                                  icon={presentation.icon}
                                  label={disposition?.display_status || "Open"}
                                  size="small"
                                  color={presentation.chipColor}
                                  variant="filled"
                                />
                              </Stack>
                            </Stack>

                            <Typography variant="body2" color="text.secondary">
                              {recommendation.description}
                            </Typography>

                            <Typography variant="caption" color="text.secondary">
                              Effort: {recommendation.estimated_effort} · Reduction potential: {recommendation.risk_reduction}
                            </Typography>

                            <Stack
                              direction={{ xs: "column", sm: "row" }}
                              spacing={1}
                              alignItems={{ xs: "flex-start", sm: "center" }}
                              justifyContent="space-between"
                            >
                              <Stack spacing={0.5}>
                                {reviewDate && (
                                  <Typography variant="caption" fontWeight={800}>
                                    Review due: {reviewDate}
                                  </Typography>
                                )}
                                {disposition?.escalated_to && (
                                  <Typography variant="caption" fontWeight={800}>
                                    Escalated to: {disposition.escalated_to}
                                  </Typography>
                                )}
                              </Stack>

                              {historyCount > 0 && (
                                <Button
                                  size="small"
                                  variant="text"
                                  startIcon={<HistoryIcon />}
                                  onClick={(event) => {
                                    event.stopPropagation();
                                    setHistoryRecommendation(recommendation);
                                  }}
                                >
                                  Decision History ({historyCount})
                                </Button>
                              )}
                            </Stack>
                          </Stack>
                        </Box>
                      );
                    })}
                  </Stack>

                  <Divider sx={{ mt: 2 }} />
                </Box>
              ))
            ) : (
              <Typography color="text.secondary">
                No recommended actions are available.
              </Typography>
            )}
          </Stack>
        </CardContent>
      </Card>

      <RecommendationHistoryDialog
        open={Boolean(historyRecommendation)}
        onClose={() => setHistoryRecommendation(null)}
        recommendation={historyRecommendation}
      />
    </>
  );
}


