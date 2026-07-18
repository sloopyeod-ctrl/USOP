import { Routes, Route } from "react-router-dom";

import Layout from "./layout/Layout";
import ExecutiveDashboard from "./pages/ExecutiveDashboard";
import IdentityIntelligence from "./pages/IdentityIntelligence";
import IdentityExplorer from "./pages/IdentityExplorer";
import AnalystWorkspace from "./pages/AnalystWorkspace";
import PlatformAdministration from "./pages/PlatformAdministration";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ExecutiveDashboard />} />
        <Route path="/identity/:id" element={<IdentityIntelligence />} />
        <Route path="/explorer/:identityId" element={<IdentityExplorer />} />
        <Route path="/workspace/:identityId" element={<AnalystWorkspace />} />
        <Route
          path="/platform/administration"
          element={<PlatformAdministration />}
        />
      </Routes>
    </Layout>
  );
}