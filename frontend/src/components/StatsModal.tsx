import { useEffect, useState } from "react";
import { fetchBehaviorStats } from "../api/client";
import type { BehaviorStats, HeatPoint } from "../types";
import "./StatsModal.css";

type Props = {
  open: boolean;
  onClose: () => void;
};

function formatDuration(sec: number) {
  const s = Math.max(0, Math.round(sec));
  const m = Math.floor(s / 60);
  const r = s % 60;
  if (m <= 0) {
    return `${r} с`;
  }
  return `${m} мин ${r} с`;
}

function Heatmap({ points }: { points: HeatPoint[] }) {
  const maxW = Math.max(1, ...points.map((p) => p.weight));
  return (
    <svg
      className="stats-modal__heat"
      viewBox="0 0 100 100"
      role="img"
      aria-label="Хитмап курсора"
    >
      <rect
        x="0"
        y="0"
        width="100"
        height="100"
        className="stats-modal__heat-bg"
      />
      {points.map((p, i) => {
        const t = p.weight / maxW;
        const r = 1.2 + t * 4.5;
        return (
          <circle
            key={`${p.x}-${p.y}-${i}`}
            cx={p.x}
            cy={p.y}
            r={r}
            fill={`rgba(0, 113, 227, ${0.15 + t * 0.7})`}
          />
        );
      })}
    </svg>
  );
}

export function StatsModal({ open, onClose }: Props) {
  const [stats, setStats] = useState<BehaviorStats | null>(
    null,
  );
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) {
      return;
    }
    setLoading(true);
    setError("");
    void fetchBehaviorStats()
      .then(setStats)
      .catch((err) => {
        setError(
          err instanceof Error
            ? err.message
            : "Не удалось загрузить статистику",
        );
      })
      .finally(() => setLoading(false));
  }, [open]);

  useEffect(() => {
    if (!open) {
      return;
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="stats-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="stats-modal-title"
    >
      <div className="stats-modal__panel">
        <header className="stats-modal__head">
          <div>
            <p className="stats-modal__eyebrow">
              Поведение на странице заявки
            </p>
            <h2 id="stats-modal-title">
              Статистика пользователей
            </h2>
          </div>
          <button
            type="button"
            className="stats-modal__close"
            onClick={onClose}
          >
            Закрыть
          </button>
        </header>

        {loading && (
          <p className="stats-modal__hint">Загрузка…</p>
        )}
        {error && (
          <p className="stats-modal__error">{error}</p>
        )}

        {stats && (
          <>
            <section className="stats-modal__times">
              <article>
                <h3>День</h3>
                <p>
                  Среднее макс.:{" "}
                  <strong>
                    {formatDuration(stats.day.avg_seconds)}
                  </strong>
                </p>
                <p>
                  Максимум:{" "}
                  <strong>
                    {formatDuration(stats.day.max_seconds)}
                  </strong>
                </p>
              </article>
              <article>
                <h3>Неделя</h3>
                <p>
                  Среднее макс.:{" "}
                  <strong>
                    {formatDuration(stats.week.avg_seconds)}
                  </strong>
                </p>
                <p>
                  Максимум:{" "}
                  <strong>
                    {formatDuration(stats.week.max_seconds)}
                  </strong>
                </p>
              </article>
              <article>
                <h3>Месяц</h3>
                <p>
                  Среднее макс.:{" "}
                  <strong>
                    {formatDuration(stats.month.avg_seconds)}
                  </strong>
                </p>
                <p>
                  Максимум:{" "}
                  <strong>
                    {formatDuration(stats.month.max_seconds)}
                  </strong>
                </p>
              </article>
            </section>

            <section className="stats-modal__map-block">
              <h3>Хитмап курсора</h3>
              <p className="stats-modal__hint">
                Кружки — зоны, где чаще бывает курсор
                (ярче и крупнее = популярнее).
              </p>
              {stats.heatmap.length === 0 ? (
                <p className="stats-modal__hint">
                  Пока нет данных курсора.
                </p>
              ) : (
                <Heatmap points={stats.heatmap} />
              )}
            </section>
          </>
        )}
      </div>
    </div>
  );
}
