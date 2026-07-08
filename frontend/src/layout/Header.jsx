import { AppBar, Toolbar, Typography, Box } from "@mui/material";

export default function Header() {
  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: 1201,
        backgroundColor: "#0B0F14",
        borderBottom: "1px solid #1F2933",
      }}
    >
      <Toolbar>
        <Typography variant="h6" fontWeight={700}>
          USOP
        </Typography>

        <Typography sx={{ ml: 2, color: "text.secondary" }}>
          Unified Security Operations Platform
        </Typography>

        <Box sx={{ flexGrow: 1 }} />

        <Typography variant="body2" color="text.secondary">
          v1 Dashboard
        </Typography>
      </Toolbar>
    </AppBar>
  );
}