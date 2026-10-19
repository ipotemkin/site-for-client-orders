import {
  type ChangeEvent,
  type FormEvent,
  useEffect,
  useMemo,
  useState,
} from "react";
import { createBehavior, createLead } from "../api/client";
import { useBehaviorTracker } from "../hooks/useBehavior";
import type { AdminSettings, LeadPayload } from "../types";
import "./LeadForm.css";

type Props = {
  settings: AdminSettings;
};

const empty: LeadPayload = {
  first_name: "",
  last_name: "",
  middle_name: "",
  email: "",
  phone: "",
  business_info: "",
  niche: "",
  company_size: "",
  task_volume: "",
  need_volume: "",
  role: "руководитель",
  budget: "",
  contact_method: "телефон",
  convenient_time: "",
  comments: "",
  deadline: "",
  task_type: "",
  interested_product: "",
};

function parseBudget(value: string | null, fallback: number) {
  const n = Number(String(value ?? "").replace(/\D/g, ""));
  return Number.isFinite(n) && n > 0 ? n : fallback;
}

function formatRub(n: number) {
  return new Intl.NumberFormat("ru-RU").format(n) + " ₽";
}

export function LeadForm({ settings }: Props) {
  const { snapshot } = useBehaviorTracker();
  const [form, setForm] = useState<LeadPayload>(empty);
  const [status, setStatus] = useState<
    "idle" | "loading" | "ok" | "error"
  >("idle");
  const [error, setError] = useState("");

  const min = useMemo(
    () => parseBudget(settings.budget_min, 300_000),
    [settings.budget_min],
  );
  const max = useMemo(
    () => parseBudget(settings.budget_max, 5_000_000),
    [settings.budget_max],
  );
  const mid = Math.round((min + max) / 2);

  useEffect(() => {
    setForm((prev) => ({
      ...prev,
      budget: String(mid),
      interested_product:
        prev.interested_product ||
        settings.services[0] ||
        "",
    }));
  }, [mid, settings.services]);

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
    setStatus("loading");
    setError("");
    try {
      const lead = await createLead({
        ...form,
        middle_name: form.middle_name || null,
        email: form.email || null,
        phone: form.phone || null,
      });
      await createBehavior(snapshot(lead.id));
      setStatus("ok");
      setForm({ ...empty, budget: String(mid) });
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
          Мы свяжемся в удобное для вас время — без лишних писем.
        </p>
      </section>
    );
  }

  return (
    <section className="form-block" id="apply">
      <p className="form-block__eyebrow">Заявка</p>
      <h2 className="form-block__title">Расскажите о задаче</h2>
      <p className="form-block__hint">
        Несколько точных ответов — достаточно, чтобы начать.
      </p>

      <form className="lead-form" onSubmit={onSubmit}>
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
              Email
              <input
                type="email"
                value={form.email ?? ""}
                onChange={set("email")}
                autoComplete="email"
              />
            </label>
            <label>
              Телефон
              <input
                value={form.phone ?? ""}
                onChange={set("phone")}
                autoComplete="tel"
              />
            </label>
          </div>
        </fieldset>

        <fieldset>
          <legend>Бизнес</legend>
          <div className="grid-2">
            <label>
              Ниша
              <input
                value={form.niche ?? ""}
                onChange={set("niche")}
              />
            </label>
            <label>
              Размер компании
              <input
                value={form.company_size ?? ""}
                onChange={set("company_size")}
                placeholder="например, 50–200 человек"
              />
            </label>
          </div>
          <label>
            О бизнесе
            <textarea
              rows={3}
              value={form.business_info ?? ""}
              onChange={set("business_info")}
            />
          </label>
          <label>
            Кто вы
            <select
              value={form.role ?? ""}
              onChange={set("role")}
            >
              <option value="руководитель">Руководитель</option>
              <option value="сотрудник">Сотрудник</option>
            </select>
          </label>
        </fieldset>

        <fieldset>
          <legend>Задача</legend>
          <div className="grid-2">
            <label>
              Тип задачи
              <input
                value={form.task_type ?? ""}
                onChange={set("task_type")}
              />
            </label>
            <label>
              Интересующий продукт
              <select
                value={form.interested_product ?? ""}
                onChange={set("interested_product")}
              >
                {settings.services.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="grid-2">
            <label>
              Объём задачи
              <input
                value={form.task_volume ?? ""}
                onChange={set("task_volume")}
              />
            </label>
            <label>
              Объём потребности
              <input
                value={form.need_volume ?? ""}
                onChange={set("need_volume")}
              />
            </label>
          </div>
          <label>
            Срок результата
            <input
              value={form.deadline ?? ""}
              onChange={set("deadline")}
              placeholder="например, до конца квартала"
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
                <option value="email">Email</option>
              </select>
            </label>
            <label>
              Удобное время
              <input
                value={form.convenient_time ?? ""}
                onChange={set("convenient_time")}
                placeholder="будни 11:00–16:00"
              />
            </label>
          </div>
          <label>
            Комментарий
            <textarea
              rows={3}
              value={form.comments ?? ""}
              onChange={set("comments")}
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
          disabled={status === "loading"}
        >
          {status === "loading" ? "Отправляем…" : "Отправить"}
        </button>
      </form>
    </section>
  );
}
