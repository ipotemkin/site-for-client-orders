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
        Ателье премиального
        <br />
        тюнинга и дооснащения
      </h1>
      <p className="hero__lead">
        Bose, итальянская покраска, аэрография и тонкая
        работа с кузовом — без конвейера, только под ваш
        автомобиль.
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
