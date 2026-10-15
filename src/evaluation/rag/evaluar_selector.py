#!/usr/bin/env python3
"""HU-02 · Prueba del paso "la similitud propone, el LLM elige".

Para cada pregunta:
  1. vectoriza la pregunta (gemini-embedding-001, RETRIEVAL_QUERY, 768),
  2. toma los 5 documentos de normativa/salud más parecidos (coseno),
  3. le pasa esos 5 al LLM y le pide el id que responde la pregunta, o "ninguna",
  4. valida que el id devuelto esté entre los 5 (si no, cuenta como "ninguna").
Y lo compara con el RAG con piso (top-1 si similitud >= 0.65), que es lo que ya mediste.

Uso (en src/evaluation/rag/):
    read -rs GEMINI_KEY; export GEMINI_KEY; echo
    read -rs GROQ_KEY; export GROQ_KEY; echo      # opcional: juzga Groq, como en el bot
    python3 evaluar_juez.py preguntas_normativa_ia.csv [otro.csv ...]
    unset GEMINI_KEY GROQ_KEY

Variables opcionales: JUEZ=groq|gemini, GROQ_MODEL (llama-3.3-70b-versatile),
GEMINI_MODEL (gemini-2.5-flash), TOP_K=5, PISO=0.65.
Los CSV necesitan columnas id, pregunta, esperado (un id de documentos_rag o "ninguna").
"""
import csv
import json
import math
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

GEMINI_URL = os.environ.get("GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta")
GROQ_URL = os.environ.get("GROQ_URL", "https://api.groq.com/openai/v1")
TOP_K = int(os.environ.get("TOP_K", "5"))
PISO = float(os.environ.get("PISO", "0.65"))
CACHE = "cache_juez_embeddings.json"
DOCS_CMD = os.environ.get(
    "DOCS_CMD",
    "docker exec -i aire_postgres psql -U n8n_user -d calidad_aire -At -z -c "
    "\"SELECT id, tipo, coalesce(parametro,''), "
    "regexp_replace(contenido, '[\\t\\n\\r]+', ' ', 'g'), embedding::text "
    "FROM documentos_rag WHERE tipo IN ('norma','salud') AND embedding IS NOT NULL ORDER BY id\"",
)


def post(url, cuerpo, headers, intentos=4):
    datos = json.dumps(cuerpo).encode()
    for i in range(intentos):
        req = urllib.request.Request(url, data=datos, headers={"Content-Type": "application/json", "User-Agent": "ecopredict-eval/1.0", **headers})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and i < intentos - 1:
                espera = 2 ** i * 2
                print(f"   HTTP {e.code}, reintento {i + 1} en {espera}s", file=sys.stderr)
                time.sleep(espera)
                continue
            detalle = e.read()[:300].decode("utf-8", "replace")
            raise RuntimeError(f"HTTP {e.code}: {detalle}") from None
        except urllib.error.URLError as e:
            if i < intentos - 1:
                time.sleep(2 ** i * 2)
                continue
            raise RuntimeError(f"Sin conexión: {e.reason}") from None


def normalizar(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def coseno(a, b):
    return sum(x * y for x, y in zip(a, b))


def cargar_cache():
    try:
        return json.load(open(CACHE))
    except (OSError, ValueError):
        return {}


def embedding_pregunta(texto, cache, key):
    if texto in cache:
        return cache[texto]
    r = post(
        f"{GEMINI_URL}/models/gemini-embedding-001:embedContent",
        {"model": "models/gemini-embedding-001", "content": {"parts": [{"text": texto}]},
         "taskType": "RETRIEVAL_QUERY", "outputDimensionality": 768},
        {"x-goog-api-key": key},
    )
    v = normalizar(r["embedding"]["values"])
    cache[texto] = v
    json.dump(cache, open(CACHE, "w"))
    return v


def cargar_documentos():
    out = subprocess.run(DOCS_CMD, shell=True, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("No pude leer documentos_rag:\n" + out.stderr)
    docs = []
    for linea in out.stdout.splitlines():
        if not linea.strip():
            continue
        id_, tipo, parametro, contenido, emb = linea.split("\0")
        docs.append({"id": int(id_), "tipo": tipo, "parametro": parametro, "contenido": contenido,
                     "vec": normalizar([float(x) for x in emb.strip("[]").split(",")])})
    if not docs:
        sys.exit("documentos_rag no devolvió filas de norma/salud con embedding.")
    return docs


INSTRUCCION = """Eres el filtro de un bot sobre calidad del aire en Lima.
Te doy una pregunta de un ciudadano y varios fragmentos de normativa numerados por id.
Elige el id del fragmento que RESPONDE la pregunta. Si ninguno la responde de verdad
(solo habla del mismo tema, o le falta el dato que se pide), responde "ninguna".
No uses conocimiento propio: solo lo que dicen los fragmentos.
Responde SOLO con JSON: {"id": <número o "ninguna">, "motivo": "<una frase>"}"""


def armar_prompt(pregunta, candidatos):
    bloques = "\n\n".join(f"[id {c['id']}] {c['contenido']}" for c in candidatos)
    return f"{INSTRUCCION}\n\nPregunta: {pregunta}\n\nFragmentos:\n{bloques}"


def preguntar_juez(prompt, juez):
    if juez == "groq":
        r = post(f"{GROQ_URL}/chat/completions",
                 {"model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"), "temperature": 0,
                  "response_format": {"type": "json_object"},
                  "messages": [{"role": "user", "content": prompt}]},
                 {"Authorization": "Bearer " + os.environ["GROQ_KEY"]})
        texto = r["choices"][0]["message"]["content"]
        uso = r.get("usage", {}).get("total_tokens")
    else:
        modelo = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        r = post(f"{GEMINI_URL}/models/{modelo}:generateContent",
                 {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                  "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}},
                 {"x-goog-api-key": os.environ["GEMINI_KEY"]})
        texto = "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"])
        uso = r.get("usageMetadata", {}).get("totalTokenCount")
    return texto, uso


def interpretar(texto, ids_validos):
    try:
        d = json.loads(texto.strip().strip("`").removeprefix("json").strip())
        valor = d.get("id")
        motivo = str(d.get("motivo", ""))[:120]
    except (ValueError, AttributeError):
        return "ninguna", "respuesta no era JSON"
    if valor is None or str(valor).strip().lower() == "ninguna":
        return "ninguna", motivo
    try:
        valor = int(str(valor).strip())
    except ValueError:
        return "ninguna", f"id ilegible: {valor!r}"
    if valor not in ids_validos:
        return "ninguna", f"id {valor} no estaba entre los candidatos (descartado)"
    return str(valor), motivo


def clasificar(esperado, obtenido):
    if esperado == "ninguna":
        return "ok" if obtenido == "ninguna" else "falso_aceptado"
    if obtenido == esperado:
        return "ok"
    return "rechazado" if obtenido == "ninguna" else "id_equivocado"


def resumen(nombre, filas, col):
    pos = [f for f in filas if f["esperado"] != "ninguna"]
    neg = [f for f in filas if f["esperado"] == "ninguna"]
    c = lambda fs, r: sum(1 for f in fs if clasificar(f["esperado"], f[col]) == r)
    return (f"{nombre:<16} {c(pos, 'ok'):>3}/{len(pos):<3}        {c(pos, 'id_equivocado'):>3}/{len(pos):<3}"
            f"          {c(pos, 'rechazado'):>3}/{len(pos):<3}        {c(neg, 'falso_aceptado'):>3}/{len(neg):<3}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    gkey = os.environ.get("GEMINI_KEY") or sys.exit("Falta GEMINI_KEY (read -rs GEMINI_KEY; export GEMINI_KEY)")
    juez = os.environ.get("JUEZ") or ("groq" if os.environ.get("GROQ_KEY") else "gemini")
    if juez == "groq" and not os.environ.get("GROQ_KEY"):
        sys.exit("JUEZ=groq pero falta GROQ_KEY")

    docs = cargar_documentos()
    print(f"Documentos norma/salud con embedding: {len(docs)} (ids {', '.join(str(d['id']) for d in docs)})")
    print(f"Juez: {juez} · top-{TOP_K} · piso de comparación {PISO}\n")
    cache = cargar_cache()

    for ruta in sys.argv[1:]:
        preguntas = list(csv.DictReader(open(ruta, encoding="utf-8")))
        filas, tokens = [], 0
        for p in preguntas:
            esperado = str(p["esperado"]).strip().lower()
            q = embedding_pregunta(p["pregunta"], cache, gkey)
            ranking = sorted(docs, key=lambda d: coseno(q, d["vec"]), reverse=True)[:TOP_K]
            sims = [round(coseno(q, d["vec"]), 3) for d in ranking]
            piso = str(ranking[0]["id"]) if sims[0] >= PISO else "ninguna"
            texto, uso = preguntar_juez(armar_prompt(p["pregunta"], ranking), juez)
            tokens += uso or 0
            elegido, motivo = interpretar(texto, {d["id"] for d in ranking})
            filas.append({"id": p["id"], "pregunta": p["pregunta"], "esperado": esperado,
                          "candidatos": " ".join(f"{d['id']}:{s}" for d, s in zip(ranking, sims)),
                          "esperado_en_candidatos": "si" if esperado == "ninguna" or
                          esperado in {str(d["id"]) for d in ranking} else "NO",
                          "rag_piso": piso, "juez": elegido, "motivo_juez": motivo})
            time.sleep(0.3)

        pos = sum(1 for f in filas if f["esperado"] != "ninguna")
        print(f"Archivo: {ruta} · {len(filas)} preguntas ({pos} con respuesta, {len(filas) - pos} 'ninguna')")
        print("método           acierta (con resp.)  id equivocado  rechazado (con resp.)  falsos aceptados")
        print(resumen("rag_piso", filas, "rag_piso"))
        print(resumen("rag + juez", filas, "juez"))
        fuera = [f["id"] for f in filas if f["esperado_en_candidatos"] == "NO"]
        if fuera:
            print(f"  ojo: en {fuera} el documento correcto no llegó al top-{TOP_K}; ahí el juez no podía acertar.")
        print(f"  tokens del juez: {tokens}")
        print("\n--- donde rag_piso y juez no coinciden, o alguno falla ---")
        for f in filas:
            a, b = clasificar(f["esperado"], f["rag_piso"]), clasificar(f["esperado"], f["juez"])
            if a != "ok" or b != "ok":
                print(f"#{f['id']} esperado={f['esperado']}  [{f['candidatos']}]\n   {f['pregunta'][:90]}")
                print(f"   {'ok ' if a == 'ok' else 'MAL'} rag_piso   -> {f['rag_piso']}")
                print(f"   {'ok ' if b == 'ok' else 'MAL'} rag+juez   -> {f['juez']}   ({f['motivo_juez']})")
        salida = ruta.rsplit(".", 1)[0] + f"_juez_{juez}.csv"
        with open(salida, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
        print(f"\nDetalle guardado en {salida}\n")


if __name__ == "__main__":
    main()
