import {
  Box,
  Toolbar,
} from "@mui/material";

import Header from "./Header";
import Sidebar from "./Sidebar";


export default function Layout({
  children,
}) {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundColor:
          "background.default",
      }}
    >
      <Header />

      <Toolbar />

      <Box
        sx={{
          display: "flex",
          minHeight:
            "calc(100vh - 64px)",
        }}
      >
        <Sidebar />

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            minWidth: 0,
            p: 3,
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}