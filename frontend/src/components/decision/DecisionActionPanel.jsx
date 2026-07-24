import React from "react";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
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


export default function DecisionActionPanel({
  recommendation,
}) {
  const [decisionType, setDecisionType] =
    React.useState("CorrectRisk");

  const [justification, setJustification] =
    React.useState("");

  const [notes, setNotes] =
    React.useState("");

  const [acceptanceType, setAcceptanceType] =
    React.useState("Temporary");

  const [reviewDueAt, setReviewDueAt] =
    React.useState("");

  const [escalatedTo, setEscalatedTo] =
    React.useState("");


  if (!recommendation) {
    return (
      <Alert severity="info">
        Select one recommendation before recording
        an organizational decision.
      </Alert>
    );
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
                color="text.secondary"
                fontWeight={800}
                sx={{
                  textTransform: "uppercase",
                  letterSpacing: 0.8,
                }}
              >
                Selected Recommendation
              </Typography>

              <Typography fontWeight={900}>
                {recommendation.title}
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
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
                  color={
                    recommendation.severity
                    === "Critical"
                      ? "error"
                      : recommendation.severity
                        === "High"
                        ? "warning"
                        : "info"
                  }
                />

                <Chip
                  label={
                    recommendation
                      .recommendation_type
                    || "General"
                  }
                  size="small"
                  variant="outlined"
                />
              </Stack>
            </Stack>
          </Box>

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

          {decisionType === "AcceptRisk" && (
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

          {decisionType === "Escalate" && (
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

          <Alert severity="info">
            Decision submission will be connected to
            the stable recommendation API in the next
            slice.
          </Alert>

          <Button
            variant="contained"
            size="large"
            disabled
            fullWidth
          >
            Save Organizational Decision
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}