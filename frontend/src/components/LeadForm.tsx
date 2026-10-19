import {
  type ChangeEvent,
  type FormEvent,
  useEffect,
  useMemo,
  useState,
} from "react";
import { createBehavior, createLead } from "../api/client";
import { useBehaviorTracker } from "../hooks/useBehavior";
import type { AdminSettings, LeadPayload, Service } from "../types";
import "./LeadForm.css";

type Props = {
  services: Service[];
  settings: AdminSettings;
};

const empty: LeadPayload = {
  first_name: "",
  last_name: "",
  middle_name: "",
  email: "",
  phone: "",
  business_info: "",
  budget: "",
  contact_method: "телефон",
  convenient_time: "",
  comments: "",
  deadline: "",
  interested_product: "",
  task_type: "тюнинг / дооснащение",
};

function parseBudget(value: string | null, fallback: number) {
  const n = Number(String(value ?? "").replace(/\D/g, ""));
  return Number.isFinite(n) && n > 0 ? n : fallback;
}

function formatRub(n: number) {
  return new Intl.NumberFormat("ru-RU").format(n) + " ₽";
}

export function LeadForm({ services, settings }: Props) {
  const { snapshot } = useBehaviorTracker();
  const [form, setForm] = useState<LeadPayload>(empty);
  const [status, setStatus] = useState<
    "idle" | "loading" | "ok" | "error"
  >("idle");
  const [error, setError] = useState("");

  const min = useMemo(
    () => parseBudget(settings.budget_min, 200_000),
    [settings.budget_min],
  );
  const max = useMemo(
    () => parseBudget(settings.budget_max, 3_000_000),
    [settings.budget_max],
  );
  const mid = Math.round((min + max) / 2);

  useEffect(() => {
    setForm((prev) => ({
      ...prev,
      budget: prev.budget || String(mid),
      interested_product:
        prev.interested_product ||
        services[0]?.name ||
        "",
    }));
  }, [mid, services]);

  const set =
    (key: keyof LeadPayload) =>
    (
      e: ChangeEvent<
        HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
      >,
    ) => {
      setForm((prev) => ({ ...prev, [key]: e.target.value }));
    };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.interested_product) {
      setStatus("error");
      setError("Выберите услугу");
      return;
    }
    setStatus("loading");
    setError("");
    try {
      const lead = await createLead({
        ...form,
        middle_name: form.middle_name || null,
        email: form.email || null,
        phone: form.phone || null,
        task_type: form.interested_product,
      });
      await createBehavior(snapshot(lead.id));
      setStatus("ok");
      setForm({
        ...empty,
        budget: String(mid),
        interested_product: services[0]?.name || "",
      });
    } catch (err) {
      setStatus("error");
      setError(
        err instanceof Error
          ? err.message
          : "Не удалось отправить заявку",
      );
    }
  };

  if (status === "ok") {
    return (
      <section className="form-block" id="apply">
        <p className="form-block__eyebrow">Готово</p>
        <h2 className="form-block__title">Заявка принята</h2>
        <p className="form-block__hint">
          Мастер свяжется в удобное время и уточнит детали
          по автомобилю и объёму работ.
        </p>
      </section>
    );
  }

  return (
    <section className="form-block" id="apply">
      <p className="form-block__eyebrow">Заявка</p>
      <h2 className="form-block__title">
        Запись на услугу
      </h2>
      <p className="form-block__hint">
        Выберите направление и оставьте контакты — остальное
        обсудим лично.
      </p>

      <form className="lead-form" onSubmit={onSubmit}>
        <fieldset>
          <legend>Услуга</legend>
          <div className="service-grid">
            {services.map((s) => {
              const selected =
                form.interested_product === s.name;
              return (
                <button
                  key={s.id}
                  type="button"
                  className={
                    selected
                      ? "service-card is-active"
                      : "service-card"
                  }
                  data-track={`service-${s.id}`}
                  onClick={() =>
                    setForm((prev) => ({
                      ...prev,
                      interested_product: s.name,
                    }))
                  }
                >
                  <span className="service-card__name">
                    {s.name}
                  </span>
                  {s.description && (
                    <span className="service-card__desc">
                      {s.description}
                    </span>
                  )}
                  {(s.params.price_from ||
                    s.params.duration) && (
                    <span className="service-card__meta">
                      {s.params.price_from
                        ? `от ${formatRub(Number(s.params.price_from) || 0)}`
                        : ""}
                      {s.params.price_from &&
                      s.params.duration
                        ? " · "
                        : ""}
                      {s.params.duration || ""}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
          {services.length === 0 && (
            <p className="lead-form__error">
              Услуги пока не настроены. Загляните позже.
            </p>
          )}
        </fieldset>

        <fieldset>
          <legend>Контакты</legend>
          <div className="grid-3">
            <label>
              Имя
              <input
                required
                value={form.first_name}
                onChange={set("first_name")}
                autoComplete="given-name"
              />
            </label>
            <label>
              Фамилия
              <input
                required
                value={form.last_name}
                onChange={set("last_name")}
                autoComplete="family-name"
              />
            </label>
            <label>
              Отчество
              <input
                value={form.middle_name ?? ""}
                onChange={set("middle_name")}
              />
            </label>
          </div>
          <div className="grid-2">
            <label>
              Телефон
              <input
                required
                value={form.phone ?? ""}
                onChange={set("phone")}
                autoComplete="tel"
              />
            </label>
            <label>
              Email
              <input
                type="email"
                value={form.email ?? ""}
                onChange={set("email")}
                autoComplete="email"
              />
            </label>
          </div>
        </fieldset>

        <fieldset>
          <legend>Автомобиль</legend>
          <label>
            Марка, модель, год
            <input
              required
              value={form.business_info ?? ""}
              onChange={set("business_info")}
              placeholder="например, Porsche Cayenne 2022"
            />
          </label>
          <label>
            Желаемый срок
            <input
              value={form.deadline ?? ""}
              onChange={set("deadline")}
              placeholder="например, к апрелю"
            />
          </label>
        </fieldset>

        <fieldset>
          <legend>Бюджет</legend>
          <label className="budget">
            <span className="budget__value">
              {formatRub(Number(form.budget) || mid)}
            </span>
            <input
              type="range"
              min={min}
              max={max}
              step={50_000}
              value={Number(form.budget) || mid}
              onChange={set("budget")}
              data-track="budget-slider"
            />
            <span className="budget__range">
              {formatRub(min)} — {formatRub(max)}
            </span>
          </label>
        </fieldset>

        <fieldset>
          <legend>Связь</legend>
          <div className="grid-2">
            <label>
              Способ связи
              <select
                value={form.contact_method ?? ""}
                onChange={set("contact_method")}
              >
                <option value="телефон">Телефон</option>
                <option value="telegram">Telegram</option>
                <option value="whatsapp">WhatsApp</option>
                <option value="email">Email</option>
              </select>
            </label>
            <label>
              Удобное время
              <input
                value={form.convenient_time ?? ""}
                onChange={set("convenient_time")}
                placeholder="будни 12:00–18:00"
              />
            </label>
          </div>
          <label>
            Комментарий
            <textarea
              rows={3}
              value={form.comments ?? ""}
              onChange={set("comments")}
              placeholder="Пожелания по комплектации, цвету, срокам…"
            />
          </label>
        </fieldset>

        {status === "error" && (
          <p className="lead-form__error" role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          className="lead-form__submit"
          data-track="submit-lead"
          disabled={status === "loading" || services.length === 0}
        >
          {status === "loading" ? "Отправляем…" : "Отправить"}
        </button>
      </form>
    </section>
  );
}
