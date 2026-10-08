import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// `base` debe calzar con el prefijo que usa el shell para montar este
// microfrontend (ver /nlq-chat en frontend-shell/vercel.json y su proxy de
// desarrollo) — así los assets se referencian como /nlq-chat/assets/...
// tanto en dev como en el build de producción.
export default defineConfig({
  base: "/nlq-chat/",
  plugins: [react()],
  server: {
    port: 5174,
  },
});
