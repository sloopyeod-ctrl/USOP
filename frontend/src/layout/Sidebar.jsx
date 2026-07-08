import { Drawer, List, ListItemButton, ListItemText, Toolbar } from "@mui/material";
import { Link, useLocation } from "react-router-dom";

const drawerWidth = 240;

const navItems = [
  { label: "Dashboard", path: "/" },
  { label: "Identity Intelligence", path: "/identity/ed8b8386-22fe-4d95-bf82-7071163bb4d0" },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        "& .MuiDrawer-paper": {
          width: drawerWidth,
          backgroundColor: "#101820",
          borderRight: "1px solid #1F2933",
        },
      }}
    >
      <Toolbar />

      <List>
        {navItems.map((item) => (
          <ListItemButton
            key={item.path}
            component={Link}
            to={item.path}
            selected={location.pathname === item.path}
          >
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  );
}