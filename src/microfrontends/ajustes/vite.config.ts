import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// `base` debe calzar con el prefijo que usa el shell para montar este
// microfrontend (ver /ajustes en frontend-shell/vercel.json y su proxy de
// desarrollo).
export default defineConfig({
  base: "/ajustes/",
  plugins: [react()],
  server: {
    port: 5177,
  },
});
