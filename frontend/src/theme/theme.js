import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",

    primary: {
      main: "#00BCD4",
    },

    secondary: {
      main: "#64FFDA",
    },

    background: {
      default: "#0B0F14",
      paper: "#141B23",
    },
  },

  typography: {
    fontFamily: "Roboto, Arial, sans-serif",
  },
});

export default theme;