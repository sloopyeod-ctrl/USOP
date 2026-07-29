import {
  useEffect,
  useState,
} from "react";

import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import ExpandMoreIcon from
  "@mui/icons-material/ExpandMore";
import InsightsOutlinedIcon from
  "@mui/icons-material/InsightsOutlined";

import {
  listDecisionPatterns,
} from "../../services/decisionPatternService";


function readableValue(value) {
  if (
    value === null
    || value === undefined
    || value === ""
  ) {
    return null;
  }

  return String(value)
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}


function titleCase(value) {
  const readable =
    readableValue(value);

  if (!readable) {
    return null;
  }

  return readable
    .split(" ")
    .map(
      (word) => (
        word.length
          ? (
            word.charAt(0).toUpperCase()
            + word.slice(1).toLowerCase()
          )
          : word
      ),
    )
    .join(" ");
}


function formatDateTime(value) {
  if (!value) {
    return null;
  }

  const date = new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return null;
  }

  return date.toLocaleString();
}


function errorMessage(error) {
  const apiDetail =
    error?.response?.data?.detail;

  if (
    typeof apiDetail === "string"
    && apiDetail.trim()
  ) {
    return apiDetail;
  }

  if (
    typeof error?.message === "string"
    && error.message.trim()
  ) {
    return error.message;
  }

  return (
    "Organizational patterns could not "
    + "be loaded."
  );
}


function metricLabel(metricName) {
  const normalized =
    String(metricName || "")
      .trim()
      .toLowerCase();

  const simplifiedNames = {
    occurrence_count: "Occurrences",
    evidence_record_count:
      "Evidence Records",
    decision_record_count:
      "Decision Records",
    scheduled_review_count:
      "Scheduled Reviews",
    open_count: "Currently Open",
    closed_count: "Closed",
    overdue_count: "Overdue",
    success_count: "Successful",
    failure_count: "Unsuccessful",
    exception_count: "Exceptions",
  };

  if (
    Object.prototype.hasOwnProperty.call(
      simplifiedNames,
      normalized,
    )
  ) {
    return simplifiedNames[normalized];
  }

  return (
    titleCase(metricName)
    || "Metric"
  );
}


function numberValue(value) {
  const numericValue =
    Number(value);

  return Number.isFinite(
    numericValue,
  )
    ? numericValue
    : null;
}


function formatNumber(value) {
  return new Intl.NumberFormat(
    "en-US",
    {
      maximumFractionDigits: 2,
    },
  ).format(value);
}


function formatMetricValue(
  metricName,
  value,
) {
  if (
    value === null
    || value === undefined
    || value === ""
  ) {
    return "Not available";
  }

  if (typeof value === "boolean") {
    return value
      ? "Yes"
      : "No";
  }

  if (Array.isArray(value)) {
    return value.length
      ? value.join(", ")
      : "None";
  }

  if (
    typeof value === "object"
  ) {
    return JSON.stringify(value);
  }

  const normalizedName =
    String(metricName || "")
      .trim()
      .toLowerCase();

  const numericValue =
    numberValue(value);

  if (numericValue === null) {
    return String(value);
  }

  if (
    normalizedName.endsWith("_rate")
    || normalizedName.endsWith("_percent")
    || normalizedName.endsWith("_percentage")
  ) {
    return `${formatNumber(numericValue)}%`;
  }

  if (
    normalizedName.endsWith("_days")
    || normalizedName.includes(
      "_days_",
    )
  ) {
    return (
      `${formatNumber(numericValue)} `
      + (
        numericValue === 1
          ? "day"
          : "days"
      )
    );
  }

  if (
    normalizedName.endsWith("_hours")
    || normalizedName.includes(
      "_hours_",
    )
  ) {
    return (
      `${formatNumber(numericValue)} `
      + (
        numericValue === 1
          ? "hour"
          : "hours"
      )
    );
  }

  if (
    normalizedName.endsWith("_minutes")
    || normalizedName.includes(
      "_minutes_",
    )
  ) {
    return (
      `${formatNumber(numericValue)} `
      + (
        numericValue === 1
          ? "minute"
          : "minutes"
      )
    );
  }

  return formatNumber(
    numericValue,
  );
}


function PatternMetric({
  metricName,
  value,
}) {
  return (
    <Box
      sx={{
        minWidth: 0,
        p: 1.5,
        borderRadius: 2,
        border:
          "1px solid rgba(34, 211, 238, 0.18)",
        background:
          "rgba(15, 23, 42, 0.55)",
      }}
    >
      <Typography
        variant="caption"
        color="text.secondary"
        fontWeight={800}
        sx={{
          display: "block",
          textTransform: "uppercase",
          letterSpacing: 0.65,
          mb: 0.6,
        }}
      >
        {metricLabel(metricName)}
      </Typography>

      <Typography
        variant="h6"
        fontWeight={900}
        sx={{
          color: "#E5E7EB",
          overflowWrap: "anywhere",
        }}
      >
        {
          formatMetricValue(
            metricName,
            value,
          )
        }
      </Typography>
    </Box>
  );
}


function PatternCard({
  pattern,
}) {
  const metrics =
    pattern?.metrics
    && typeof pattern.metrics === "object"
      ? Object.entries(
        pattern.metrics,
      )
      : [];

  const firstSeenAt =
    formatDateTime(
      pattern?.first_seen_at,
    );

  const lastSeenAt =
    formatDateTime(
      pattern?.last_seen_at,
    );

  const evidenceRecordIds =
    Array.isArray(
      pattern?.evidence_record_ids,
    )
      ? pattern.evidence_record_ids
      : [];

  const scope =
    titleCase(
      pattern?.scope,
    );

  return (
    <Card
      variant="outlined"
      sx={{
        borderColor:
          "rgba(34, 211, 238, 0.28)",
        background:
          "rgba(30, 41, 59, 0.45)",
      }}
    >
      <CardContent>
        <Stack spacing={2}>
          <Stack
            direction={{
              xs: "column",
              sm: "row",
            }}
            justifyContent="space-between"
            alignItems={{
              xs: "flex-start",
              sm: "center",
            }}
            spacing={1}
          >
            <Box>
              <Typography
                variant="overline"
                color="info.light"
                fontWeight={900}
                sx={{
                  letterSpacing: 0.8,
                }}
              >
                Observed Pattern
              </Typography>

              <Typography
                variant="h6"
                fontWeight={900}
              >
                {
                  pattern?.title
                  || "Organizational Pattern"
                }
              </Typography>
            </Box>

            <Stack
              direction="row"
              spacing={0.75}
              flexWrap="wrap"
              useFlexGap
            >
              {scope && (
                <Chip
                  label={scope}
                  size="small"
                  variant="outlined"
                />
              )}

              <Chip
                label={
                  `${evidenceRecordIds.length} `
                  + (
                    evidenceRecordIds.length === 1
                      ? "record"
                      : "records"
                  )
                }
                size="small"
                color="info"
              />
            </Stack>
          </Stack>

          {pattern?.summary && (
            <Typography
              variant="body2"
              sx={{
                color: "#CBD5E1",
                lineHeight: 1.7,
              }}
            >
              {pattern.summary}
            </Typography>
          )}

          {metrics.length > 0 && (
            <>
              <Divider />

              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  fontWeight={800}
                  sx={{
                    display: "block",
                    textTransform: "uppercase",
                    letterSpacing: 0.7,
                    mb: 1,
                  }}
                >
                  Observed Metrics
                </Typography>

                <Box
                  sx={{
                    display: "grid",
                    gridTemplateColumns: {
                      xs: "1fr",
                      sm: "repeat(2, 1fr)",
                      md: "repeat(3, 1fr)",
                    },
                    gap: 1.25,
                  }}
                >
                  {metrics.map(
                    ([
                      metricName,
                      value,
                    ]) => (
                      <PatternMetric
                        key={metricName}
                        metricName={
                          metricName
                        }
                        value={value}
                      />
                    ),
                  )}
                </Box>
              </Box>
            </>
          )}

          {(
            firstSeenAt
            || lastSeenAt
          ) && (
            <>
              <Divider />

              <Stack
                direction={{
                  xs: "column",
                  sm: "row",
                }}
                spacing={{
                  xs: 0.5,
                  sm: 2,
                }}
              >
                {firstSeenAt && (
                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    First observed:{" "}
                    {firstSeenAt}
                  </Typography>
                )}

                {lastSeenAt && (
                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    Last observed:{" "}
                    {lastSeenAt}
                  </Typography>
                )}
              </Stack>
            </>
          )}

          {evidenceRecordIds.length > 0 && (
            <>
              <Divider />

              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  fontWeight={800}
                  sx={{
                    display: "block",
                    textTransform: "uppercase",
                    letterSpacing: 0.7,
                    mb: 0.75,
                  }}
                >
                  Supporting Decision Records
                </Typography>

                <Stack
                  direction="row"
                  spacing={0.75}
                  flexWrap="wrap"
                  useFlexGap
                >
                  {evidenceRecordIds.map(
                    (recordId) => (
                      <Chip
                        key={recordId}
                        label={recordId}
                        size="small"
                        variant="outlined"
                      />
                    ),
                  )}
                </Stack>
              </Box>
            </>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}


export default function OrganizationPatternsPanel({
  organizationId,
  identityId,
  recommendationId,
}) {
  const [
    patterns,
    setPatterns,
  ] = useState([]);

  const [
    isLoading,
    setIsLoading,
  ] = useState(false);

  const [
    loadError,
    setLoadError,
  ] = useState(null);

  useEffect(
    () => {
      let isCurrent = true;

      if (
        !organizationId
        || !identityId
        || !recommendationId
      ) {
        return () => {
          isCurrent = false;
        };
      }

      Promise.resolve().then(
        async () => {
          if (!isCurrent) {
            return;
          }

          setIsLoading(true);
          setLoadError(null);
          setPatterns([]);

          try {
            const result =
              await listDecisionPatterns({
                organizationId,
                identityId,
                recommendationId,
              });

            if (isCurrent) {
              setPatterns(result);
            }
          } catch (error) {
            if (isCurrent) {
              setPatterns([]);
              setLoadError(
                errorMessage(error),
              );
            }
          } finally {
            if (isCurrent) {
              setIsLoading(false);
            }
          }
        },
      );

      return () => {
        isCurrent = false;
      };
    },
    [
      organizationId,
      identityId,
      recommendationId,
    ],
  );

  const patternCount =
    patterns.length;

  const hasCompleteScope = Boolean(
    organizationId
    && identityId
    && recommendationId,
  );

  return (
    <Accordion
      disableGutters
      elevation={0}
      sx={{
        background:
          "rgba(15, 23, 42, 0.35)",
        border:
          "1px solid rgba(34, 211, 238, 0.24)",
        borderRadius: "12px !important",
        overflow: "hidden",
        "&::before": {
          display: "none",
        },
      }}
    >
      <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        aria-controls={
          "organization-patterns-content"
        }
        id="organization-patterns-header"
        sx={{
          px: 2,
          py: 0.5,
        }}
      >
        <Stack
          direction="row"
          alignItems="center"
          spacing={1.25}
          sx={{
            width: "100%",
            pr: 1,
          }}
        >
          <InsightsOutlinedIcon
            color="info"
          />

          <Box sx={{ flexGrow: 1 }}>
            <Typography
              variant="h6"
              fontWeight={900}
            >
              Organization Patterns
            </Typography>

            <Typography
              variant="caption"
              color="text.secondary"
            >
              Deterministic observations derived
              from this organization&apos;s
              recorded decision history.
            </Typography>
          </Box>

          <Chip
            label={
              `${patternCount} `
              + (
                patternCount === 1
                  ? "pattern"
                  : "patterns"
              )
            }
            size="small"
            variant="outlined"
          />
        </Stack>
      </AccordionSummary>

      <AccordionDetails
        id="organization-patterns-content"
        sx={{
          px: 2,
          pb: 2,
        }}
      >
        {!hasCompleteScope && (
          <Alert severity="info">
            Organizational patterns become
            available when a recommendation,
            identity, and organization are all
            in scope.
          </Alert>
        )}

        {hasCompleteScope
          && isLoading && (
          <Stack
            direction="row"
            alignItems="center"
            spacing={1.5}
            sx={{
              py: 2,
            }}
          >
            <CircularProgress size={22} />

            <Typography
              variant="body2"
              color="text.secondary"
            >
              Analyzing organizational decision
              history...
            </Typography>
          </Stack>
        )}

        {hasCompleteScope
          && !isLoading
          && loadError && (
          <Alert severity="error">
            {loadError}
          </Alert>
        )}

        {hasCompleteScope
          && !isLoading
          && !loadError
          && patternCount === 0 && (
          <Alert severity="info">
            No repeated organizational pattern
            has been observed for this
            recommendation.
          </Alert>
        )}

        {hasCompleteScope
          && !isLoading
          && !loadError
          && patternCount > 0 && (
          <Stack spacing={1.5}>
            {patterns.map(
              (pattern, index) => (
                <PatternCard
                  key={
                    (
                      pattern?.pattern_type
                      || "pattern"
                    )
                    + `-${index}`
                  }
                  pattern={pattern}
                />
              ),
            )}
          </Stack>
        )}
      </AccordionDetails>
    </Accordion>
  );
}
