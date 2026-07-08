import { Box, Toolbar } from "@mui/material";
import Header from "./Header";
import Sidebar from "./Sidebar";

const drawerWidth = 240;

export default function Layout({ children }) {
  return (
    <Box sx={{ display: "flex", minHeight: "100vh", backgroundColor: "background.default" }}>
      <Header />
      <Sidebar />

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ml: `${drawerWidth}px`,
          p: 3,
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}