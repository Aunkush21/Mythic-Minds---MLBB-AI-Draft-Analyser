import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { AppShell } from "@/components/layout/AppShell";
import { PageTransition } from "@/components/common/PageTransition";
import { LandingPage } from "@/pages/LandingPage";
import { DraftRoomPage } from "@/pages/DraftRoomPage";
import { HeroCompendiumPage } from "@/pages/HeroCompendiumPage";
import { HeroDetailPage } from "@/pages/HeroDetailPage";
import { BuildExplorerPage } from "@/pages/BuildExplorerPage";
import { MetaDashboardPage } from "@/pages/MetaDashboardPage";

function App() {
  const location = useLocation();

  return (
    <AppShell>
      <AnimatePresence mode="wait" initial={false}>
        <PageTransition key={location.pathname}>
          <Routes location={location}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/draft" element={<DraftRoomPage />} />
            <Route path="/heroes" element={<HeroCompendiumPage />} />
            <Route path="/heroes/:heroId" element={<HeroDetailPage />} />
            <Route path="/builds" element={<BuildExplorerPage />} />
            <Route path="/meta" element={<MetaDashboardPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </PageTransition>
      </AnimatePresence>
    </AppShell>
  );
}

export default App;
