export default async function handler(req, res) {
  // 1. Lista blanca de rutas permitidas según el Sprint 4 (HT-07)
  const allowedRoutes = ['estaciones', 'serie-horaria', 'alertas'];
  const { ruta } = req.query;

  if (!allowedRoutes.includes(ruta)) {
    return res.status(403).json({ 
      error: 'Acceso denegado', 
      message: 'Ruta no autorizada en la lista blanca del BFF.' 
    });
  }

  // 2. Configuración de cabeceras de caché exigidas por el Sprint 4
  res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600, stale-if-error=86400');

  try {
    const n8nBaseUrl = process.env.N8N_BASE_URL;
    const n8nApiKey = process.env.N8N_API_KEY;

    if (!n8nBaseUrl || !n8nApiKey) {
      return res.status(500).json({ error: 'Error de configuración en las variables de entorno del servidor serverless.' });
    }

    // 3. Petición segura hacia el Flujo C en n8n
    const response = await fetch(`${n8nBaseUrl}/${ruta}`, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': n8nApiKey
      },
      body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
    });

    const data = await response.json();
    return res.status(response.status).json(data);

  } catch (error) {
    return res.status(503).json({ 
      error: 'Servicio no disponible temporalmente', 
      details: 'No se pudo conectar con el motor de n8n, mostrando datos en caché si están disponibles.' 
    });
  }
}