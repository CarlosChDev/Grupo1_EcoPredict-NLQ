import json, os, re, subprocess, sys, time, urllib.request, urllib.error

KEY = os.environ["GEMINI_KEY"]
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"

PREGUNTAS = [
    "¿Es peligroso este nivel de PM2.5?",
    "¿Cuál es el límite diario de partículas finas?",
    "¿Cuántas veces al año se puede pasar el límite de PM10?",
    "¿Cuánto es lo máximo de ozono permitido?",
    "monóxido de carbono en 8 horas",
    "¿Quién declara una alerta por contaminación del aire?",
    "¿Qué es un ECA?",
    "nivel máximo de dióxido de nitrógeno por hora",
]

def embed(texto):
    body = json.dumps({"model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": texto}]},
        "taskType": "RETRIEVAL_QUERY", "outputDimensionality": 768}).encode()
    for intento in range(6):
        req = urllib.request.Request(URL, data=body, headers={
            "Content-Type": "application/json", "x-goog-api-key": KEY})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                vals = json.load(r)["embedding"]["values"]
                assert len(vals) == 768
                return vals
        except urllib.error.HTTPError as e:
            print(f"  (HTTP {e.code}, reintento {intento+1})", file=sys.stderr)
            time.sleep(2)
    raise RuntimeError("Gemini falló tras 6 intentos")

def psql(sql):
    out = subprocess.run(
        ["docker", "exec", "-i", "aire_postgres", "psql", "-U", "n8n_user",
         "-d", "calidad_aire", "-At", "-F", "|"],
        input=sql, text=True, capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr)
    return [l.split("|") for l in out.stdout.strip().splitlines() if l]

def vectorial(vec):
    v = "[" + ",".join(str(float(x)) for x in vec) + "]"
    return psql(f"""
SELECT id, COALESCE(parametro,'general'), left(referencia,30),
       round((1 - (embedding <=> '{v}'::vector))::numeric, 3)
FROM documentos_rag WHERE tipo='norma' AND embedding IS NOT NULL
ORDER BY embedding <=> '{v}'::vector LIMIT 3;""")

def palabras_clave(pregunta):
    toks = re.findall(r"[a-záéíóúñ0-9]+", pregunta.lower())
    toks = [t for t in toks if len(t) > 2]
    if not toks:
        return []
    q = " | ".join(toks)
    return psql(f"""
SELECT id, COALESCE(parametro,'general'), left(referencia,30),
       round(ts_rank(to_tsvector('spanish', contenido), to_tsquery('spanish', '{q}'))::numeric, 3)
FROM documentos_rag
WHERE tipo='norma' AND to_tsvector('spanish', contenido) @@ to_tsquery('spanish', '{q}')
ORDER BY 4 DESC LIMIT 3;""")

for p in PREGUNTAS:
    print(f"\n=== {p}")
    print("  pgvector (similitud):")
    for f in vectorial(embed(p)):
        print(f"    id {f[0]:>4} | {f[1]:<8} | {f[2]:<30} | {f[3]}")
    print("  palabras clave (ts_rank):")
    kw = palabras_clave(p)
    if not kw:
        print("    (sin resultados)")
    for f in kw:
        print(f"    id {f[0]:>4} | {f[1]:<8} | {f[2]:<30} | {f[3]}")
    time.sleep(0.7)
