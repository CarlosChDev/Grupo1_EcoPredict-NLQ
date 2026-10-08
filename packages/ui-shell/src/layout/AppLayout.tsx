import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { TelegramBubble } from "../widgets/TelegramBubble";
import "./AppLayout.css";

export interface AppLayoutProps {
  /** Título/subtítulo que muestra el Topbar de esta app. */
  titulo: string;
  subtitulo: string;
  /** id del microfrontend activo (ver registry.ts) para resaltarlo en el Sidebar. */
  activeId: string;
  children: ReactNode;
}

/**
 * Layout compartido (Sidebar + Topbar) que cada microfrontend renderiza
 * alrededor de su propia página. A diferencia del Shell monolítico
 * original, ya no hay un <Outlet/> de React Router: cada app es su propio
 * despliegue y solo tiene una pantalla, así que título/subtítulo/activeId
 * se pasan directo como props en vez de vía contexto de ruta.
 */
export function AppLayout({ titulo, subtitulo, activeId, children }: AppLayoutProps) {
  return (
    <div className="app-layout">
      <div className="aurora" aria-hidden="true" />

      <Sidebar activeId={activeId} />

      <main className="main-content">
        <Topbar titulo={titulo} subtitulo={subtitulo} />

        <section className="content-container">{children}</section>
      </main>

      <TelegramBubble />
    </div>
  );
}
