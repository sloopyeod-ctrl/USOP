import { Routes, Route } from "react-router-dom";

import Layout from "./layout/Layout";

import ExecutiveDashboard from "./pages/ExecutiveDashboard";
import IdentityIntelligence from "./pages/IdentityIntelligence";

export default function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<ExecutiveDashboard />} />

                <Route
                    path="/identity/:id"
                    element={<IdentityIntelligence />}
                />
            </Routes>
        </Layout>
    );
}