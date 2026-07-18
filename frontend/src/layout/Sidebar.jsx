import {
  NavLink,
  useLocation,
} from "react-router-dom";

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


function resolveActiveIdentityId(pathname) {
  const workspaceMatch = pathname.match(
    /^\/workspace\/([^/]+)/,
  );

  if (workspaceMatch?.[1]) {
    return workspaceMatch[1];
  }

  const identityMatch = pathname.match(
    /^\/identity\/([^/]+)/,
  );

  if (identityMatch?.[1]) {
    return identityMatch[1];
  }

  const explorerMatch = pathname.match(
    /^\/explorer\/([^/]+)/,
  );

  if (explorerMatch?.[1]) {
    return explorerMatch[1];
  }

  return localStorage.getItem(
    "usop.activeInvestigationIdentityId",
  );
}


function SidebarSection({
  title,
  items,
}) {
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
            component={
              item.disabled
                ? "div"
                : NavLink
            }
            to={
              item.disabled
                ? undefined
                : item.to
            }
            disabled={item.disabled}
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
                backgroundColor:
                  "rgba(34,211,238,.08)",
              },

              "&.active": {
                backgroundColor:
                  "rgba(34,211,238,.16)",

                "& .MuiListItemIcon-root": {
                  color: "#22D3EE",
                },

                "& .MuiTypography-root": {
                  color: "#22D3EE",
                  fontWeight: 700,
                },
              },

              "&.Mui-disabled": {
                opacity: 0.45,
                color: "#94A3B8",
              },
            }}
          >
            <ListItemIcon>
              {item.icon}
            </ListItemIcon>

            <ListItemText
              primary={item.label}
              secondary={item.secondary}
              primaryTypographyProps={{
                fontWeight: 600,
                color: "inherit",
              }}
              secondaryTypographyProps={{
                color: "#64748B",
                fontSize: 11,
              }}
            />
          </ListItemButton>
        ))}
      </List>
    </>
  );
}


export default function Sidebar() {
  const location = useLocation();

  const activeIdentityId = resolveActiveIdentityId(
    location.pathname,
  );

  const investigationRoute = activeIdentityId
    ? `/workspace/${activeIdentityId}`
    : "/";

  const workspaceItems = [
    {
      label: "Executive Dashboard",
      icon: <DashboardIcon />,
      to: "/",
    },
    {
      label: "Select Identity",
      icon: <HubIcon />,
      to: "/",
      secondary:
        "Choose from exposed identities",
    },
    {
      label: activeIdentityId
        ? "Resume Investigation"
        : "Analyst Workspace",
      icon: <PsychologyIcon />,
      to: investigationRoute,
      secondary: activeIdentityId
        ? "Return to active identity"
        : "Select an identity first",
    },
    {
      label: "Attack Simulation",
      icon: <ScienceIcon />,
      to: investigationRoute,
      secondary: activeIdentityId
        ? "Continue active investigation"
        : "Select an identity first",
    },
  ];

  const operationsItems = [
    {
      label: "Investigations",
      icon: <FolderIcon />,
      disabled: true,
    },
    {
      label: "Executive Risk",
      icon: <AssessmentIcon />,
      disabled: true,
    },
  ];

  const platformItems = [
    {
      label: "Administration",
      icon: <SettingsIcon />,
      to: "/platform/administration",
    },
    {
      label: "Connectors",
      icon: <StorageIcon />,
      disabled: true,
    },
    {
      label: "Policies",
      icon: <PolicyIcon />,
      disabled: true,
    },
    {
      label: "Audit Logs",
      icon: <HistoryIcon />,
      disabled: true,
    },
  ];

  return (
    <Box
      sx={{
        width: 280,
        height: "100%",
        backgroundColor: "#111827",
        color: "#E5E7EB",
        borderRight:
          "1px solid rgba(255,255,255,.08)",
        overflowY: "auto",
      }}
    >
      <SidebarSection
        title="WORKSPACE"
        items={workspaceItems}
      />

      <Divider
        sx={{
          my: 2,
          borderColor:
            "rgba(255,255,255,.08)",
        }}
      />

      <SidebarSection
        title="OPERATIONS"
        items={operationsItems}
      />

      <Divider
        sx={{
          my: 2,
          borderColor:
            "rgba(255,255,255,.08)",
        }}
      />

      <SidebarSection
        title="PLATFORM"
        items={platformItems}
      />
    </Box>
  );
}
