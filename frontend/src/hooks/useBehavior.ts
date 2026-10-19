import { useEffect, useRef } from "react";
import type { BehaviorPayload } from "../types";

const RETURN_KEY = "autello_return_count";
const SAMPLE_MS = 800;
const MAX_HOTSPOTS = 80;

function bumpReturnCount(): number {
  const prev = Number(sessionStorage.getItem(RETURN_KEY) || "0");
  const next = prev + 1;
  sessionStorage.setItem(RETURN_KEY, String(next));
  return next;
}

export function useBehaviorTracker() {
  const started = useRef(Date.now());
  const clicks = useRef<{ id: string; at: number }[]>([]);
  const hotspots = useRef<
    { x: number; y: number; at: number }[]
  >([]);
  const returns = useRef(bumpReturnCount());
  const lastSample = useRef(0);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const el = e.target as HTMLElement | null;
      const id =
        el?.closest("[data-track]")?.getAttribute("data-track") ||
        el?.tagName ||
        "unknown";
      clicks.current.push({ id, at: Date.now() });
    };

    const onMove = (e: MouseEvent) => {
      const now = Date.now();
      if (now - lastSample.current < SAMPLE_MS) {
        return;
      }
      lastSample.current = now;
      const x = Math.round(
        (e.clientX / window.innerWidth) * 100,
      );
      const y = Math.round(
        (e.clientY / window.innerHeight) * 100,
      );
      hotspots.current.push({ x, y, at: now });
      if (hotspots.current.length > MAX_HOTSPOTS) {
        hotspots.current.shift();
      }
    };

    document.addEventListener("click", onClick, true);
    document.addEventListener("mousemove", onMove, {
      passive: true,
    });
    return () => {
      document.removeEventListener("click", onClick, true);
      document.removeEventListener("mousemove", onMove);
    };
  }, []);

  const snapshot = (leadId: string): BehaviorPayload => ({
    id: leadId,
    time_on_page_seconds: Math.round(
      (Date.now() - started.current) / 1000,
    ),
    buttons_clicked: [...clicks.current],
    cursor_hotspots: [...hotspots.current],
    return_count: returns.current,
    raw_metrics: {
      viewport: {
        w: window.innerWidth,
        h: window.innerHeight,
      },
      userAgent: navigator.userAgent,
    },
  });

  return { snapshot };
}
