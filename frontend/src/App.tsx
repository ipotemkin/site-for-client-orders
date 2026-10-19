import { useEffect, useState } from "react";
import { fetchAdminSettings } from "./api/client";
import { Hero } from "./components/Hero";
import { LeadForm } from "./components/LeadForm";
import type { AdminSettings } from "./types";

export default function App() {
  const [settings, setSettings] = useState<AdminSettings | null>(
    null,
  );

  useEffect(() => {
    void fetchAdminSettings().then(setSettings);
  }, []);

  const scrollToForm = () => {
    document
      .getElementById("apply")
      ?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <main className="page">
      <Hero onCta={scrollToForm} />
      {settings && <LeadForm settings={settings} />}
    </main>
  );
}
