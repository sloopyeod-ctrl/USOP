import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import {
  useNavigate,
} from "react-router-dom";

import useOrganizationContext from
  "../hooks/useOrganizationContext";

import {
  listPendingDecisionWorkItems,
} from "../services/pendingDecisionWorkItemService";


const PRIORITY_ORDER = [
  "Critical",
  "High",
  "Moderate",
  "Low",
  "Unknown",
];

const PRIORITY_SEVERITY = {
  Critical: "error",
  High: "warning",
  Moderate: "warning",
  Low: "success",
  Unknown: "default",
};


function formatAge(createdAt) {
  if (!createdAt) {
    return "Unknown";
  }

  const created = new Date(createdAt);
  const now = new Date();
  const milliseconds = Math.max(
    0,
    now.getTime() - created.getTime(),
  );

  const minutes = Math.floor(
    milliseconds / 60000,
  );

  if (minutes < 1) {
    return "Just now";
  }

  if (minutes < 60) {
    return `${minutes} min ago`;
  }

  const hours = Math.floor(minutes / 60);

  if (hours < 24) {
    return `${hours} hr ago`;
  }

  const days = Math.floor(hours / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}


function PrioritySummary({
  label,
  count,
}) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          spacing={2}
        >
          <Typography
            variant="subtitle2"
            color="text.secondary"
          >
            {label}
          </Typography>

          <Chip
            label={count}
            color={
              PRIORITY_SEVERITY[label]
              || "default"
            }
            size="small"
          />
        </Stack>
      </CardContent>
    </Card>
  );
}


function WorkItemCard({
  item,
  onOpen,
}) {
  const sourceLabel = (
    item.source_type
    || "Unknown Source"
  );

  return (
    <Card variant="outlined">
      <CardActionArea
        onClick={() => onOpen(item)}
        disabled={!item.identity_id}
      >
        <CardContent>
          <Stack
            direction={{
              xs: "column",
              md: "row",
            }}
            justifyContent="space-between"
            spacing={2}
          >
            <Box sx={{ minWidth: 0 }}>
              <Stack
                direction="row"
                spacing={1}
                alignItems="center"
                flexWrap="wrap"
                useFlexGap
                sx={{ mb: 1 }}
              >
                <Chip
                  label={item.priority}
                  color={
                    PRIORITY_SEVERITY[
                      item.priority
                    ] || "default"
                  }
                  size="small"
                />

                <Chip
                  label={item.status}
                  size="small"
                  variant="outlined"
                />

                <Chip
                  label={sourceLabel}
                  size="small"
                  variant="outlined"
                />
              </Stack>

              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  mb: 0.75,
                }}
              >
                {item.title}
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 1 }}
              >
                {item.summary
                  || item.materiality_reason
                  || "Human review is required."}
              </Typography>

              <Typography
                variant="caption"
                color="text.secondary"
              >
                Created {formatAge(item.created_at)}
                {" • "}
                Category {item.decision_category}
              </Typography>
            </Box>

            <Stack
              alignItems={{
                xs: "flex-start",
                md: "flex-end",
              }}
              justifyContent="center"
              spacing={1}
              sx={{ minWidth: 170 }}
            >
              <Typography
                variant="body2"
                color="text.secondary"
              >
                Risk: {item.risk_level}
              </Typography>

              <Button
                variant="contained"
                size="small"
                disabled={!item.identity_id}
              >
                {item.identity_id
                  ? "Open Investigation"
                  : "Identity Unavailable"}
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}


export default function OperationsWorkspace() {
  const navigate = useNavigate();

  const {
    activeOrganization,
    activeOrganizationId,
    isLoadingOrganizations,
    organizationError,
  } = useOrganizationContext();

  const [items, setItems] = useState([]);
  const [
    loadedOrganizationId,
    setLoadedOrganizationId,
  ] = useState(null);
  const [error, setError] = useState(null);

  const isLoading = (
    Boolean(activeOrganizationId)
    && loadedOrganizationId
      !== activeOrganizationId
  );

  useEffect(() => {
    if (!activeOrganizationId) {
      return undefined;
    }

    let isCurrent = true;

    listPendingDecisionWorkItems({
      organizationId: activeOrganizationId,
      status: "Pending",
    })
      .then((records) => {
        if (!isCurrent) {
          return;
        }

        setItems(
          Array.isArray(records)
            ? records
            : [],
        );
        setError(null);
        setLoadedOrganizationId(
          activeOrganizationId,
        );
      })
      .catch((requestError) => {
        if (!isCurrent) {
          return;
        }

        console.error(requestError);
        setError(
          "Unable to load pending analyst work.",
        );
        setLoadedOrganizationId(
          activeOrganizationId,
        );
      });

    return () => {
      isCurrent = false;
    };
  }, [activeOrganizationId]);

  const counts = useMemo(() => {
    return PRIORITY_ORDER.reduce(
      (result, priority) => ({
        ...result,
        [priority]: items.filter(
          (item) =>
            item.priority === priority,
        ).length,
      }),
      {},
    );
  }, [items]);

  const orderedItems = useMemo(() => {
    const rank = new Map(
      PRIORITY_ORDER.map(
        (priority, index) => [
          priority,
          index,
        ],
      ),
    );

    return [...items].sort((left, right) => {
      const leftRank = rank.get(
        left.priority,
      ) ?? PRIORITY_ORDER.length;
      const rightRank = rank.get(
        right.priority,
      ) ?? PRIORITY_ORDER.length;

      if (leftRank !== rightRank) {
        return leftRank - rightRank;
      }

      return new Date(
        left.created_at,
      ) - new Date(
        right.created_at,
      );
    });
  }, [items]);

  function openWorkItem(item) {
    if (!item.identity_id) {
      return;
    }

    navigate(
      `/workspace/${item.identity_id}`,
    );
  }

  if (organizationError) {
    return (
      <Alert severity="error">
        {organizationError}
      </Alert>
    );
  }

  if (
    isLoadingOrganizations
    || !activeOrganizationId
  ) {
    return <CircularProgress />;
  }

  return (
    <Box
      data-organization-id={
        activeOrganizationId
      }
    >
      <Stack spacing={1} sx={{ mb: 3 }}>
        <Typography
          variant="h4"
          sx={{ fontWeight: 800 }}
        >
          Analyst Operations Workspace
        </Typography>

        <Typography
          color="text.secondary"
        >
          What requires attention right now
          {activeOrganization?.name
            ? ` for ${activeOrganization.name}`
            : ""}.
        </Typography>
      </Stack>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr 1fr",
            lg: "repeat(5, 1fr)",
          },
          gap: 2,
          mb: 3,
        }}
      >
        {PRIORITY_ORDER.map(
          (priority) => (
            <PrioritySummary
              key={priority}
              label={priority}
              count={counts[priority] || 0}
            />
          ),
        )}
      </Box>

      <Divider sx={{ mb: 3 }} />

      <Stack spacing={2}>
        <Typography
          variant="h6"
          sx={{ fontWeight: 700 }}
        >
          Pending Decision Queue
        </Typography>

        {isLoading && (
          <CircularProgress />
        )}

        {error && (
          <Alert severity="error">
            {error}
          </Alert>
        )}

        {!isLoading
          && !error
          && orderedItems.length === 0
          && (
            <Alert severity="success">
              No pending decisions require
              attention for this Organization.
            </Alert>
          )}

        {!isLoading
          && !error
          && orderedItems.map((item) => (
            <WorkItemCard
              key={item.id}
              item={item}
              onOpen={openWorkItem}
            />
          ))}
      </Stack>
    </Box>
  );
}
