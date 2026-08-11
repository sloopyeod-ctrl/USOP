import {
  Link,
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
      {title && (
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
      )}

      <List dense disablePadding>
        {items.map((item) => {
          const isActive =
            Boolean(item.active);

          return (
            <ListItemButton
              key={item.label}
              component={
                item.disabled
                  ? "div"
                  : Link
              }
              to={
                item.disabled
                  ? undefined
                  : item.to
              }
              disabled={item.disabled}
              selected={isActive}
              sx={{
                mx: 1,
                mb: 0.5,
                px: 1.5,
                py: 0.8,
                borderRadius: 2,

                color:
                  isActive
                    ? "#22D3EE"
                    : "#E5E7EB",

                backgroundColor:
                  isActive
                    ? "rgba(8,145,178,0.28)"
                    : "transparent",

                "& .MuiListItemIcon-root": {
                  minWidth: 40,
                  color:
                    isActive
                      ? "#22D3EE"
                      : "#94A3B8",
                },

                "&.Mui-selected": {
                  backgroundColor:
                    "rgba(8,145,178,0.28)",
                },

                "&.Mui-selected:hover": {
                  backgroundColor:
                    "rgba(8,145,178,0.36)",
                },

                "&:hover": {
                  backgroundColor:
                    isActive
                      ? "rgba(8,145,178,0.36)"
                      : "rgba(34,211,238,0.08)",
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
                sx={{
                  minWidth: 0,
                }}
                primaryTypographyProps={{
                  fontWeight:
                    isActive ? 700 : 600,
                  color:
                    isActive
                      ? "#22D3EE"
                      : "#E5E7EB",
                }}
                secondaryTypographyProps={{
                  color:
                    isActive
                      ? "#BAE6FD"
                      : "#94A3B8",
                }}
              />
            </ListItemButton>
          );
        })}
      </List>
    </>
  );
}


export default function Sidebar() {
  const location = useLocation();

  const activeIdentityId =
    resolveActiveIdentityId(
      location.pathname,
    );

  const investigationRoute =
    activeIdentityId
      ? `/workspace/${activeIdentityId}`
      : null;

  const isInvestigationWorkspace =
    Boolean(
      activeIdentityId
      && location.pathname
        === investigationRoute,
    );

  const isAttackSimulation =
    Boolean(
      isInvestigationWorkspace
      && location.hash
        === "#attack-simulation",
    );


  const workspaceItems = [
    {
      label: "Executive Dashboard",
      icon: <DashboardIcon />,
      to: "/",
      active:
        location.pathname === "/"
        && !location.hash,
    },
    {
      label: "Select Identity",
      icon: <HubIcon />,
      to: "/#identity-selection",
      active:
        location.pathname === "/"
        && location.hash
          === "#identity-selection",
      secondary:
        "Choose from exposed identities",
    },
    {
      label: "Analyst Workspace",
      icon: <PsychologyIcon />,
      to: investigationRoute,
      disabled: !activeIdentityId,
      active:
        isInvestigationWorkspace
        && !isAttackSimulation,
      secondary:
        activeIdentityId
          ? "Resume active investigation"
          : "Select an identity first",
    },
    {
      label: "Attack Simulation",
      icon: <ScienceIcon />,
      to:
        activeIdentityId
          ? (
            `${investigationRoute}`
            + "#attack-simulation"
          )
          : null,
      disabled: !activeIdentityId,
      active: isAttackSimulation,
      secondary:
        activeIdentityId
          ? "Continue active investigation"
          : "Select an identity first",
    },
  ];


  const operationsItems = [
    {
      label: "Investigations",
      icon: <FolderIcon />,
      to: "/workspace",
      active:
        location.pathname
        === "/workspace",
      secondary:
        "Pending analyst decisions",
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
      active:
        location.pathname
        === "/platform/administration",
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
        minWidth: 280,
        flexShrink: 0,
        height: "100%",
        backgroundColor: "#111827",
        color: "#E5E7EB",
        borderRight:
          "1px solid rgba(255,255,255,.08)",
        overflowX: "hidden",
        overflowY: "auto",
        boxSizing: "border-box",
      }}
    >
      <SidebarSection
        title=""
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