import { useEffect, useState } from "react";
import { fetchLeadQueue } from "../api/client";
import type {
  LeadQueueStats,
  ScoredLead,
} from "../types";
import "./LeadsIntelPanel.css";

function formatDate(value?: string) {
  if (!value) {
    return "—";
  }
  return new Date(value).toLocaleString("ru-RU");
}

function formatBudget(raw?: string | null) {
  if (!raw) {
    return "—";
  }
  const n = Number(String(raw).replace(/\D/g, ""));
  if (!Number.isFinite(n) || n <= 0) {
    return raw;
  }
  return `${n.toLocaleString("ru-RU")} ₽`;
}

function fullName(lead: ScoredLead) {
  return [lead.last_name, lead.first_name, lead.middle_name]
    .filter(Boolean)
    .join(" ");
}

function StatsCards({ stats }: { stats: LeadQueueStats }) {
  return (
    <div className="leads-intel__stats">
      <article>
        <span>Всего</span>
        <strong>{stats.total}</strong>
      </article>
      <article className="is-hot">
        <span>Горячие</span>
        <strong>{stats.hot}</strong>
      </article>
      <article className="is-warm">
        <span>Тёплые</span>
        <strong>{stats.warm}</strong>
      </article>
      <article className="is-cold">
        <span>Холодные</span>
        <strong>{stats.cold}</strong>
      </article>
      <article className="is-urgent">
        <span>Срочные</span>
        <strong>{stats.urgent}</strong>
      </article>
      <article>
        <span>Перс. менеджер</span>
        <strong>{stats.with_manager}</strong>
      </article>
      <article>
        <span>Средний score</span>
        <strong>{stats.avg_score}</strong>
      </article>
    </div>
  );
}

function LeadDetail({
  lead,
  onClose,
}: {
  lead: ScoredLead;
  onClose: () => void;
}) {
  const a = lead.analysis;
  const tel = lead.phone
    ? `tel:${lead.phone.replace(/\s/g, "")}`
    : null;
  const mail = lead.email ? `mailto:${lead.email}` : null;

  return (
    <div
      className="lead-detail"
      role="dialog"
      aria-modal="true"
    >
      <div className="lead-detail__panel">
        <header className="lead-detail__head">
          <div>
            <p className="lead-detail__eyebrow">
              Карточка заявки
            </p>
            <h3>{fullName(lead)}</h3>
          </div>
          <button type="button" onClick={onClose}>
            Закрыть
          </button>
        </header>

        <div className="lead-detail__badges">
          <span className={`temp temp--${a.temperature}`}>
            {a.temperature_label} · {a.score}
          </span>
          {a.is_urgent && (
            <span className="badge badge--urgent">
              Срочно
            </span>
          )}
          {a.needs_personal_manager && (
            <span className="badge">Перс. менеджер</span>
          )}
          <span className="badge badge--dept">
            {a.department_label}
          </span>
        </div>

        <p className="lead-detail__verdict">
          {a.worth_time_label}
        </p>
        {a.reasons.length > 0 && (
          <ul className="lead-detail__reasons">
            {a.reasons.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        )}

        <dl className="lead-detail__grid">
          <div>
            <dt>Контакты</dt>
            <dd>
              {[lead.phone, lead.email]
                .filter(Boolean)
                .join(" · ") || "—"}
            </dd>
          </div>
          <div>
            <dt>Связь</dt>
            <dd>
              {[lead.contact_method, lead.convenient_time]
                .filter(Boolean)
                .join(", ") || "—"}
            </dd>
          </div>
          <div>
            <dt>Авто / объект</dt>
            <dd>{lead.business_info || "—"}</dd>
          </div>
          <div>
            <dt>Услуга</dt>
            <dd>
              {lead.interested_product ||
                lead.task_type ||
                "—"}
            </dd>
          </div>
          <div>
            <dt>Бюджет</dt>
            <dd>{formatBudget(lead.budget)}</dd>
          </div>
          <div>
            <dt>Срок</dt>
            <dd>{lead.deadline || "—"}</dd>
          </div>
          <div>
            <dt>Ниша</dt>
            <dd>{lead.niche || "—"}</dd>
          </div>
          <div>
            <dt>Компания / роль</dt>
            <dd>
              {[lead.company_size, lead.role]
                .filter(Boolean)
                .join(" · ") || "—"}
            </dd>
          </div>
          <div>
            <dt>Объём</dt>
            <dd>
              {[lead.task_volume, lead.need_volume]
                .filter(Boolean)
                .join(" · ") || "—"}
            </dd>
          </div>
          <div>
            <dt>Создано</dt>
            <dd>{formatDate(lead.created_at)}</dd>
          </div>
        </dl>

        {lead.comments && (
          <p className="lead-detail__comments">
            {lead.comments}
          </p>
        )}

        <div className="lead-detail__actions">
          {tel && (
            <a className="lead-detail__cta" href={tel}>
              Позвонить
            </a>
          )}
          {mail && (
            <a
              className="lead-detail__cta lead-detail__cta--ghost"
              href={mail}
            >
              Написать
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

export function LeadsIntelPanel() {
  const [items, setItems] = useState<ScoredLead[]>([]);
  const [stats, setStats] = useState<LeadQueueStats | null>(
    null,
  );
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<ScoredLead | null>(
    null,
  );

  useEffect(() => {
    void fetchLeadQueue()
      .then((data) => {
        setItems(data.items);
        setStats(data.stats);
      })
      .catch((err) => {
        setError(
          err instanceof Error
            ? err.message
            : "Не удалось загрузить заявки",
        );
      });
  }, []);

  return (
    <section className="admin__section leads-intel">
      <h2>Очередь заявок · интеллект</h2>
      <p className="leads-intel__sub">
        Срочные и горячие — сверху. Откройте карточку,
        чтобы увидеть отдел, менеджера и контакты.
      </p>

      {error && <p className="leads-intel__error">{error}</p>}
      {stats && <StatsCards stats={stats} />}

      {stats && Object.keys(stats.by_department).length > 0 && (
        <p className="leads-intel__deps">
          По отделам:{" "}
          {Object.entries(stats.by_department)
            .map(([k, v]) => `${k} — ${v}`)
            .join(" · ")}
        </p>
      )}

      <div className="admin__table-wrap">
        <table className="admin__table leads-intel__table">
          <thead>
            <tr>
              <th>Приоритет</th>
              <th>Клиент</th>
              <th>Услуга / бюджет</th>
              <th>Отдел</th>
              <th>Вердикт</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {items.map((lead) => {
              const a = lead.analysis;
              return (
                <tr
                  key={lead.id}
                  className={
                    a.is_urgent ? "is-urgent-row" : undefined
                  }
                >
                  <td>
                    <span
                      className={`temp temp--${a.temperature}`}
                    >
                      {a.temperature_label}
                    </span>
                    <div className="leads-intel__score">
                      score {a.score}
                      {a.is_urgent ? " · срочно" : ""}
                    </div>
                  </td>
                  <td>
                    <strong>{fullName(lead)}</strong>
                    <div className="leads-intel__muted">
                      {[lead.phone, lead.email]
                        .filter(Boolean)
                        .join(" · ") || "нет контактов"}
                    </div>
                  </td>
                  <td>
                    {lead.interested_product ||
                      lead.task_type ||
                      "—"}
                    <div className="leads-intel__muted">
                      {formatBudget(lead.budget)}
                      {lead.deadline
                        ? ` · ${lead.deadline}`
                        : ""}
                    </div>
                  </td>
                  <td>
                    {a.department_label}
                    {a.needs_personal_manager && (
                      <div className="leads-intel__muted">
                        нужен перс. менеджер
                      </div>
                    )}
                  </td>
                  <td className="leads-intel__verdict-cell">
                    {a.worth_time_label}
                  </td>
                  <td>
                    <button
                      type="button"
                      className="leads-intel__open"
                      onClick={() => setSelected(lead)}
                    >
                      Открыть
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {items.length === 0 && !error && (
          <p className="admin__empty">Заявок пока нет</p>
        )}
      </div>

      {selected && (
        <LeadDetail
          lead={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </section>
  );
}
