import json, os, subprocess, sys, time, urllib.request, urllib.error

KEY = os.environ["GEMINI_KEY"]
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"

PREGUNTAS = [
    "¿Cómo está el aire en Vitarte?",
    "calidad del aire en Chosica",
    "¿Cómo está el aire cerca de la embajada?",
    "aire en SJL",
    "¿Cómo está el aire en Huachipa?",
    "aire en Miraflores",
    "¿Es peligroso este nivel de PM2.5?",
]

def embed(texto):
    body = json.dumps({
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": texto}]},
        "taskType": "RETRIEVAL_QUERY",
        "outputDimensionality": 768,
    }).encode()
    for intento in range(6):
        req = urllib.request.Request(URL, data=body, headers={
            "Content-Type": "application/json", "x-goog-api-key": KEY})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                vals = json.load(r)["embedding"]["values"]
                assert len(vals) == 768, f"dimensión {len(vals)}"
                return vals
        except urllib.error.HTTPError as e:
            print(f"  (HTTP {e.code}, reintento {intento + 1})", file=sys.stderr)
            time.sleep(2)
    raise RuntimeError("Gemini falló tras 6 intentos")

for p in PREGUNTAS:
    vec = "[" + ",".join(str(float(v)) for v in embed(p)) + "]"
    sql = f"""
SELECT id, tipo, estacion_id AS est,
       round((1 - (embedding <=> '{vec}'::vector))::numeric, 3) AS similitud,
       left(contenido, 70) AS contenido
FROM documentos_rag
WHERE tipo IN ('estacion','zona') AND embedding IS NOT NULL
ORDER BY embedding <=> '{vec}'::vector
LIMIT 3;
"""
    print(f"\n=== {p}")
    out = subprocess.run(
        ["docker", "exec", "-i", "aire_postgres", "psql", "-U", "n8n_user", "-d", "calidad_aire"],
        input=sql, text=True, capture_output=True)
    print(out.stdout or out.stderr)
    time.sleep(0.7)
