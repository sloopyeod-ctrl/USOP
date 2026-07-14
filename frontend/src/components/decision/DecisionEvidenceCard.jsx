import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import FactCheckIcon from "@mui/icons-material/FactCheck";


function severityColor(value) {
  if (value === "Critical") return "error";
  if (value === "High") return "warning";

  if (
    value === "Moderate" ||
    value === "Medium"
  ) {
    return "info";
  }

  if (value === "Low") return "success";

  return "default";
}


function displayValue(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "Not available";
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return String(value);
}


export default function DecisionEvidenceCard({
  decision,
}) {
  if (!decision?.available) {
    return null;
  }

  const authorization =
    decision.authorization ?? {};

  const classifications =
    authorization.role_classifications ?? [];

  const evidence = decision.evidence ?? [];

  const confidenceBasis =
    decision.confidence?.basis ?? [];

  const confidenceGaps =
    decision.confidence?.gaps ?? [];

  return (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
          >
            <FactCheckIcon color="primary" />

            <Box>
              <Typography
                variant="h5"
                fontWeight={900}
              >
                Decision Evidence
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
              >
                Observable facts supporting the
                classification and recommended action.
              </Typography>
            </Box>
          </Stack>

          <Accordion defaultExpanded>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
            >
              <Stack
                direction="row"
                spacing={1}
                alignItems="center"
                flexWrap="wrap"
                useFlexGap
              >
                <Typography fontWeight={900}>
                  Authorization Classification
                </Typography>

                <Chip
                  label={
                    `${authorization
                      .privileged_role_count ?? 0} ` +
                    "high-impact roles"
                  }
                  size="small"
                  color="warning"
                />

                <Chip
                  label={
                    `${authorization
                      .tenant_wide_assignment_count ?? 0} ` +
                    "tenant-wide"
                  }
                  size="small"
                  variant="outlined"
                />
              </Stack>
            </AccordionSummary>

            <AccordionDetails>
              <Stack spacing={1.5}>
                {classifications.length ? (
                  classifications.map(
                    (item, index) => (
                      <Box
                        key={
                          `${item.role_name}-${index}`
                        }
                        sx={{
                          p: 2,
                          borderRadius: 2,
                          border:
                            "1px solid rgba(" +
                            "148, 163, 184, 0.16)",
                          backgroundColor:
                            "rgba(15, 23, 42, 0.35)",
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
                              {item.role_name}
                            </Typography>

                            <Stack
                              direction="row"
                              spacing={1}
                              flexWrap="wrap"
                              useFlexGap
                            >
                              <Chip
                                label={
                                  item.risk_level
                                }
                                color={severityColor(
                                  item.risk_level,
                                )}
                                size="small"
                              />

                              <Chip
                                label={
                                  item.scope ||
                                  "Unknown Scope"
                                }
                                size="small"
                                variant="outlined"
                              />

                              <Chip
                                label={
                                  item.assignment ||
                                  "Unknown Assignment"
                                }
                                size="small"
                                variant="outlined"
                              />
                            </Stack>
                          </Stack>

                          <Typography
                            variant="body2"
                            color="text.secondary"
                          >
                            Capability:{" "}
                            {displayValue(
                              item.capability,
                            )}
                          </Typography>

                          {(item.reasons ?? []).map(
                            (reason, reasonIndex) => (
                              <Typography
                                key={reasonIndex}
                                variant="body2"
                              >
                                {reason}
                              </Typography>
                            ),
                          )}

                          <Typography
                            variant="caption"
                            color="text.secondary"
                          >
                            Classification source:{" "}
                            {displayValue(
                              item
                                .classification_source,
                            )}
                          </Typography>
                        </Stack>
                      </Box>
                    ),
                  )
                ) : (
                  <Alert severity="info">
                    No classified role assignments are
                    available.
                  </Alert>
                )}
              </Stack>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
            >
              <Typography fontWeight={900}>
                Supporting Facts ({evidence.length})
              </Typography>
            </AccordionSummary>

            <AccordionDetails>
              <Stack spacing={1.5}>
                {evidence.map((item, index) => (
                  <Box
                    key={
                      `${item.type}-${item.title}-${index}`
                    }
                    sx={{
                      p: 1.75,
                      borderRadius: 2,
                      border:
                        "1px solid rgba(" +
                        "148, 163, 184, 0.16)",
                    }}
                  >
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      alignItems="center"
                      spacing={1}
                    >
                      <Typography fontWeight={900}>
                        {item.title}
                      </Typography>

                      <Chip
                        label={item.type}
                        size="small"
                        variant="outlined"
                      />
                    </Stack>

                    <Divider sx={{ my: 1.25 }} />

                    <Box
                      sx={{
                        display: "grid",
                        gridTemplateColumns: {
                          xs: "1fr",
                          sm: "1fr 1fr",
                        },
                        gap: 1,
                      }}
                    >
                      {Object.entries(
                        item.facts ?? {},
                      ).map(([key, value]) => (
                        <Box key={key}>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{
                              textTransform:
                                "capitalize",
                            }}
                          >
                            {key.replaceAll("_", " ")}
                          </Typography>

                          <Typography
                            variant="body2"
                            fontWeight={700}
                          >
                            {displayValue(value)}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                ))}
              </Stack>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
            >
              <Typography fontWeight={900}>
                Confidence Basis
              </Typography>
            </AccordionSummary>

            <AccordionDetails>
              <Stack spacing={1}>
                {confidenceBasis.map(
                  (basis, index) => (
                    <Alert
                      key={index}
                      severity="success"
                      variant="outlined"
                    >
                      {basis}
                    </Alert>
                  ),
                )}

                {confidenceGaps.map(
                  (gap, index) => (
                    <Alert
                      key={index}
                      severity="warning"
                      variant="outlined"
                    >
                      {gap}
                    </Alert>
                  ),
                )}
              </Stack>
            </AccordionDetails>
          </Accordion>
        </Stack>
      </CardContent>
    </Card>
  );
}
