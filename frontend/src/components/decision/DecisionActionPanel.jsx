import {
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
  FormControl,
  FormControlLabel,
  FormLabel,
  MenuItem,
  Radio,
  RadioGroup,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import FactCheckIcon from
  "@mui/icons-material/FactCheck";

import {
  createDecisionRecord,
} from "../../services/decisionRecordService";


const DECISION_OPTIONS = [
  {
    value: "CorrectRisk",
    label: "Correct Risk",
  },
  {
    value: "AcceptRisk",
    label: "Accept Risk",
  },
  {
    value: "Escalate",
    label: "Escalate",
  },
  {
    value: "Defer",
    label: "Defer",
  },
  {
    value: "FalsePositive",
    label: "False Positive",
  },
];


function severityColor(value) {
  if (value === "Critical") {
    return "error";
  }

  if (value === "High") {
    return "warning";
  }

  if (
    value === "Moderate"
    || value === "Medium"
  ) {
    return "info";
  }

  if (value === "Low") {
    return "success";
  }

  return "default";
}


function resolveErrorMessage(error) {
  return (
    error?.response?.data?.detail
    || error?.message
    || "Unable to record the decision."
  );
}


export default function DecisionActionPanel({
  organizationId,
  identityId,
  recommendation,
  onDecisionCreated = null,
}) {
  const [
    decisionType,
    setDecisionType,
  ] = useState("CorrectRisk");

  const [
    justification,
    setJustification,
  ] = useState("");

  const [notes, setNotes] =
    useState("");

  const [
    acceptanceType,
    setAcceptanceType,
  ] = useState("Temporary");

  const [
    reviewDueAt,
    setReviewDueAt,
  ] = useState("");

  const [
    escalatedTo,
    setEscalatedTo,
  ] = useState("");

  const [
    externalTicketReference,
    setExternalTicketReference,
  ] = useState("");

  const [
    isSubmitting,
    setIsSubmitting,
  ] = useState(false);

  const [
    submissionError,
    setSubmissionError,
  ] = useState(null);

  const [
    createdDecision,
    setCreatedDecision,
  ] = useState(null);

  if (!recommendation) {
    return (
      <Alert severity="info">
        Select one recommendation before recording
        an organizational decision.
      </Alert>
    );
  }


  const canSubmit =
    Boolean(organizationId)
    && Boolean(identityId)
    && Boolean(
      recommendation.recommendation_id,
    )
    && !isSubmitting;


  async function submitDecision() {
    if (!canSubmit) {
      return;
    }

    setIsSubmitting(true);
    setSubmissionError(null);
    setCreatedDecision(null);

    try {
      const record =
        await createDecisionRecord({
          organizationId,
          identityId,
          recommendationId:
            recommendation
              .recommendation_id,
          decisionType,
          justification,
          notes,
          acceptanceType,
          reviewDueAt,
          escalatedTo,
          externalTicketReference,
        });

      setCreatedDecision(record);

      if (
        typeof onDecisionCreated
        === "function"
      ) {
        onDecisionCreated(record);
      }
    } catch (error) {
      console.error(
        "Decision creation failed:",
        error,
      );

      setSubmissionError(
        resolveErrorMessage(error),
      );
    } finally {
      setIsSubmitting(false);
    }
  }


  return (
    <Card
      sx={{
        border:
          "1px solid rgba(34, 211, 238, 0.35)",
      }}
    >
      <CardContent>
        <Stack spacing={2.5}>
          <Stack
            direction="row"
            spacing={1.25}
            alignItems="center"
          >
            <FactCheckIcon color="primary" />

            <Box>
              <Typography
                variant="h5"
                fontWeight={900}
              >
                Organizational Decision
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
              >
                Record one authoritative response to
                the selected recommendation.
              </Typography>
            </Box>
          </Stack>

          <Box
            sx={{
              p: 1.75,
              borderRadius: 2,
              backgroundColor:
                "rgba(15, 23, 42, 0.45)",
              border:
                "1px solid rgba(148, 163, 184, 0.16)",
            }}
          >
            <Stack spacing={1}>
              <Typography
                variant="caption"
                sx={{
                  color: "#94A3B8",
                  fontWeight: 800,
                  textTransform:
                    "uppercase",
                  letterSpacing: 0.8,
                }}
              >
                Selected Recommendation
              </Typography>

              <Typography
                fontWeight={900}
                sx={{ color: "#E5E7EB" }}
              >
                {recommendation.title}
              </Typography>

              <Typography
                variant="body2"
                sx={{ color: "#94A3B8" }}
              >
                {recommendation.description}
              </Typography>

              <Stack
                direction="row"
                spacing={1}
                flexWrap="wrap"
                useFlexGap
              >
                <Chip
                  label={
                    recommendation.severity
                    || "Unclassified"
                  }
                  size="small"
                  color={severityColor(
                    recommendation.severity,
                  )}
                />

                <Chip
                  label={
                    recommendation
                      .recommendation_type
                    || "General"
                  }
                  size="small"
                  variant="outlined"
                  sx={{
                    color: "#E5E7EB",
                    borderColor: "#475569",
                  }}
                />
              </Stack>
            </Stack>
          </Box>

          {!organizationId && (
            <Alert severity="warning">
              An active Organization is required
              before recording a decision.
            </Alert>
          )}

          <FormControl>
            <FormLabel>
              Organizational Response
            </FormLabel>

            <RadioGroup
              value={decisionType}
              onChange={(event) =>
                setDecisionType(
                  event.target.value,
                )
              }
            >
              {DECISION_OPTIONS.map(
                (option) => (
                  <FormControlLabel
                    key={option.value}
                    value={option.value}
                    control={<Radio />}
                    label={option.label}
                  />
                ),
              )}
            </RadioGroup>
          </FormControl>

          <TextField
            label="Justification"
            value={justification}
            onChange={(event) =>
              setJustification(
                event.target.value,
              )
            }
            multiline
            minRows={3}
            fullWidth
            helperText={
              "Explain why this response is appropriate."
            }
          />

          <TextField
            label="Analyst Notes"
            value={notes}
            onChange={(event) =>
              setNotes(event.target.value)
            }
            multiline
            minRows={2}
            fullWidth
          />

          {decisionType
            === "AcceptRisk" && (
            <Stack spacing={2}>
              <FormControl fullWidth>
                <FormLabel>
                  Acceptance Duration
                </FormLabel>

                <Select
                  value={acceptanceType}
                  onChange={(event) =>
                    setAcceptanceType(
                      event.target.value,
                    )
                  }
                >
                  <MenuItem value="Temporary">
                    Temporary
                  </MenuItem>

                  <MenuItem value="Permanent">
                    Permanent
                  </MenuItem>
                </Select>
              </FormControl>

              <TextField
                label="Review Due"
                type="datetime-local"
                value={reviewDueAt}
                onChange={(event) =>
                  setReviewDueAt(
                    event.target.value,
                  )
                }
                slotProps={{
                  inputLabel: {
                    shrink: true,
                  },
                }}
                fullWidth
              />
            </Stack>
          )}

          {decisionType
            === "Escalate" && (
            <TextField
              label="Escalate To"
              value={escalatedTo}
              onChange={(event) =>
                setEscalatedTo(
                  event.target.value,
                )
              }
              fullWidth
            />
          )}

          <TextField
            label="External Ticket Reference"
            value={externalTicketReference}
            onChange={(event) =>
              setExternalTicketReference(
                event.target.value,
              )
            }
            fullWidth
            helperText={
              "Optional external case, change, or ticket ID."
            }
          />

          {submissionError && (
            <Alert severity="error">
              {submissionError}
            </Alert>
          )}

          {createdDecision && (
            <Alert severity="success">
              Decision recorded successfully.
              Status:{" "}
              <strong>
                {createdDecision.status}
              </strong>
              . Decision ID:{" "}
              <strong>
                {createdDecision.id}
              </strong>
            </Alert>
          )}

          <Button
            variant="contained"
            size="large"
            disabled={!canSubmit}
            fullWidth
            onClick={submitDecision}
            startIcon={
              isSubmitting
                ? (
                  <CircularProgress
                    size={18}
                    color="inherit"
                  />
                )
                : undefined
            }
          >
            {isSubmitting
              ? "Recording Decision..."
              : "Save Organizational Decision"}
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}