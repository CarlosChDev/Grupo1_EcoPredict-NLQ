"""Normativa: cinco métodos sobre preguntas_normativa.csv.

  filtro_param   : detecta el parámetro por nombre o alias y devuelve su fila
  palabras_clave : coincidencia de raíces con peso IDF, con el código del
                   parámetro añadido cuando se detecta un alias
  rag_top1       : fila más parecida por similitud coseno, sin piso
  rag_piso       : lo anterior solo si la similitud >= PISO
  hibrido        : filtro_param si detecta parámetro; si no, rag_piso

'esperado' es el id de la fila, o 'ninguna' si la base NO tiene la respuesta
(benceno, H2S y plomo existen en el Anexo, pero no están cargados).
Un empate en palabras clave cuenta como fallo.

ALIAS: solo nombres de uso común. Revísala en equipo antes de citar resultados.
"""
import csv
import json
import math
import os
import sys
from collections import Counter

from rag_util import AQUI, _psql, coseno, embed, norm

PISO = 0.65  # provisional; mira el barrido del final
CSV_IN = os.path.join(AQUI, sys.argv[1] if len(sys.argv) > 1 else "preguntas_normativa.csv")
CSV_OUT = CSV_IN.replace(".csv", "_resultados.csv")

ALIAS = {
    "PM2.5": ["pm2 5", "pm25", "pm 2 5", "particulas finas",
              "material particulado fino"],
    "PM10": ["pm10", "pm 10"],
    "NO2": ["no2", "dioxido de nitrogeno"],
    "SO2": ["so2", "dioxido de azufre"],
    "CO": ["co", "monoxido de carbono"],
    "O3": ["o3", "ozono"],
}
STOP = set("""el la los las un una unos unas de del al y o u a en por para con sin
que se es son su sus lo le les cual cuales cuanto cuantos cuanta cuantas como
quien quienes donde cuando me mi si no ni mas muy ya hay ser esta estan puede
pueden dice segun""".split())

SQL = """SELECT COALESCE(json_agg(json_build_object('id', id, 'parametro', parametro,
'contenido', contenido, 'emb', embedding::text) ORDER BY id), '[]'::json)
FROM documentos_rag WHERE tipo = 'norma' AND embedding IS NOT NULL;"""

docs = json.loads(_psql(SQL))
for d in docs:
    d["id"] = str(d["id"])
    d["emb"] = json.loads(d["emb"])
print(f"Filas de normativa cargadas: {len(docs)} (ids {[d['id'] for d in docs]})")

param_a_id = {d["parametro"]: d["id"] for d in docs if d["parametro"]}
for p in ALIAS:
    if p not in param_a_id:
        print(f"AVISO: no hay fila con parametro={p!r}; ese alias no resolverá nada.")


def stems(texto):
    return {t[:5] for t in norm(texto).split() if t not in STOP}


for d in docs:
    d["stems"] = stems(d["contenido"])
df = Counter(s for d in docs for s in d["stems"])
idf = {s: math.log(len(docs) / n) for s, n in df.items()}


def detectar(q):
    nq = f" {norm(q)} "
    return [p for p, al in ALIAS.items() if any(f" {norm(a)} " in nq for a in al)]


def m_filtro(q):
    ps = [p for p in detectar(q) if p in param_a_id]
    return param_a_id[ps[0]] if ps else "ninguna"


def m_claves(q):
    qs = stems(q)
    for p in detectar(q):
        qs |= stems(p)
    pts = sorted(((sum(idf.get(s, 0) for s in qs & d["stems"]), d["id"])
                  for d in docs), reverse=True)
    if pts[0][0] <= 0:
        return "ninguna"
    if len(pts) > 1 and abs(pts[0][0] - pts[1][0]) < 1e-9:
        return "empate"
    return pts[0][1]


with open(CSV_IN, encoding="utf-8", newline="") as f:
    filas = list(csv.DictReader(f))

res = []
print(f"Vectorizando {len(filas)} preguntas (usa caché si ya existe)...")
for r in filas:
    q = r["pregunta"]
    eq = embed(q, "RETRIEVAL_QUERY")
    sims = sorted(((coseno(eq, d["emb"]), d["id"]) for d in docs), reverse=True)
    sim1, id1 = sims[0]
    piso = id1 if sim1 >= PISO else "ninguna"
    a = m_filtro(q)
    res.append({"id": r["id"], "tipo": r["tipo"], "esperado": r["esperado"].strip(),
                "pregunta": q, "sim1": sim1, "id1": id1,
                "pred": {"filtro_param": a, "palabras_clave": m_claves(q),
                         "rag_top1": id1, "rag_piso": piso,
                         "hibrido": a if a != "ninguna" else piso}})

TIPOS = ["nombrado", "indirecto", "general", "sin_respuesta"]
METODOS = ["filtro_param", "palabras_clave", "rag_top1", "rag_piso", "hibrido"]

print(f"\nAciertos por tipo de pregunta (PISO = {PISO}); en sin_respuesta, acertar = 'ninguna'\n")
print(f"{'tipo':<14}{'n':>3}  " + "  ".join(f"{m:<14}" for m in METODOS))
for t in TIPOS + ["TOTAL"]:
    xs = res if t == "TOTAL" else [x for x in res if x["tipo"] == t]
    cols = [f"{sum(1 for x in xs if x['pred'][m] == x['esperado'])}/{len(xs)}"
            for m in METODOS]
    print(f"{t:<14}{len(xs):>3}  " + "  ".join(f"{c:<14}" for c in cols))

print("\n--- Preguntas donde algún método falla ---")
for x in res:
    if any(x["pred"][m] != x["esperado"] for m in METODOS):
        print(f"\n#{x['id']} [{x['tipo']}] esperado={x['esperado']}  "
              f"top1 vectorial={x['id1']} (sim {x['sim1']:.3f})")
        print(f"   {x['pregunta'][:90]}")
        for m in METODOS:
            marca = "ok " if x["pred"][m] == x["esperado"] else "MAL"
            print(f"   {marca} {m:<15} -> {x['pred'][m]}")

print("\n--- Similitud del top-1 en preguntas sin respuesta cargada ---")
for x in res:
    if x["tipo"] == "sin_respuesta":
        print(f"   {x['sim1']:.3f}  (fila {x['id1']})  {x['pregunta'][:70]}")

print("\n--- Barrido de piso (vectorial) ---")
print(f"{'corte':>6} {'errores aceptados':>18} {'aciertos rechazados':>20}")
for c in [0.60 + i * 0.01 for i in range(0, 17)]:
    err = sum(1 for x in res if (x["esperado"] == "ninguna" or x["id1"] != x["esperado"])
              and x["sim1"] >= c)
    rech = sum(1 for x in res if x["esperado"] != "ninguna"
               and x["id1"] == x["esperado"] and x["sim1"] < c)
    print(f"{c:>6.2f} {err:>18} {rech:>20}")

with open(CSV_OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "tipo", "esperado", "sim1", "id1"] + METODOS + ["pregunta"])
    for x in res:
        w.writerow([x["id"], x["tipo"], x["esperado"], f"{x['sim1']:.3f}", x["id1"]]
                   + [x["pred"][m] for m in METODOS] + [x["pregunta"]])
print(f"\nDetalle guardado en {CSV_OUT}")
