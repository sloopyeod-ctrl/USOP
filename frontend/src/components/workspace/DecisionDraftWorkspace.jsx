import {
  Alert,
  CircularProgress,
  Stack,
  TextField,
} from "@mui/material";


export default function DecisionDraftWorkspace({
  decisionDraft,
  isDraftLoading,
  draftError,
  justification,
  onJustificationChange,
  notes,
  onNotesChange,
}) {
  const evidenceCount =
    decisionDraft?.metadata?.evidence_count ?? 0;

  const confidenceScore =
    decisionDraft?.confidence_score ?? 0;

  return (
    <Stack spacing={2}>
      {isDraftLoading && (
        <Alert
          severity="info"
          icon={
            <CircularProgress
              size={18}
              color="inherit"
            />
          }
        >
          Preparing an evidence-backed
          deterministic draft...
        </Alert>
      )}

      {!isDraftLoading && draftError && (
        <Alert severity="warning">
          {draftError}
          {" "}
          You may continue documenting the
          decision manually.
        </Alert>
      )}

      {!isDraftLoading && decisionDraft && (
        <Alert
          severity="success"
          variant="outlined"
        >
          Deterministic draft prepared from{" "}
          <strong>{evidenceCount}</strong>{" "}
          evidence
          {evidenceCount === 1
            ? " source"
            : " sources"}{" "}
          with{" "}
          <strong>{confidenceScore}%</strong>{" "}
          construction confidence. Review and edit
          the text before saving.
        </Alert>
      )}

      <TextField
        label="Justification"
        value={justification}
        onChange={(event) =>
          onJustificationChange(
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
          onNotesChange(event.target.value)
        }
        multiline
        minRows={2}
        fullWidth
      />
    </Stack>
  );
}
