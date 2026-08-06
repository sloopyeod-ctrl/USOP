import {
  Box,
  Card,
  CardContent,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import HistoryEduIcon from
  "@mui/icons-material/HistoryEdu";

import OrganizationGuidancePanel from
  "./OrganizationGuidancePanel";
import OrganizationPatternsPanel from
  "./OrganizationPatternsPanel";


function ExperienceSection({
  question,
  children,
}) {
  return (
    <Stack spacing={1.5}>
      <Box>
        <Typography
          variant="overline"
          color="primary.main"
          fontWeight={900}
          sx={{
            letterSpacing: 0.9,
          }}
        >
          {question}
        </Typography>
      </Box>

      {children}
    </Stack>
  );
}


export default function OrganizationalExperiencePanel({
  organizationId,
  identityId,
  recommendationId,
  decisionRecordId,
}) {
  return (
    <Card
      sx={{
        border:
          "1px solid rgba(168, 85, 247, 0.28)",
        backgroundColor:
          "rgba(30, 27, 75, 0.20)",
      }}
    >
      <CardContent
        sx={{
          p: {
            xs: 2.25,
            md: 2.75,
          },
        }}
      >
        <Stack spacing={2.5}>
          <Stack
            direction="row"
            spacing={1.25}
            alignItems="center"
          >
            <HistoryEduIcon
              color="secondary"
            />

            <Box>
              <Typography
                variant="h6"
                fontWeight={900}
              >
                Organizational Experience
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
              >
                Apply the organization&apos;s
                guidance and prior decision patterns
                to the current investigation.
              </Typography>
            </Box>
          </Stack>

          <ExperienceSection
            question="How do we normally respond?"
          >
            <OrganizationGuidancePanel
              organizationId={organizationId}
              decisionRecordId={
                decisionRecordId
              }
            />
          </ExperienceSection>

          <Divider />

          <ExperienceSection
            question="What have we done before?"
          >
            <OrganizationPatternsPanel
              organizationId={organizationId}
              identityId={identityId}
              recommendationId={
                recommendationId
              }
            />
          </ExperienceSection>
        </Stack>
      </CardContent>
    </Card>
  );
}
