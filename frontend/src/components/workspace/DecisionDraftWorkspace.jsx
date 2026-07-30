import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  LinearProgress,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import AutoAwesomeIcon from
  "@mui/icons-material/AutoAwesome";

import FactCheckIcon from
  "@mui/icons-material/FactCheck";


export default function DecisionDraftWorkspace({
  decisionDraft,
  isDraftLoading,
  draftError,
  justification,
  onJustificationChange,
  notes,
  onNotesChange,
}) {
  const evidence =
    decisionDraft?.evidence_used ?? [];

  const confidence =
    decisionDraft?.confidence_score ?? 0;

  const constructionVersion =
    decisionDraft?.construction_version
    ?? "unknown";

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
          Preparing deterministic documentation
          from available evidence...
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
        <Card
          variant="outlined"
          sx={{
            borderColor:
              "rgba(34, 211, 238, 0.35)",
            backgroundColor:
              "rgba(15, 23, 42, 0.42)",
          }}
        >
          <CardContent>
            <Stack spacing={2.25}>
              <Stack
                direction="row"
                spacing={1.25}
                alignItems="flex-start"
              >
                <AutoAwesomeIcon
                  color="primary"
                  sx={{ mt: 0.25 }}
                />

                <Box>
                  <Typography
                    variant="h6"
                    fontWeight={900}
                  >
                    USOP Decision Preparation
                  </Typography>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                  >
                    Generated from deterministic
                    evidence. Review and edit the
                    content before saving the
                    organizational decision.
                  </Typography>
                </Box>
              </Stack>

              <Box>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                  spacing={2}
                  sx={{ mb: 0.75 }}
                >
                  <Typography
                    variant="subtitle2"
                    fontWeight={800}
                  >
                    Construction Confidence
                  </Typography>

                  <Typography
                    variant="h5"
                    fontWeight={900}
                    color="primary"
                  >
                    {confidence}%
                  </Typography>
                </Stack>

                <LinearProgress
                  variant="determinate"
                  value={confidence}
                  sx={{
                    height: 8,
                    borderRadius: 999,
                  }}
                />

                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{
                    display: "block",
                    mt: 0.75,
                  }}
                >
                  Reflects the completeness of the
                  deterministic draft based on
                  available evidence. It does not
                  represent decision quality,
                  compliance, or analyst approval.
                </Typography>
              </Box>

              <Box>
                <Typography
                  variant="subtitle2"
                  fontWeight={800}
                  sx={{ mb: 1 }}
                >
                  Intelligence Sources
                </Typography>

                {evidence.length === 0 ? (
                  <Typography
                    variant="body2"
                    color="text.secondary"
                  >
                    No evidence references were
                    returned for this draft.
                  </Typography>
                ) : (
                  <Stack spacing={1.25}>
                    {evidence.map(
                      (item, index) => {
                        const evidenceKey = [
                          item?.source_type
                            ?? "evidence",
                          item?.source_id
                            ?? "unidentified",
                          item?.label
                            ?? index,
                        ].join(":");

                        return (
                          <Box
                            key={evidenceKey}
                            sx={{
                              p: 1.5,
                              borderRadius: 2,
                              backgroundColor:
                                "rgba(15, 23, 42, 0.55)",
                              border:
                                "1px solid rgba(148, 163, 184, 0.16)",
                            }}
                          >
                            <Stack
                              direction="row"
                              spacing={1}
                              alignItems="flex-start"
                            >
                              <FactCheckIcon
                                color="success"
                                fontSize="small"
                                sx={{ mt: 0.2 }}
                              />

                              <Box
                                sx={{ minWidth: 0 }}
                              >
                                <Typography
                                  variant="caption"
                                  sx={{
                                    color:
                                      "#94A3B8",
                                    fontWeight: 800,
                                    textTransform:
                                      "uppercase",
                                    letterSpacing:
                                      0.65,
                                  }}
                                >
                                  {item?.source_type
                                    ?? "Evidence"}
                                </Typography>

                                <Typography
                                  variant="body2"
                                  fontWeight={800}
                                  sx={{
                                    color:
                                      "#E5E7EB",
                                    mt: 0.25,
                                  }}
                                >
                                  {item?.label
                                    ?? "Unlabeled evidence"}
                                </Typography>

                                  <Typography
                                    variant="caption"
                                    sx={{
                                      mt: 1,
                                      display: "block",
                                      fontWeight: 700,
                                      color: "#94A3B8",
                                      textTransform: "uppercase",
                                      letterSpacing: 0.6,
                                    }}
                                  >
                                    Detail
                                  </Typography>

                                  <Typography
                                    variant="body2"
                                    color="text.secondary"
                                  >
                                    {item?.detail ?? "No additional detail provided."}
                                  </Typography>

                                  {item?.source_id && (
                                    <>
                                      <Typography
                                        variant="caption"
                                        sx={{
                                          mt: 1,
                                          display: "block",
                                          fontWeight: 700,
                                          color: "#94A3B8",
                                          textTransform: "uppercase",
                                          letterSpacing: 0.6,
                                        }}
                                      >
                                        Source ID
                                      </Typography>

                                      <Typography
                                        variant="body2"
                                        sx={{
                                          fontFamily: "monospace",
                                        }}
                                      >
                                        {item.source_id}
                                      </Typography>
                                    </>
                                  )}
                              </Box>
                            </Stack>
                          </Box>
                        );
                      },
                    )}
                  </Stack>
                )}
              </Box>

              <Box
                sx={{
                  pt: 1.5,
                  borderTop:
                    "1px solid rgba(148, 163, 184, 0.16)",
                }}
              >
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Prepared By

                  USOP Draft Engine

                  Version

                  {constructionVersion}
                </Typography>

                <Typography
                  variant="body2"
                  fontWeight={800}
                >
                  {constructionVersion}
                </Typography>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      )}

      <TextField
        label="Suggested Justification"
        value={justification}
        onChange={(event) =>
          onJustificationChange(
            event.target.value,
          )
        }
        multiline
        minRows={4}
        fullWidth
        helperText={
          "USOP prepared this text from deterministic evidence. The analyst remains responsible for reviewing and approving the final justification."
        }
      />

      <TextField
        label="Analyst Notes"
        value={notes}
        onChange={(event) =>
          onNotesChange(
            event.target.value,
          )
        }
        multiline
        minRows={3}
        fullWidth
        helperText={
          "Add analyst-owned context, implementation details, or follow-up actions."
        }
      />
    </Stack>
  );
}