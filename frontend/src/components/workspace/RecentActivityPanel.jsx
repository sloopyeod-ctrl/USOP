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

function filterEvents(events, selectedNode) {
  if (!selectedNode) return events;

  const details = selectedNode.data.details || {};
  const username = details.username;
  const groupName = details.group_name;
  const roleName = details.role_name;

  const filtered = events.filter((event) => {
    const text = `${event.event_type} ${event.message} ${event.actor || ""}`.toLowerCase();

    return (
      (username && text.includes(username.toLowerCase())) ||
      (groupName && text.includes(groupName.toLowerCase())) ||
      (roleName && text.includes(roleName.toLowerCase()))
    );
  });

  return filtered.length ? filtered : events;
}

export default function RecentActivityPanel({ events, selectedNode }) {
  const filteredEvents = filterEvents(events, selectedNode);
  const collapsedEvents = collapseEvents(filteredEvents);

  return (
    <Card>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h5" fontWeight={800}>
            Recent Activity
          </Typography>

          {selectedNode && (
            <Chip
              label={`Context: ${selectedNode.data.nodeType}`}
              color="primary"
              size="small"
            />
          )}
        </Stack>

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
                  <Chip label={`${event.count}x`} color="warning" size="small" />
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