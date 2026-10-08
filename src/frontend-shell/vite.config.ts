import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En Vercel, la composición de microfrontends la hacen los `rewrites` de
// vercel.json (cada uno es un despliegue aparte). En `npm run dev` no hay
// rewrites, así que este proxy replica exactamente el mismo mapeo para que
// http://localhost:5173/nlq-chat, /dashboard-ambiental, etc. funcionen
// igual — siempre que el microfrontend correspondiente también esté
// corriendo en su puerto fijo (ver `npm run dev:all` en la raíz del repo).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/nlq-chat": "http://localhost:5174",
      "/dashboard-ambiental": "http://localhost:5175",
      "/estado-sistema": "http://localhost:5176",
      "/ajustes": "http://localhost:5177",
      "/data-analytics": "http://localhost:5178",
    },
  },
});
