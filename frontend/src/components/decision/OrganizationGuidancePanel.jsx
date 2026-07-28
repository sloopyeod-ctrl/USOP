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
import MenuBookOutlinedIcon from
  "@mui/icons-material/MenuBookOutlined";

import {
  listDecisionKnowledge,
} from "../../services/decisionRecordService";


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
    .trim();
}


function confidenceColor(score) {
  if (score >= 90) {
    return "success";
  }

  if (score >= 70) {
    return "info";
  }

  if (score >= 50) {
    return "warning";
  }

  return "default";
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
    "Organization guidance could not "
    + "be loaded."
  );
}


function GuidanceCard({
  item,
}) {
  const relationship =
    item?.relationship || {};

  const knowledge =
    item?.knowledge || {};

  const relationshipType =
    readableValue(
      relationship.relationship_type,
    ) || "Reference";

  const category =
    readableValue(
      knowledge.category,
    );

  const status =
    readableValue(
      knowledge.status,
    );

  const confidenceScore =
    Number.isFinite(
      Number(
        knowledge.confidence_score,
      ),
    )
      ? Number(
        knowledge.confidence_score,
      )
      : null;

  return (
    <Card
      variant="outlined"
      sx={{
        borderColor:
          "rgba(167, 139, 250, 0.30)",
        background:
          "rgba(30, 41, 59, 0.45)",
      }}
    >
      <CardContent>
        <Stack spacing={1.5}>
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
            <Typography
              variant="overline"
              color="secondary.light"
              fontWeight={900}
              sx={{
                letterSpacing: 0.8,
              }}
            >
              {relationshipType}
            </Typography>

            <Stack
              direction="row"
              spacing={0.75}
              useFlexGap
              flexWrap="wrap"
            >
              {category && (
                <Chip
                  label={category}
                  size="small"
                  variant="outlined"
                />
              )}

              {status && (
                <Chip
                  label={status}
                  size="small"
                  variant="outlined"
                />
              )}

              {confidenceScore !== null && (
                <Chip
                  label={
                    `Confidence `
                    + `${confidenceScore}%`
                  }
                  size="small"
                  color={confidenceColor(
                    confidenceScore,
                  )}
                />
              )}
            </Stack>
          </Stack>

          <Typography
            variant="h6"
            fontWeight={900}
          >
            {
              knowledge.title
              || "Untitled organizational knowledge"
            }
          </Typography>

          {knowledge.summary && (
            <Typography
              variant="body2"
              sx={{
                color: "#CBD5E1",
                lineHeight: 1.7,
              }}
            >
              {knowledge.summary}
            </Typography>
          )}

          {knowledge.guidance && (
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
                    mb: 0.5,
                  }}
                >
                  Customer-Provided Guidance
                </Typography>

                <Typography
                  variant="body2"
                  sx={{
                    color: "#E5E7EB",
                    lineHeight: 1.7,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {knowledge.guidance}
                </Typography>
              </Box>
            </>
          )}

          {(
            knowledge.source_system
            || knowledge.source_identifier
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
                {knowledge.source_system && (
                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    Source:{" "}
                    {knowledge.source_system}
                  </Typography>
                )}

                {knowledge.source_identifier && (
                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    Reference:{" "}
                    {knowledge.source_identifier}
                  </Typography>
                )}

                {knowledge.version && (
                  <Typography
                    variant="caption"
                    color="text.secondary"
                  >
                    Version:{" "}
                    {knowledge.version}
                  </Typography>
                )}
              </Stack>
            </>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}


export default function OrganizationGuidancePanel({
  organizationId,
  decisionRecordId,
}) {
  const [
    guidanceItems,
    setGuidanceItems,
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
        || !decisionRecordId
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
          setGuidanceItems([]);

          try {
            const result =
              await listDecisionKnowledge({
                organizationId,
                decisionRecordId,
              });

            if (isCurrent) {
              setGuidanceItems(result);
            }
          } catch (error) {
            if (isCurrent) {
              setGuidanceItems([]);
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
      decisionRecordId,
    ],
  );

  const guidanceCount =
    guidanceItems.length;

  return (
    <Accordion
      disableGutters
      elevation={0}
      sx={{
        background:
          "rgba(15, 23, 42, 0.35)",
        border:
          "1px solid rgba(167, 139, 250, 0.24)",
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
          "organization-guidance-content"
        }
        id="organization-guidance-header"
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
          <MenuBookOutlinedIcon
            color="secondary"
          />

          <Box sx={{ flexGrow: 1 }}>
            <Typography
              variant="h6"
              fontWeight={900}
            >
              Organization Guidance
            </Typography>

            <Typography
              variant="caption"
              color="text.secondary"
            >
              Customer-owned policies,
              procedures, standards, decisions,
              and operational knowledge linked
              to this decision.
            </Typography>
          </Box>

          <Chip
            label={
              `${guidanceCount} linked`
            }
            size="small"
            variant="outlined"
          />
        </Stack>
      </AccordionSummary>

      <AccordionDetails
        id="organization-guidance-content"
        sx={{
          px: 2,
          pb: 2,
        }}
      >
        {!decisionRecordId && (
          <Alert severity="info">
            Organization guidance can be linked
            after an accountable decision has
            been recorded.
          </Alert>
        )}

        {decisionRecordId && isLoading && (
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
              Loading linked organizational
              knowledge...
            </Typography>
          </Stack>
        )}

        {decisionRecordId
          && !isLoading
          && loadError && (
          <Alert severity="error">
            {loadError}
          </Alert>
        )}

        {decisionRecordId
          && !isLoading
          && !loadError
          && guidanceCount === 0 && (
          <Alert severity="info">
            No customer-owned organizational
            guidance has been linked to this
            decision.
          </Alert>
        )}

        {decisionRecordId
          && !isLoading
          && !loadError
          && guidanceCount > 0 && (
          <Stack spacing={1.5}>
            {guidanceItems.map(
              (item, index) => (
                <GuidanceCard
                  key={
                    item?.relationship?.id
                    || (
                      item?.knowledge?.id
                      + `-${index}`
                    )
                  }
                  item={item}
                />
              ),
            )}
          </Stack>
        )}
      </AccordionDetails>
    </Accordion>
  );
}
