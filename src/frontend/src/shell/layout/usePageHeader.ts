import { useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import type { AppLayoutContext, PageHeader } from "./AppLayout";

/**
 * Cada página del Shell (Inicio, microfrontends) llama este hook una vez
 * para anunciar el título/subtítulo que debe mostrar el Topbar compartido.
 */
export function usePageHeader(header: PageHeader) {
  const { setHeader } = useOutletContext<AppLayoutContext>();

  useEffect(() => {
    setHeader(header);
  }, [header.titulo, header.subtitulo]);
}
