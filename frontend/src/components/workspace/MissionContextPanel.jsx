import {
  Card,
  CardContent,
  Chip,
  Divider,
  LinearProgress,
  Stack,
  Typography,
  Button,
  Box,
} from "@mui/material";

export default function MissionContextPanel({ node }) {
  if (!node) {
    return (
      <Card sx={{ height: "100%" }}>
        <CardContent>
          <Typography variant="h5" fontWeight={800}>
            Mission Context
          </Typography>

          <Typography sx={{ mt: 3 }} color="text.secondary">
            Select an identity, account, role, or group from the graph to begin
            your investigation.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const d = node.data.details;

  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>

        <Typography variant="h5" fontWeight={900}>
          Mission Context
        </Typography>

        <Chip
          sx={{ mt: 2 }}
          color="primary"
          label={node.data.nodeType}
        />

        <Typography
          variant="h6"
          fontWeight={900}
          sx={{ mt: 2 }}
        >
          {node.data.label}
        </Typography>

        <Divider sx={{ my: 2 }} />

        {Object.entries(d).map(([key, value]) => (
          <Box key={key} sx={{ mb: 2 }}>

            <Typography
              variant="body2"
              color="text.secondary"
            >
              {key.replaceAll("_", " ")}
            </Typography>

            <Typography fontWeight={700}>
              {String(value)}
            </Typography>

          </Box>
        ))}

        <Divider sx={{ my: 2 }} />

        <Typography fontWeight={700}>
          Estimated Exposure Contribution
        </Typography>

        <LinearProgress
          sx={{
            mt: 1,
            mb: 2,
            height: 10,
            borderRadius: 10,
          }}
          variant="determinate"
          value={65}
        />

        <Stack spacing={1}>

          <Button
            variant="contained"
            fullWidth
          >
            Investigate
          </Button>

          <Button
            variant="outlined"
            fullWidth
          >
            Open Timeline
          </Button>

          <Button
            variant="outlined"
            fullWidth
          >
            View Policies
          </Button>

        </Stack>

      </CardContent>
    </Card>
  );
}