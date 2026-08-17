import { CSSProperties, FormEvent, useEffect, useState } from "react";
import "./App.css";

const WEBHOOK_URL = import.meta.env.VITE_N8N_WEBHOOK_URL;

const PARAMETROS = ["pm25", "pm10", "no2", "so2", "o3", "co"] as const;

const EJEMPLOS = [
  "¿Cuál fue el nivel de PM2.5 en Lima la semana pasada?",
  "Compara el NO2 entre Lima y Callao este mes",
  "¿Cuándo se superó el límite de PM10 en Ate?",
];

type Estado = "idle" | "cargando" | "ok" | "error";

const ESTADO_INFO: Record<
  Estado,
  { label: string; color: string; pct: string; icon: string }
> = {
  idle: { label: "En espera", color: "var(--text-muted)", pct: "18%", icon: "🌙" },
  cargando: { label: "Enviando…", color: "var(--primary-cyan)", pct: "70%", icon: "🔄" },
  ok: { label: "Recibido", color: "var(--status-good)", pct: "100%", icon: "✅" },
  error: { label: "Error", color: "var(--status-bad)", pct: "100%", icon: "⚠️" },
};

function App() {
  const [pregunta, setPregunta] = useState("");
  const [ciudad, setCiudad] = useState("Lima");
  const [parametro, setParametro] = useState<(typeof PARAMETROS)[number]>("pm25");
  const [estado, setEstado] = useState<Estado>("idle");
  const [respuesta, setRespuesta] = useState<unknown>(null);
  const [mensajeError, setMensajeError] = useState("");
  const [ahora, setAhora] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setAhora(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  async function enviarConsulta(e: FormEvent) {
    e.preventDefault();
    setEstado("cargando");
    setMensajeError("");
    setRespuesta(null);

    try {
      const res = await fetch(WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pregunta, ciudad, parametro }),
      });

      const json = await res.json();
      setRespuesta(json);
      setEstado(res.ok ? "ok" : "error");
    } catch (err) {
      setEstado("error");
      setMensajeError(
        err instanceof Error ? err.message : "No se pudo contactar al webhook de n8n.",
      );
    }
  }

  const info = ESTADO_INFO[estado];
  const ringStyle: CSSProperties = {
    background: `conic-gradient(${info.color} ${info.pct}, #1c3045 0)`,
  };

  return (
    <div className="app-layout">
      {/* ================= SIDEBAR ================= */}
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon">🌿</div>
          <div className="logo-text">
            <strong>EcoPredict</strong>
            <span>NLQ</span>
          </div>
        </div>

        <div className="section-title">NAVEGACIÓN</div>

        <div className="nav-item active">
          <span className="icon">💬</span>
          <span>Consulta NLQ</span>
        </div>

        <div className="nav-item disabled">
          <span className="icon">📊</span>
          <span>Historial</span>
          <span className="soon-badge">Pronto</span>
        </div>

        <div className="nav-item disabled">
          <span className="icon">📈</span>
          <span>Analytics</span>
          <span className="soon-badge">Pronto</span>
        </div>

        <div className="stream">
          <div className="stream-title">
            <span className="live-pulse"></span>
            n8n WEBHOOK
          </div>
          <p>{WEBHOOK_URL || "Sin definir — revisa .env"}</p>
          <div className="stream-badges">
            <span className="badge badge-teal">n8n</span>
            <span className="badge badge-teal">Postgres</span>
          </div>
        </div>

        <div className="version">HU-04 · Flujo base NLQ</div>
      </aside>

      {/* ================= MAIN ================= */}
      <main className="main-content">
        <header className="topbar">
          <div className="title">
            <h1>Consulta en Lenguaje Natural</h1>
            <p>Pregunta en español y n8n consulta la base de datos ambiental</p>
          </div>

          <div className="top-actions">
            <div className="time">
              <strong>
                {ahora.toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit" })}
              </strong>
              <span>
                {ahora.toLocaleDateString("es-PE", {
                  weekday: "long",
                  day: "numeric",
                  month: "long",
                })}
              </span>
            </div>

            <button type="button" className="top-btn" disabled>
              🔌 {WEBHOOK_URL ? "Webhook configurado" : "Webhook no configurado"}
            </button>

            <div className="avatar">EP</div>
          </div>
        </header>

        <section className="content-container">
          {/* ================= TOP ================= */}
          <div className="top-grid">
            {/* STATUS */}
            <div className="card card-gradient status-card">
              <div className="card-label">
                <span className="small-icon">📡</span>
                ESTADO DE LA CONSULTA
              </div>

              <div className={estado === "cargando" ? "status-ring spinning" : "status-ring"} style={ringStyle}>
                <div className="status-ring-inner">
                  <span className="status-icon">{info.icon}</span>
                </div>
              </div>

              <div className="aqi-status" style={{ color: info.color, borderColor: info.color }}>
                {info.label}
              </div>

              <div className="station">
                <p>Consulta actual</p>
                <strong>
                  {ciudad} <span>· {parametro.toUpperCase()}</span>
                </strong>
              </div>

              <div className="aqi-scale">
                <span className="good">Recibido</span>
                <span className="moderate">Enviando</span>
                <span className="bad">Error</span>
              </div>
            </div>

            {/* QUERY FORM */}
            <div className="card query-card">
              <div className="card-label">
                <span className="small-icon">💬</span>
                NUEVA CONSULTA NLQ
              </div>

              <form onSubmit={enviarConsulta} className="nlq-form">
                <textarea
                  value={pregunta}
                  onChange={(e) => setPregunta(e.target.value)}
                  placeholder="¿Cuál fue el nivel de PM2.5 en Lima la semana pasada?"
                  rows={3}
                  required
                />

                <div className="chips">
                  {EJEMPLOS.map((ejemplo) => (
                    <button
                      key={ejemplo}
                      type="button"
                      className="chip"
                      onClick={() => setPregunta(ejemplo)}
                    >
                      {ejemplo}
                    </button>
                  ))}
                </div>

                <div className="form-row">
                  <label>
                    Ciudad
                    <input value={ciudad} onChange={(e) => setCiudad(e.target.value)} />
                  </label>

                  <label>
                    Parámetro
                    <select
                      value={parametro}
                      onChange={(e) => setParametro(e.target.value as (typeof PARAMETROS)[number])}
                    >
                      {PARAMETROS.map((p) => (
                        <option key={p} value={p}>
                          {p.toUpperCase()}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <button type="submit" className="btn-primary submit-btn" disabled={estado === "cargando"}>
                  {estado === "cargando" ? "Enviando..." : "Enviar al webhook"}
                </button>
              </form>
            </div>
          </div>

          {/* ================= BOTTOM ================= */}
          <div className="bottom-grid">
            {/* FLOW */}
            <div className="card flow-card">
              <div className="section-heading">
                <span className="heading-icon">🗺️</span>
                <strong>Flujo de datos</strong>
              </div>

              <div className="flow-grid">
                <div className="flow-item">
                  <div className="flow-icon">📝</div>
                  <div className="flow-value">Pregunta</div>
                  <div className="flow-label">Lenguaje natural</div>
                </div>

                <div className="flow-item">
                  <div className="flow-icon">🔗</div>
                  <div className="flow-value">n8n</div>
                  <div className="flow-label">Webhook local</div>
                </div>

                <div className="flow-item">
                  <div className="flow-icon">🗄️</div>
                  <div className="flow-value">Postgres</div>
                  <div className="flow-label">Valida y consulta</div>
                </div>

                <div className="flow-item">
                  <div className="flow-icon">📬</div>
                  <div className="flow-value">Respuesta</div>
                  <div className="flow-label">JSON crudo</div>
                </div>
              </div>
            </div>

            {/* RESPONSE */}
            <div className="card response-card">
              <div className="alerts-header">
                <div className="section-heading">
                  <span className="heading-icon">📥</span>
                  <strong>Respuesta del Webhook</strong>
                </div>

                <span className="live-label" style={{ color: info.color }}>
                  {info.label.toUpperCase()}
                </span>
              </div>

              {estado === "idle" && (
                <div className="alert-msg neutral">Aún no se ha enviado ninguna consulta.</div>
              )}

              {estado === "cargando" && (
                <div className="alert-msg warning">Esperando respuesta de n8n...</div>
              )}

              {estado === "error" && mensajeError && (
                <div className="alert-msg danger">Error de red: {mensajeError}</div>
              )}

              {respuesta !== null ? (
                <pre className={estado === "error" ? "response-json danger" : "response-json ok"}>
                  {JSON.stringify(respuesta, null, 2)}
                </pre>
              ) : null}

              <div className="webhook-info">
                Webhook: <code>{WEBHOOK_URL || "(sin definir — revisa .env)"}</code>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
