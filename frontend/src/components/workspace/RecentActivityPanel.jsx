import { Box, Card, CardContent, Chip, Divider, Stack, Typography } from "@mui/material";

function collapseEvents(events) {
  const grouped = {};

  events.forEach((event) => {
    const key = `${event.event_type}-${event.message}`;

    if (!grouped[key]) {
      grouped[key] = {
        ...event,
        count: 1,
      };
    } else {
      grouped[key].count += 1;
    }
  });

  return Object.values(grouped);
}

export default function RecentActivityPanel({ events }) {
  const collapsedEvents = collapseEvents(events);

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" fontWeight={800} gutterBottom>
          Recent Activity
        </Typography>

        <Stack spacing={2}>
          {collapsedEvents.map((event, index) => (
            <Box key={`${event.event_type}-${index}`}>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography fontWeight={800}>{event.event_type}</Typography>

                  <Typography color="text.secondary">
                    {event.message}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Last seen: {new Date(event.timestamp).toLocaleString()}
                  </Typography>
                </Box>

                {event.count > 1 && (
                  <Chip
                    label={`${event.count}x`}
                    color="warning"
                    size="small"
                  />
                )}
              </Stack>

              <Divider sx={{ mt: 2 }} />
            </Box>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}