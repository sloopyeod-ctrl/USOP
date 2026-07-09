import { NavLink } from "react-router-dom";

import DashboardIcon from "@mui/icons-material/Dashboard";
import HubIcon from "@mui/icons-material/Hub";
import PsychologyIcon from "@mui/icons-material/Psychology";
import ScienceIcon from "@mui/icons-material/Science";
import FolderIcon from "@mui/icons-material/Folder";
import AssessmentIcon from "@mui/icons-material/Assessment";
import SettingsIcon from "@mui/icons-material/Settings";
import StorageIcon from "@mui/icons-material/Storage";
import PolicyIcon from "@mui/icons-material/Policy";
import HistoryIcon from "@mui/icons-material/History";

import {
  Box,
  Divider,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";

const workspaceItems = [
  {
    label: "Executive Dashboard",
    icon: <DashboardIcon />,
    to: "/",
  },
  {
    label: "Identity Explorer",
    icon: <HubIcon />,
    to: "/identity",
  },
  {
    label: "Analyst Workspace",
    icon: <PsychologyIcon />,
    to: "/workspace/ed8b8386-22fe-4d95-bf82-7071163bb4d0",
  },
  {
    label: "Attack Simulation",
    icon: <ScienceIcon />,
    to: "/workspace/ed8b8386-22fe-4d95-bf82-7071163bb4d0",
  },
];

const operationsItems = [
  {
    label: "Investigations",
    icon: <FolderIcon />,
    to: "#",
  },
  {
    label: "Executive Risk",
    icon: <AssessmentIcon />,
    to: "#",
  },
];

const platformItems = [
  {
    label: "Administration",
    icon: <SettingsIcon />,
    to: "#",
  },
  {
    label: "Connectors",
    icon: <StorageIcon />,
    to: "#",
  },
  {
    label: "Policies",
    icon: <PolicyIcon />,
    to: "#",
  },
  {
    label: "Audit Logs",
    icon: <HistoryIcon />,
    to: "#",
  },
];

function SidebarSection(title, items) {
  return (
    <>
      <Typography
        variant="overline"
        sx={{
          px: 2,
          pt: 2,
          pb: 1,
          display: "block",
          color: "#94A3B8",
          fontWeight: 700,
          letterSpacing: 1.2,
        }}
      >
        {title}
      </Typography>

      <List dense disablePadding>
        {items.map((item) => (
          <ListItemButton
            key={item.label}
            component={item.to === "#" ? "div" : NavLink}
            to={item.to === "#" ? undefined : item.to}
            sx={{
              mx: 1,
              mb: 0.5,
              borderRadius: 2,

              color: "#E5E7EB",

              "& .MuiListItemIcon-root": {
                color: "#94A3B8",
                minWidth: 40,
              },

              "&:hover": {
                backgroundColor: "rgba(34,211,238,.08)",
              },

              "&.active": {
                backgroundColor: "rgba(34,211,238,.16)",

                "& .MuiListItemIcon-root": {
                  color: "#22D3EE",
                },

                "& .MuiTypography-root": {
                  color: "#22D3EE",
                  fontWeight: 700,
                },
              },
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>

            <ListItemText
              primary={item.label}
              primaryTypographyProps={{
                fontWeight: 600,
                color: "inherit",
              }}
            />
          </ListItemButton>
        ))}
      </List>
    </>
  );
}

export default function Sidebar() {
  return (
    <Box
      sx={{
        width: 280,
        height: "100%",
        backgroundColor: "#111827",
        color: "#E5E7EB",
        borderRight: "1px solid rgba(255,255,255,.08)",
        overflowY: "auto",
      }}
    >
      {SidebarSection("WORKSPACE", workspaceItems)}

      <Divider sx={{ my: 2, borderColor: "rgba(255,255,255,.08)" }} />

      {SidebarSection("OPERATIONS", operationsItems)}

      <Divider sx={{ my: 2, borderColor: "rgba(255,255,255,.08)" }} />

      {SidebarSection("PLATFORM", platformItems)}
    </Box>
  );
}