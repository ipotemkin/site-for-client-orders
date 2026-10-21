import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./NotFoundPage.css";

const REDIRECT_SEC = 5;

export function NotFoundPage() {
  const navigate = useNavigate();
  const [left, setLeft] = useState(REDIRECT_SEC);

  useEffect(() => {
    const tick = window.setInterval(() => {
      setLeft((n) => Math.max(0, n - 1));
    }, 1000);
    const go = window.setTimeout(() => {
      navigate("/", { replace: true });
    }, REDIRECT_SEC * 1000);
    return () => {
      window.clearInterval(tick);
      window.clearTimeout(go);
    };
  }, [navigate]);

  return (
    <main className="not-found page">
      <p className="not-found__brand">Autello</p>
      <p className="not-found__code">404</p>
      <h1>Страница не найдена</h1>
      <p className="not-found__text">
        Такой страницы нет. Через {left}{" "}
        {left === 1 ? "секунду" : left < 5 ? "секунды" : "секунд"}{" "}
        вы вернётесь на главную.
      </p>
      <Link className="not-found__link" to="/">
        На главную сейчас
      </Link>
    </main>
  );
}
