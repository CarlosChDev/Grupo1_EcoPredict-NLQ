import "./TelegramBubble.css";

const TELEGRAM_URL = "https://t.me/ecopredict_lima_bot";

/**
 * Burbuja flotante fija (bottom-right) con un robot que respira/se asoma,
 * enlaza al bot de Telegram. Vive en AppLayout, así que aparece en todos
 * los microfrontends que comparten el shell.
 */
export function TelegramBubble() {
  return (
    <a
      href={TELEGRAM_URL}
      target="_blank"
      rel="noopener noreferrer"
      className="telegram-bubble"
      aria-label="Suscríbete a EcoBot en Telegram"
      title="Suscríbete a EcoBot en Telegram"
    >
      <span className="telegram-bubble-avatar">
        <span className="telegram-bubble-ping" aria-hidden="true" />

        <svg
          className="telegram-bubble-head"
          viewBox="0 0 48 46"
          width="30"
          height="30"
          aria-hidden="true"
        >
          <rect x="9" y="17" width="30" height="26" rx="11" fill="currentColor" />
          <rect x="21" y="9" width="6" height="8" rx="3" fill="currentColor" />
          <circle className="telegram-bubble-led" cx="24" cy="5" r="4" />
          <circle className="telegram-bubble-eye" cx="18" cy="29" r="3.4" />
          <circle
            className="telegram-bubble-eye"
            cx="30"
            cy="29"
            r="3.4"
            style={{ animationDelay: "0.15s" }}
          />
          <path
            d="M17 36c2.6 2.4 11.4 2.4 14 0"
            className="telegram-bubble-mouth"
            strokeWidth="2.6"
            strokeLinecap="round"
            fill="none"
          />
        </svg>

        <span className="telegram-bubble-dot" aria-hidden="true" />
      </span>

      <span className="telegram-bubble-label">Suscríbete a EcoBot</span>
    </a>
  );
}
