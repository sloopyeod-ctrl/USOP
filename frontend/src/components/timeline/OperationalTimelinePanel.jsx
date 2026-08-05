import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import TimelineIcon from
  "@mui/icons-material/Timeline";

import {
  getOperationalTimeline,
} from "../../services/operationalTimelineService";


function formatDateTime(value) {
  if (!value) {
    return "Time unavailable";
  }

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? "Time unavailable"
    : date.toLocaleString();
}


function visibilityColor(value) {
  if (value === "Critical") {
    return "error";
  }

  if (value === "Warning") {
    return "warning";
  }

  if (value === "Notice") {
    return "info";
  }

  return "default";
}


function timelineAccent(value) {
  if (value === "Critical") {
    return "error.main";
  }

  if (value === "Warning") {
    return "warning.main";
  }

  if (value === "Notice") {
    return "info.main";
  }

  return "text.secondary";
}


function errorMessage(error) {
  return (
    error?.response?.data?.detail
    || error?.message
    || "Unable to load operational history."
  );
}


function mergeEvents(
  current,
  incoming,
) {
  const byId = new Map();

  [...current, ...incoming].forEach(
    (event) => {
      if (event?.event_id) {
        byId.set(
          event.event_id,
          event,
        );
      }
    },
  );

  return Array.from(
    byId.values(),
  );
}


function OperationalTimelineEvent({
  event,
  isLast,
}) {
  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns:
          "28px minmax(0, 1fr)",
        columnGap: 1.5,
      }}
    >
      <Box
        sx={{
          position: "relative",
          display: "flex",
          justifyContent: "center",
        }}
      >
        <Box
          sx={{
            mt: 0.75,
            width: 12,
            height: 12,
            borderRadius: "50%",
            backgroundColor:
              timelineAccent(
                event.visibility,
              ),
            boxShadow:
              "0 0 0 4px rgba(15, 23, 42, 0.95)",
            zIndex: 1,
          }}
        />

        {!isLast && (
          <Box
            sx={{
              position: "absolute",
              top: 18,
              bottom: -24,
              width: 2,
              backgroundColor:
                "rgba(148, 163, 184, 0.28)",
            }}
          />
        )}
      </Box>

      <Box sx={{ pb: isLast ? 0 : 3 }}>
        <Stack spacing={1.25}>
          <Stack
            direction={{
              xs: "column",
              sm: "row",
            }}
            spacing={1}
            justifyContent="space-between"
            alignItems={{
              xs: "flex-start",
              sm: "center",
            }}
          >
            <Stack
              direction="row"
              spacing={1}
              flexWrap="wrap"
              useFlexGap
            >
              <Chip
                label={
                  event.category
                  || "Operational"
                }
                size="small"
                variant="outlined"
              />

              <Chip
                label={
                  event.visibility
                  || "Information"
                }
                size="small"
                color={visibilityColor(
                  event.visibility,
                )}
              />
            </Stack>

            <Typography
              variant="caption"
              color="text.secondary"
            >
              {formatDateTime(
                event.occurred_at,
              )}
            </Typography>
          </Stack>

          <Box>
            <Typography
              fontWeight={900}
            >
              {event.title}
            </Typography>

            {event.summary && (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  mt: 0.5,
                  lineHeight: 1.6,
                  whiteSpace: "pre-wrap",
                }}
              >
                {event.summary}
              </Typography>
            )}
          </Box>

          <Stack
            direction="row"
            spacing={1.5}
            flexWrap="wrap"
            useFlexGap
          >
            {event.actor && (
              <Typography
                variant="caption"
                color="text.secondary"
              >
                Actor: {event.actor}
              </Typography>
            )}

            {event.source_type && (
              <Typography
                variant="caption"
                color="text.secondary"
              >
                Source: {event.source_type}
              </Typography>
            )}

            {event.contributor_name && (
              <Typography
                variant="caption"
                color="text.secondary"
              >
                Contributor: {
                  event.contributor_name
                }
              </Typography>
            )}
          </Stack>
        </Stack>
      </Box>
    </Box>
  );
}


export default function OperationalTimelinePanel({
  organizationId,
  identityId,
  refreshKey = 0,
}) {
  const [events, setEvents] =
    useState([]);

  const [
    nextCursor,
    setNextCursor,
  ] = useState(null);

  const [
    diagnostics,
    setDiagnostics,
  ] = useState([]);

  const [
    warnings,
    setWarnings,
  ] = useState([]);

  const [
    isPartial,
    setIsPartial,
  ] = useState(false);

  const [
    isLoading,
    setIsLoading,
  ] = useState(false);

  const [
    isLoadingEarlier,
    setIsLoadingEarlier,
  ] = useState(false);

  const [error, setError] =
    useState(null);


  const loadTimeline = useCallback(
    async ({
      cursor = null,
      append = false,
    } = {}) => {
      if (
        !organizationId
        || !identityId
      ) {
        return;
      }

      if (append) {
        setIsLoadingEarlier(true);
      } else {
        setEvents([]);
        setNextCursor(null);
        setDiagnostics([]);
        setWarnings([]);
        setIsPartial(false);
        setIsLoading(true);
      }

      setError(null);

      try {
        const result =
          await getOperationalTimeline({
            organizationId,
            identityId,
            cursor,
            limit: 25,
          });

        const incomingEvents =
          Array.isArray(result?.events)
            ? result.events
            : [];

        setEvents((current) =>
          append
            ? mergeEvents(
              current,
              incomingEvents,
            )
            : incomingEvents,
        );

        setNextCursor(
          result?.next_cursor || null,
        );

        setDiagnostics(
          Array.isArray(
            result
              ?.contributor_diagnostics,
          )
            ? result
              .contributor_diagnostics
            : [],
        );

        setWarnings(
          Array.isArray(result?.warnings)
            ? result.warnings
            : [],
        );

        setIsPartial(
          Boolean(result?.is_partial),
        );
      } catch (requestError) {
        console.error(
          "Operational timeline failed:",
          requestError,
        );

        if (!append) {
          setEvents([]);
        }

        setError(
          errorMessage(requestError),
        );
      } finally {
        if (append) {
          setIsLoadingEarlier(false);
        } else {
          setIsLoading(false);
        }
      }
    },
    [
      organizationId,
      identityId,
    ],
  );


  useEffect(
    () => {
      let isCurrent = true;

      Promise.resolve().then(
        async () => {
          if (!isCurrent) {
            return;
          }

          await loadTimeline();
        },
      );

      return () => {
        isCurrent = false;
      };
    },
    [
      loadTimeline,
      refreshKey,
    ],
  );


  const failedDiagnostics =
    diagnostics.filter(
      (item) =>
        item.status === "Failed"
        || item.status === "Unavailable",
    );


  return (
    <Card
      sx={{
        height: "100%",
        border:
          "1px solid rgba(34, 211, 238, 0.24)",
      }}
    >
      <CardContent>
        <Stack spacing={2}>
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
            justifyContent="space-between"
          >
            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
            >
              <TimelineIcon color="primary" />

              <Box>
                <Typography
                  variant="h6"
                  fontWeight={900}
                >
                  Operational Timeline
                </Typography>

                <Typography
                  variant="body2"
                  color="text.secondary"
                >
                  Authorization, investigation,
                  and decision history.
                </Typography>
              </Box>
            </Stack>

            <Chip
              label={`${events.length} event${
                events.length === 1
                  ? ""
                  : "s"
              }`}
              size="small"
              variant="outlined"
            />
          </Stack>

          <Divider />

          {isPartial && (
            <Alert severity="warning">
              Some operational history could
              not be loaded. Available events
              are still shown.
            </Alert>
          )}

          {failedDiagnostics.map(
            (diagnostic) => (
              <Alert
                key={
                  diagnostic
                    .contributor_name
                }
                severity="warning"
              >
                {
                  diagnostic
                    .contributor_name
                }: {
                  diagnostic.message
                  || "Contributor unavailable."
                }
              </Alert>
            ),
          )}

          {warnings.map(
            (warning) => (
              <Alert
                key={warning}
                severity="info"
              >
                {warning}
              </Alert>
            ),
          )}

          {error && (
            <Alert severity="error">
              {error}
            </Alert>
          )}

          {isLoading && (
            <Box
              sx={{
                py: 4,
                display: "flex",
                justifyContent: "center",
              }}
            >
              <CircularProgress />
            </Box>
          )}

          {!isLoading
            && !error
            && events.length === 0 && (
            <Typography
              color="text.secondary"
            >
              No operational history has
              been recorded for this identity.
            </Typography>
          )}

          {!isLoading
            && events.length > 0 && (
            <Stack spacing={0}>
              {events.map(
                (event, index) => (
                  <OperationalTimelineEvent
                    key={event.event_id}
                    event={event}
                    isLast={
                      index
                      === events.length - 1
                    }
                  />
                ),
              )}
            </Stack>
          )}

          {nextCursor && (
            <Button
              variant="outlined"
              disabled={isLoadingEarlier}
              onClick={() =>
                loadTimeline({
                  cursor: nextCursor,
                  append: true,
                })
              }
              startIcon={
                isLoadingEarlier
                  ? (
                    <CircularProgress
                      size={18}
                      color="inherit"
                    />
                  )
                  : undefined
              }
            >
              {isLoadingEarlier
                ? "Loading Earlier History..."
                : "Load Earlier History"}
            </Button>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
