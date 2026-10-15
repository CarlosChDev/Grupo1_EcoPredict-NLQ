import csv, json, os, subprocess, sys, time, urllib.request, urllib.error

KEY = os.environ["GEMINI_KEY"]
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
AQUI = os.path.dirname(os.path.abspath(__file__))
ENTRADA = os.path.join(AQUI, "preguntas_eval.csv")
SALIDA = os.path.join(AQUI, "resultados_eval.csv")

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

SQL = """
SELECT d.id, d.tipo, COALESCE(d.metadata->>'zona', e.zona) AS zona,
       round((1 - (d.embedding <=> '{vec}'::vector))::numeric, 4) AS sim
FROM documentos_rag d LEFT JOIN estaciones e ON e.id = d.estacion_id
WHERE d.tipo IN ('estacion','zona') AND d.embedding IS NOT NULL
ORDER BY d.embedding <=> '{vec}'::vector
LIMIT 5;
"""

def buscar(vec):
    v = "[" + ",".join(str(float(x)) for x in vec) + "]"
    out = subprocess.run(
        ["docker", "exec", "-i", "aire_postgres", "psql", "-U", "n8n_user",
         "-d", "calidad_aire", "-At", "-F", "|"],
        input=SQL.format(vec=v), text=True, capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr)
    filas = []
    for linea in out.stdout.strip().splitlines():
        i, tipo, zona, sim = linea.split("|")
        filas.append((int(i), tipo, zona, float(sim)))
    return filas

if not os.path.exists(ENTRADA):
    sys.exit("No existe " + ENTRADA + " (copia ahí preguntas_eval.csv)")

R = []
with open(ENTRADA, encoding="utf-8-sig", newline="") as f:
    for fila in csv.DictReader(f):
        p = (fila.get("pregunta") or "").strip()
        esp = (fila.get("esperado") or "").strip()
        if not p or not esp or p.startswith("EJEMPLO"):
            continue
        top = buscar(embed(p))
        zonas = [t[2] for t in top]
        ninguna = esp.lower() == "ninguna"
        ok = (not ninguna) and zonas[0].lower() == esp.lower()
        en_top5 = (not ninguna) and esp.lower() in [z.lower() for z in zonas]
        R.append({"id": fila.get("id", ""), "pregunta": p, "esperado": esp,
                  "autor": fila.get("autor", ""), "top1_zona": zonas[0],
                  "sim1": top[0][3], "ok": ok, "en_top5": en_top5,
                  "ninguna": ninguna})
        time.sleep(0.5)

if not R:
    sys.exit("No hay preguntas etiquetadas en " + ENTRADA)

with open(SALIDA, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(R[0].keys()))
    w.writeheader(); w.writerows(R)

con_zona = [r for r in R if not r["ninguna"]]
n_nin = len(R) - len(con_zona)
print(f"\nPreguntas: {len(R)} ({len(con_zona)} con zona esperada, {n_nin} 'ninguna')")
if len(R) < 30:
    print("AVISO: menos de 30 preguntas, el corte no es confiable.")
if con_zona:
    a1 = sum(r["ok"] for r in con_zona)
    a5 = sum(r["en_top5"] for r in con_zona)
    print(f"Zona correcta en el 1er resultado: {a1}/{len(con_zona)}")
    print(f"Zona correcta dentro de los 5 primeros: {a5}/{len(con_zona)}")

print("\n corte | aciertos falsos | rechazos innecesarios")
print(" ------+-----------------+----------------------")
mejor = None
t = 0.55
while t <= 0.851:
    fa = sum(1 for r in R if r["sim1"] >= t and not r["ok"])
    ri = sum(1 for r in R if r["sim1"] < t and r["ok"])
    print(f" {t:.2f}  | {fa:>15} | {ri:>20}")
    if mejor is None or (fa, ri) < (mejor[1], mejor[2]):
        mejor = (round(t, 2), fa, ri)
    t += 0.01

print(f"\nCorte con menos aciertos falsos (y luego menos rechazos): {mejor[0]:.2f}")
print(f"  aciertos falsos: {mejor[1]}   rechazos innecesarios: {mejor[2]}")
print("\nSi un corte alto deja casi todos los aciertos reales rechazados,")
print("la similitud sola no sirve y conviene el diseño de candidatos + LLM.")
print("Detalle por pregunta en", SALIDA)
