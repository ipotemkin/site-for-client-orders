import "./Hero.css";

type Props = {
  onCta: () => void;
};

export function Hero({ onCta }: Props) {
  return (
    <header className="hero">
      <div className="hero__glow" aria-hidden="true" />
      <p className="hero__brand">Autello</p>
      <h1 className="hero__title">
        Тихий рост для тех,
        <br />
        кто уже впереди
      </h1>
      <p className="hero__lead">
        Персональный консалтинг без шума. Одна заявка —
        и мы соберём решение под ваш масштаб.
      </p>
      <button
        type="button"
        className="hero__cta"
        data-track="hero-cta"
        onClick={onCta}
      >
        Оставить заявку
      </button>
    </header>
  );
}
