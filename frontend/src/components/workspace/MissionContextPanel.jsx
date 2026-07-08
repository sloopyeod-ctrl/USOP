import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";

function contextColor(nodeType) {
  if (nodeType === "Account") return "warning";
  if (nodeType === "Group") return "info";
  if (nodeType === "Role") return "secondary";
  if (nodeType === "Identity") return "primary";
  return "primary";
}

function getPrimaryLabel(node) {
  const d = node.data.details || {};

  return (
    d.username ||
    d.group_name ||
    d.role_name ||
    d.display_name ||
    d.primary_email ||
    node.data.label
  );
}

function getRiskLabel(node) {
  const d = node.data.details || {};

  if (d.mfa_enabled === false && d.privilege_level === "Privileged") {
    return "Critical";
  }

  if (d.privilege_level === "Privileged") {
    return "High";
  }

  if (d.mfa_enabled === false) {
    return "Medium";
  }

  return "Low";
}

function getRiskColor(risk) {
  if (risk === "Critical") return "error";
  if (risk === "High") return "warning";
  if (risk === "Medium") return "info";
  return "success";
}

function exposureContribution(node) {
  const d = node.data.details || {};
  let score = 20;

  if (d.privilege_level === "Privileged") score += 35;
  if (d.mfa_enabled === false) score += 25;
  if (d.account_type === "Admin") score += 15;
  if (node.data.nodeType === "Role") score += 30;
  if (node.data.nodeType === "Group") score += 25;

  return Math.min(score, 100);
}

function InfoRow({ label, value }) {
  if (value === undefined || value === null || value === "") return null;

  return (
    <Box sx={{ mb: 1.5 }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography fontWeight={800}>{String(value)}</Typography>
    </Box>
  );
}

export default function MissionContextPanel({ node }) {
  if (!node) {
    return (
      <Card sx={{ height: "100%" }}>
        <CardContent>
          <Typography variant="h5" fontWeight={900}>
            Mission Context
          </Typography>

          <Typography sx={{ mt: 3 }} color="text.secondary">
            Select an identity, account, group, or role from the graph to begin
            the investigation.
          </Typography>

          <Divider sx={{ my: 3 }} />

          <Typography fontWeight={800}>Investigation Workflow</Typography>

          <Typography color="text.secondary" sx={{ mt: 1 }}>
            Selecting a graph node will update context, recommendations, and
            activity panels.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const d = node.data.details || {};
  const risk = getRiskLabel(node);
  const contribution = exposureContribution(node);

  return (
    <Card
      sx={{
        height: "100%",
        border:
          risk === "Critical"
            ? "1px solid #7F1D1D"
            : "1px solid #1F2937",
        background:
          risk === "Critical"
            ? "linear-gradient(180deg, #111827 0%, #1F1113 100%)"
            : "background.paper",
      }}
    >
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h5" fontWeight={900}>
            Mission Context
          </Typography>

          <Chip
            label={node.data.nodeType}
            color={contextColor(node.data.nodeType)}
            size="small"
            sx={{ fontWeight: 800 }}
          />
        </Stack>

        <Typography variant="h6" fontWeight={900} sx={{ mt: 2 }}>
          {getPrimaryLabel(node)}
        </Typography>

        <Chip
          label={`${risk} Risk`}
          color={getRiskColor(risk)}
          sx={{ mt: 1, fontWeight: 800 }}
        />

        <Divider sx={{ my: 2 }} />

        <InfoRow label="System" value={d.system_name} />
        <InfoRow label="Status" value={d.status} />
        <InfoRow label="Account Type" value={d.account_type} />
        <InfoRow label="Privilege" value={d.privilege_level} />
        <InfoRow label="MFA" value={d.mfa_enabled === undefined ? null : d.mfa_enabled ? "Enabled" : "Disabled"} />
        <InfoRow label="Email" value={d.primary_email} />
        <InfoRow label="Username" value={d.username} />
        <InfoRow label="Group" value={d.group_name} />
        <InfoRow label="Role" value={d.role_name} />

        <Divider sx={{ my: 2 }} />

        <Typography fontWeight={900}>Exposure Contribution</Typography>

        <Stack direction="row" alignItems="center" spacing={2} sx={{ mt: 1 }}>
          <Box sx={{ flexGrow: 1 }}>
            <LinearProgress
              variant="determinate"
              value={contribution}
              color={getRiskColor(risk)}
              sx={{
                height: 10,
                borderRadius: 10,
              }}
            />
          </Box>

          <Typography fontWeight={900}>{contribution}</Typography>
        </Stack>

        <Typography color="text.secondary" sx={{ mt: 1 }}>
          Estimated contribution based on privilege, MFA, account type, and
          relationship type.
        </Typography>

        <Divider sx={{ my: 2 }} />

        <Typography fontWeight={900} sx={{ mb: 1 }}>
          Recommended Action
        </Typography>

        <Typography color="text.secondary">
          {risk === "Critical"
            ? "Prioritize remediation immediately. Validate privilege, enforce MFA, and review related access."
            : risk === "High"
              ? "Review access and confirm the relationship is still required."
              : "Monitor and validate as part of normal governance review."}
        </Typography>

        <Stack spacing={1.2} sx={{ mt: 3 }}>
          <Button variant="contained" fullWidth>
            Investigate
          </Button>

          <Button variant="outlined" fullWidth>
            Open Timeline
          </Button>

          <Button variant="outlined" fullWidth>
            View Policies
          </Button>

          <Button variant="outlined" fullWidth>
            Simulate Fix
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}