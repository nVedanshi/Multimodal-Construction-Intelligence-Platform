import { useState, useEffect } from "react";
import Sidebar from "./components/layout/Sidebar";
import Header from "./components/layout/Header";
import Dashboard from "./pages/Dashboard";
import SafetyMonitor from "./pages/SafetyMonitor";
import CrackDetection from "./pages/CrackDetection";
import ProjectPlanner from "./pages/ProjectPlanner";
import RealEstateValuation from "./pages/RealEstateValuation";
import DailySiteAssistant from "./pages/DailySiteAssistant";
import WeatherAdvisor from "./pages/WeatherAdvisor";
import KnowledgeBase from "./pages/KnowledgeBase";
import KnowledgeAssistant from "./pages/KnowledgeAssistant";

const PAGES = {
  dashboard: Dashboard,
  safety: SafetyMonitor,
  crack: CrackDetection,
  planning: ProjectPlanner,
  valuation: RealEstateValuation,
  daily: DailySiteAssistant,
  weather: WeatherAdvisor,
  knowledgebase: KnowledgeBase,
  chatbot: KnowledgeAssistant,
};

const PAGE_TITLES = {
  dashboard: "Dashboard",
  safety: "Site Safety Monitor",
  crack: "Structural Crack Detection",
  planning: "Project Planner",
  valuation: "Real Estate Valuation",
  daily: "Daily Site Assistant",
  weather: "Weather Advisor",
  knowledgebase: "Knowledge Base",
  chatbot: "Construction Chatbot",
};

export default function App() {
  const [active, setActive] = useState("dashboard");

  useEffect(() => {
    const onHashChange = () => {
      const hash = window.location.hash.replace("#/", "");
      if (hash && PAGES[hash]) {
        setActive(hash);
      } else {
        setActive("dashboard");
      }
    };
    window.addEventListener("hashchange", onHashChange);
    onHashChange();
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const Page = PAGES[active] || Dashboard;
  const title = PAGE_TITLES[active] || "Dashboard";

  return (
    <div className="app">
      <Sidebar active={active} onSelect={setActive} />
      <div className="workspace">
        <Header title={title} />
        <div className="page">
          <Page />
        </div>
      </div>
    </div>
  );
}
