import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  createService,
  deleteService,
  fetchAdminSettings,
  fetchServices,
  saveAdminSettings,
  updateService,
} from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { LeadsIntelPanel } from "../components/LeadsIntelPanel";
import { StatsModal } from "../components/StatsModal";
import type { AdminSettings, Service } from "../types";
import "./AdminPage.css";

type Draft = {
  id?: number;
  name: string;
  description: string;
  price_from: string;
  duration: string;
  sort_order: string;
  is_active: boolean;
};

const blankDraft = (): Draft => ({
  name: "",
  description: "",
  price_from: "",
  duration: "",
  sort_order: "0",
  is_active: true,
});

function toDraft(s: Service): Draft {
  return {
    id: s.id,
    name: s.name,
    description: s.description || "",
    price_from: s.params.price_from || "",
    duration: s.params.duration || "",
    sort_order: String(s.sort_order),
    is_active: s.is_active,
  };
}

export function AdminPage() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [services, setServices] = useState<Service[]>([]);
  const [settings, setSettings] =
    useState<AdminSettings | null>(null);
  const [draft, setDraft] = useState<Draft>(blankDraft());
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [statsOpen, setStatsOpen] = useState(false);

  const onLogout = () => {
    logout();
    navigate("/admin/login", { replace: true });
  };

  const reload = useCallback(async () => {
    const [svc, admin] = await Promise.all([
      fetchServices(false),
      fetchAdminSettings(),
    ]);
    setServices(svc);
    setSettings(admin);
  }, []);

  useEffect(() => {
    void reload().catch(() => {
      setMessage("Не удалось загрузить данные");
    });
  }, [reload]);

  const onSaveService = async () => {
    if (!draft.name.trim()) {
      setMessage("Укажите название услуги");
      return;
    }
    setBusy(true);
    setMessage("");
    const payload = {
      name: draft.name.trim(),
      description: draft.description.trim() || null,
      params: {
        price_from: draft.price_from.trim() || undefined,
        duration: draft.duration.trim() || undefined,
      },
      sort_order: Number(draft.sort_order) || 0,
      is_active: draft.is_active,
    };
    try {
      if (draft.id) {
        await updateService(draft.id, payload);
      } else {
        await createService(payload);
      }
      setDraft(blankDraft());
      await reload();
      setMessage("Услуга сохранена");
    } catch (err) {
      setMessage(
        err instanceof Error ? err.message : "Ошибка сохранения",
      );
    } finally {
      setBusy(false);
    }
  };

  const onDelete = async (id: number) => {
    if (!window.confirm("Удалить услугу?")) {
      return;
    }
    setBusy(true);
    try {
      await deleteService(id);
      if (draft.id === id) {
        setDraft(blankDraft());
      }
      await reload();
      setMessage("Услуга удалена");
    } catch (err) {
      setMessage(
        err instanceof Error ? err.message : "Ошибка удаления",
      );
    } finally {
      setBusy(false);
    }
  };

  const onSaveBudget = async () => {
    if (!settings) {
      return;
    }
    setBusy(true);
    try {
      const saved = await saveAdminSettings({
        ...settings,
        services: [],
      });
      setSettings(saved);
      setMessage("Диапазон бюджета обновлён");
    } catch (err) {
      setMessage(
        err instanceof Error ? err.message : "Ошибка бюджета",
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="admin page">
      <header className="admin__head">
        <div>
          <p className="admin__brand">Autello</p>
          <h1>Админ-панель</h1>
          <p className="admin__sub">
            Услуги ателье и заявки клиентов.
          </p>
        </div>
        <div className="admin__head-actions">
          <button
            type="button"
            className="admin__link admin__link--ghost"
            onClick={() => setStatsOpen(true)}
          >
            Статистика
          </button>
          <button
            type="button"
            className="admin__link admin__link--ghost"
            onClick={onLogout}
          >
            Выйти
          </button>
          <Link className="admin__link" to="/">
            На сайт
          </Link>
        </div>
      </header>

      <StatsModal
        open={statsOpen}
        onClose={() => setStatsOpen(false)}
      />

      {message && <p className="admin__toast">{message}</p>}

      <section className="admin__section">
        <h2>Услуги</h2>
        <div className="admin__layout">
          <div className="admin__list">
            {services.map((s) => (
              <article key={s.id} className="admin__item">
                <div>
                  <strong>{s.name}</strong>
                  <p>{s.description || "Без описания"}</p>
                  <span>
                    {s.is_active ? "активна" : "скрыта"}
                    {s.params.price_from
                      ? ` · от ${s.params.price_from} ₽`
                      : ""}
                    {s.params.duration
                      ? ` · ${s.params.duration}`
                      : ""}
                  </span>
                </div>
                <div className="admin__item-actions">
                  <button
                    type="button"
                    onClick={() => setDraft(toDraft(s))}
                  >
                    Изменить
                  </button>
                  <button
                    type="button"
                    className="is-danger"
                    onClick={() => void onDelete(s.id)}
                  >
                    Удалить
                  </button>
                </div>
              </article>
            ))}
            {services.length === 0 && (
              <p className="admin__empty">Услуг пока нет</p>
            )}
          </div>

          <div className="admin__editor">
            <h3>
              {draft.id ? "Редактирование" : "Новая услуга"}
            </h3>
            <label>
              Название
              <input
                value={draft.name}
                onChange={(e) =>
                  setDraft((d) => ({
                    ...d,
                    name: e.target.value,
                  }))
                }
              />
            </label>
            <label>
              Описание
              <textarea
                rows={3}
                value={draft.description}
                onChange={(e) =>
                  setDraft((d) => ({
                    ...d,
                    description: e.target.value,
                  }))
                }
              />
            </label>
            <div className="admin__row">
              <label>
                Цена от, ₽
                <input
                  value={draft.price_from}
                  onChange={(e) =>
                    setDraft((d) => ({
                      ...d,
                      price_from: e.target.value,
                    }))
                  }
                />
              </label>
              <label>
                Срок
                <input
                  value={draft.duration}
                  onChange={(e) =>
                    setDraft((d) => ({
                      ...d,
                      duration: e.target.value,
                    }))
                  }
                  placeholder="7–14 дней"
                />
              </label>
            </div>
            <div className="admin__row">
              <label>
                Порядок
                <input
                  value={draft.sort_order}
                  onChange={(e) =>
                    setDraft((d) => ({
                      ...d,
                      sort_order: e.target.value,
                    }))
                  }
                />
              </label>
              <label className="admin__check">
                <input
                  type="checkbox"
                  checked={draft.is_active}
                  onChange={(e) =>
                    setDraft((d) => ({
                      ...d,
                      is_active: e.target.checked,
                    }))
                  }
                />
                Показывать на сайте
              </label>
            </div>
            <div className="admin__item-actions">
              <button
                type="button"
                disabled={busy}
                onClick={() => void onSaveService()}
              >
                Сохранить
              </button>
              <button
                type="button"
                onClick={() => setDraft(blankDraft())}
              >
                Сбросить
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="admin__section">
        <h2>Бюджет на форме</h2>
        {settings && (
          <div className="admin__row admin__budget">
            <label>
              Минимум
              <input
                value={settings.budget_min ?? ""}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    budget_min: e.target.value,
                  })
                }
              />
            </label>
            <label>
              Максимум
              <input
                value={settings.budget_max ?? ""}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    budget_max: e.target.value,
                  })
                }
              />
            </label>
            <button
              type="button"
              disabled={busy}
              onClick={() => void onSaveBudget()}
            >
              Сохранить бюджет
            </button>
          </div>
        )}
      </section>

      <LeadsIntelPanel />
    </main>
  );
}
