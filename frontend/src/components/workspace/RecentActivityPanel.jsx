import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

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

function eventColor(type) {
  if (type?.toLowerCase().includes("violation")) return "error";
  if (type?.toLowerCase().includes("review")) return "success";
  if (type?.toLowerCase().includes("sync")) return "info";
  return "primary";
}

function eventIcon(type) {
  if (type?.toLowerCase().includes("violation")) return "🔴";
  if (type?.toLowerCase().includes("review")) return "🟢";
  if (type?.toLowerCase().includes("sync")) return "🔵";
  return "🟡";
}

export default function RecentActivityPanel({ events, selectedNode }) {
  const filteredEvents = filterEvents(events, selectedNode);
  const collapsedEvents = collapseEvents(filteredEvents);

  return (
    <Card>
      <CardContent>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          sx={{ mb: 2 }}
        >
          <Box>
            <Typography variant="h5" fontWeight={900}>
              Recent Activity
            </Typography>

            <Typography color="text.secondary">
              Showing {collapsedEvents.length} grouped events
            </Typography>
          </Box>

          {selectedNode && (
            <Chip
              label={`Context: ${selectedNode.data.nodeType}`}
              color="primary"
              size="small"
              sx={{ fontWeight: 800 }}
            />
          )}
        </Stack>

        <Stack spacing={2}>
          {collapsedEvents.map((event, index) => (
            <Box key={`${event.event_type}-${index}`}>
              <Stack direction="row" spacing={2} alignItems="flex-start">
                <Typography fontSize={22}>{eventIcon(event.event_type)}</Typography>

                <Box sx={{ flexGrow: 1 }}>
                  <Stack
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                    spacing={2}
                  >
                    <Typography fontWeight={900}>{event.event_type}</Typography>

                    <Stack direction="row" spacing={1}>
                      <Chip
                        label={event.event_type}
                        color={eventColor(event.event_type)}
                        size="small"
                      />

                      {event.count > 1 && (
                        <Chip label={`${event.count}x`} color="warning" size="small" />
                      )}
                    </Stack>
                  </Stack>

                  <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                    {event.message}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                    Last seen: {new Date(event.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              </Stack>

              <Divider sx={{ mt: 2 }} />
            </Box>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}