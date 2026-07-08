import { Box, Card, CardContent, Divider, Stack, Typography } from "@mui/material";

export default function RecentActivityPanel({ events }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h5" fontWeight={800} gutterBottom>
          Recent Activity
        </Typography>

        <Stack spacing={2}>
          {events.map((event, index) => (
            <Box key={`${event.event_type}-${index}`}>
              <Typography fontWeight={800}>{event.event_type}</Typography>
              <Typography color="text.secondary">{event.message}</Typography>
              <Typography variant="body2" color="text.secondary">
                {new Date(event.timestamp).toLocaleString()}
              </Typography>
              <Divider sx={{ mt: 2 }} />
            </Box>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}