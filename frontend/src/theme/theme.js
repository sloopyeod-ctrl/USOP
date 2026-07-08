import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",

    primary: {
      main: "#22D3EE",
    },

    secondary: {
      main: "#5EEAD4",
    },

    error: {
      main: "#EF4444",
    },

    warning: {
      main: "#F59E0B",
    },

    info: {
      main: "#38BDF8",
    },

    success: {
      main: "#22C55E",
    },

    background: {
      default: "#0B1220",
      paper: "#111827",
    },

    text: {
      primary: "#E5E7EB",
      secondary: "#9CA3AF",
    },
  },

  typography: {
    fontFamily: "Inter, Roboto, Arial, sans-serif",
    h4: {
      letterSpacing: "-0.03em",
    },
    h5: {
      letterSpacing: "-0.02em",
    },
  },

  shape: {
    borderRadius: 14,
  },

  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          border: "1px solid #1F2937",
          boxShadow: "0 10px 25px rgba(0,0,0,0.25)",
        },
      },
    },

    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          boxShadow: "none",
        },
      },
    },

    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundImage: "none",
        },
      },
    },

    MuiLinearProgress: {
      styleOverrides: {
        root: {
          backgroundColor: "#1F2937",
        },
      },
    },
  },
});

export default theme;