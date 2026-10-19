import { useEffect, useState } from "react";
import {
  fetchAdminSettings,
  fetchServices,
} from "../api/client";
import { Hero } from "../components/Hero";
import { LeadForm } from "../components/LeadForm";
import type { AdminSettings, Service } from "../types";

export function HomePage() {
  const [services, setServices] = useState<Service[]>([]);
  const [settings, setSettings] =
    useState<AdminSettings | null>(null);

  useEffect(() => {
    void Promise.all([
      fetchServices(true),
      fetchAdminSettings(),
    ]).then(([svc, admin]) => {
      setServices(svc);
      setSettings(admin);
    });
  }, []);

  const scrollToForm = () => {
    document
      .getElementById("apply")
      ?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <main className="page">
      <Hero onCta={scrollToForm} />
      {settings && (
        <LeadForm services={services} settings={settings} />
      )}
    </main>
  );
}
