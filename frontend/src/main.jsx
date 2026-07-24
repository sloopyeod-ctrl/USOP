import React from "react";
import ReactDOM from "react-dom/client";
import {
  BrowserRouter,
} from "react-router-dom";
import {
  ThemeProvider,
} from "@mui/material/styles";

import App from "./App";
import OrganizationProvider from
  "./context/OrganizationContext";
import theme from "./theme/theme";


ReactDOM.createRoot(
  document.getElementById("root"),
).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <OrganizationProvider>
          <App />
        </OrganizationProvider>
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>,
);