import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import "./AppLayout.css";

export interface PageHeader {
  titulo: string;
  subtitulo: string;
}

/**
 * Contexto que cada página (Inicio, NLQ Chat, ...) usa para fijar el
 * título/subtítulo que el Topbar del Shell debe mostrar. Ver
 * `shell/layout/usePageHeader.ts`.
 */
export interface AppLayoutContext {
  setHeader: (header: PageHeader) => void;
}

const HEADER_POR_DEFECTO: PageHeader = {
  titulo: "EcoPredict - NLQ",
  subtitulo: "Sistema de alerta e investigación ambiental ciudadana",
};

export function AppLayout() {
  const [header, setHeader] = useState<PageHeader>(HEADER_POR_DEFECTO);

  return (
    <div className="app-layout">
      <Sidebar />

      <main className="main-content">
        <Topbar titulo={header.titulo} subtitulo={header.subtitulo} />

        <section className="content-container">
          <Outlet context={{ setHeader } satisfies AppLayoutContext} />
        </section>
      </main>
    </div>
  );
}
