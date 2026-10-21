import {
  useEffect,
  useState,
  type FormEvent,
} from "react";
import { Link, Navigate } from "react-router-dom";
import { getBootstrapStatus } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import "./LoginPage.css";

export function LoginPage() {
  const { isAuthenticated, login, register } = useAuth();
  const [loginValue, setLoginValue] = useState("");
  const [password, setPassword] = useState("");
  const [registrationOpen, setRegistrationOpen] =
    useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    void getBootstrapStatus()
      .then((s) => setRegistrationOpen(s.registration_open))
      .catch(() => setRegistrationOpen(false));
  }, []);

  if (isAuthenticated) {
    return <Navigate to="/admin" replace />;
  }

  const runAuth = async (mode: "login" | "register") => {
    setError("");
    setBusy(true);
    try {
      if (mode === "register") {
        await register(loginValue.trim(), password);
      } else {
        await login(loginValue.trim(), password);
      }
    } catch (err) {
      const msg =
        err instanceof Error
          ? err.message
          : "Не удалось войти";
      setError(msg);
    } finally {
      setBusy(false);
    }
  };

  const onLogin = (event: FormEvent) => {
    event.preventDefault();
    void runAuth("login");
  };

  return (
    <main className="login page">
      <header className="login__head">
        <div>
          <p className="login__brand">Autello</p>
          <h1>Вход в админ-панель</h1>
          <p className="login__sub">
            Войдите с логином и паролем администратора.
          </p>
        </div>
        <Link className="login__link" to="/">
          На сайт
        </Link>
      </header>

      <form className="login__form" onSubmit={onLogin}>
        <label className="login__field">
          <span>Логин</span>
          <input
            type="text"
            autoComplete="username"
            value={loginValue}
            onChange={(e) => setLoginValue(e.target.value)}
            required
            minLength={1}
            maxLength={64}
            disabled={busy}
          />
        </label>
        <label className="login__field">
          <span>Пароль</span>
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            maxLength={128}
            disabled={busy}
          />
        </label>

        {error && <p className="login__error">{error}</p>}

        <div className="login__actions">
          <button
            type="submit"
            className="login__btn"
            disabled={busy}
          >
            Войти
          </button>
          {registrationOpen && (
            <button
              type="button"
              className="login__btn login__btn--secondary"
              disabled={busy}
              onClick={() => void runAuth("register")}
            >
              Зарегистрироваться
            </button>
          )}
        </div>
      </form>
    </main>
  );
}
