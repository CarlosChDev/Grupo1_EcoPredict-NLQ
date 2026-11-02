// BFF serverless (Vercel) delante de n8n: Flujo C (estaciones) y Flujo D (analítica).
// Archivo: src/frontend-shell/api/flujo-c/[ruta].js

const RUTAS = {
  'estaciones': 'estaciones',
  'serie-horaria': 'estaciones/serie-horaria',
  'alertas': 'alertas',
  'analitica/comparativo': 'analitica/comparativo',
  'analitica/ranking-eca': 'analitica/ranking-eca',
  'analitica/patron-horario': 'analitica/patron-horario',
  'analitica/resumen-ia': 'analitica/resumen-ia',
  'analitica/distritos': 'analitica/distritos',
};

export default async function handler(req, res) {
  // Manejo de ruta compatible con [ruta].js estándar o catch-all si Vercel lo pasa como string/arreglo
  const { ruta: rutaQuery, ...queryParams } = req.query;
  const ruta = Array.isArray(rutaQuery) 
    ? rutaQuery.join('/') 
    : (typeof rutaQuery === 'string' ? rutaQuery : '');

  // 1. Solo se permiten peticiones GET
  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ error: 'Método no permitido' });
  }

  // 2. Validación de lista blanca (Object.hasOwn previene manipulación de prototipos)
  if (!Object.hasOwn(RUTAS, ruta)) {
    return res.status(403).json({
      error: 'Acceso denegado',
      message: 'Ruta no autorizada en la lista blanca del BFF.',
    });
  }

  const n8nBaseUrl = process.env.N8N_BASE_URL;
  const n8nApiKey = process.env.N8N_API_KEY;
  if (!n8nBaseUrl || !n8nApiKey) {
    return res.status(500).json({ error: 'Error de configuración del servidor.' });
  }

  try {
    // Reconstruir los query parameters (ej. ?distritos=...&dias=7) para pasarlos a n8n
    const searchParams = new URLSearchParams(queryParams);
    const queryString = searchParams.toString();
    const targetUrl = `${n8nBaseUrl.replace(/\/$/, '')}/${RUTAS[ruta]}${queryString ? `?${queryString}` : ''}`;

    // 3. Petición segura hacia n8n con la key a nivel de servidor
    const response = await fetch(targetUrl, {
      method: 'GET',
      headers: { 'X-API-Key': n8nApiKey },
      signal: AbortSignal.timeout(25000),
    });

    const texto = await response.text();
    let data;
    try {
      data = JSON.parse(texto);
    } catch {
      return res.status(502).json({ error: 'Respuesta inválida del motor de n8n' });
    }

    // 4. Caché de bordes solo si la respuesta fue exitosa
    if (response.ok) {
      res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600, stale-if-error=86400');
    } else {
      res.setHeader('Cache-Control', 'no-store');
    }
    return res.status(response.status).json(data);
  } catch {
    res.setHeader('Cache-Control', 'no-store');
    return res.status(503).json({ error: 'Servicio no disponible temporalmente' });
  }
}