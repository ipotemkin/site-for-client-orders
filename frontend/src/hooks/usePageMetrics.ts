import { useEffect, useRef } from "react";
import { postBehaviorMetric } from "../api/client";

const TICK_MS = 1000;
const MAX_CURSOR_POINTS = 900;

type CursorPoint = { x: number; y: number };

/**
 * Collects time / clicks / cursor and POSTs every second
 * to /api/behavior-metrics/.
 */
export function usePageMetrics() {
  const started = useRef(Date.now());
  const cursor = useRef<CursorPoint>({ x: 50, y: 50 });
  const positions = useRef<CursorPoint[]>([]);
  const clicks = useRef<Record<string, number>>({});
  const sending = useRef(false);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const w = window.innerWidth || 1;
      const h = window.innerHeight || 1;
      cursor.current = {
        x: Math.round((e.clientX / w) * 100),
        y: Math.round((e.clientY / h) * 100),
      };
    };

    const onClick = (e: MouseEvent) => {
      const el = e.target as HTMLElement | null;
      const id =
        el?.closest("[data-track]")?.getAttribute(
          "data-track",
        ) ||
        el?.tagName?.toLowerCase() ||
        "unknown";
      clicks.current[id] = (clicks.current[id] || 0) + 1;
    };

    const tick = async () => {
      positions.current.push({ ...cursor.current });
      if (positions.current.length > MAX_CURSOR_POINTS) {
        positions.current.shift();
      }
      if (sending.current) {
        return;
      }
      sending.current = true;
      const timeOnPage = Math.max(
        1,
        Math.round((Date.now() - started.current) / 1000),
      );
      try {
        await postBehaviorMetric({
          application_id: 0,
          time_on_page: timeOnPage,
          buttons_clicked: JSON.stringify(clicks.current),
          cursor_positions: JSON.stringify(
            positions.current,
          ),
          return_frequency: 0,
        });
      } catch {
        // Ignore network blips; next tick retries.
      } finally {
        sending.current = false;
      }
    };

    document.addEventListener("mousemove", onMove, {
      passive: true,
    });
    document.addEventListener("click", onClick, true);
    const id = window.setInterval(() => {
      void tick();
    }, TICK_MS);
    void tick();

    return () => {
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("click", onClick, true);
      window.clearInterval(id);
    };
  }, []);
}
