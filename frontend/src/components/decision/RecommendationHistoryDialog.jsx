import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Typography,
} from "@mui/material";

import DecisionTimelinePanel from
  "./DecisionTimelinePanel";


export default function RecommendationHistoryDialog({
  open,
  onClose,
  recommendation,
}) {
  const disposition =
    recommendation
      ?.organizational_disposition;

  const history =
    disposition?.history || [];

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="md"
    >
      <DialogTitle>
        <Stack spacing={0.75}>
          <Typography
            variant="h5"
            fontWeight={900}
          >
            Decision Timeline
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
          >
            {recommendation?.title}
          </Typography>
        </Stack>
      </DialogTitle>

      <DialogContent dividers>
        <DecisionTimelinePanel
          history={history}
        />
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
}
