"""Utilidades compartidas por probar_vitarte.py y comparar_base.py.

Requiere la variable de entorno GEMINI_KEY (no se escribe en ningún archivo).
Los vectores de las preguntas se guardan en cache_embeddings.json para no
repetir llamadas a la API (el caché no contiene la clave).
"""
import json
import math
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.request

URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
       "gemini-embedding-001:embedContent")
AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(AQUI, "cache_embeddings.json")

try:
    with open(CACHE_PATH, encoding="utf-8") as f:
        _cache = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    _cache = {}


def _key():
    k = os.environ.get("GEMINI_KEY")
    if not k:
        sys.exit("Falta la variable GEMINI_KEY (export GEMINI_KEY='...').")
    return k


def embed(texto, tarea):
    """tarea: 'RETRIEVAL_QUERY' (preguntas) o 'RETRIEVAL_DOCUMENT' (textos)."""
    clave = f"{tarea}|{texto}"
    if clave in _cache:
        return _cache[clave]
    cuerpo = json.dumps({
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": texto}]},
        "taskType": tarea,
        "outputDimensionality": 768,
    }).encode()
    for intento in range(6):
        req = urllib.request.Request(URL, data=cuerpo, headers={
            "Content-Type": "application/json", "x-goog-api-key": _key()})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                vals = json.load(r)["embedding"]["values"]
            assert len(vals) == 768, f"dimensión {len(vals)}"
            _cache[clave] = vals
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(_cache, f)
            time.sleep(0.4)
            return vals
        except urllib.error.HTTPError as e:
            print(f"  (HTTP {e.code}, reintento {intento + 1})", file=sys.stderr)
            time.sleep(2)
    raise RuntimeError("Gemini falló tras 6 intentos")


def norm(s):
    """Minúsculas, sin tildes, sin signos; guiones y puntuación pasan a espacio."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def coseno(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


def _psql(sql):
    out = subprocess.run(
        ["docker", "exec", "-i", "aire_postgres", "psql", "-U", "n8n_user",
         "-d", "calidad_aire", "-At"],
        input=sql, text=True, capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr)
    return out.stdout.strip()


_SQL_ZONAS = """
SELECT COALESCE(json_agg(json_build_object(
  'id', id, 'ref', referencia, 'dist', metadata->>'distrito',
  'contenido', contenido, 'emb', embedding::text) ORDER BY id), '[]'::json)
FROM documentos_rag WHERE tipo = 'zona' AND embedding IS NOT NULL;
"""


def cargar_zonas():
    """Devuelve las filas tipo 'zona' con su vector y el nombre de distrito derivado.

    El distrito se toma de metadata->>'distrito' si existe; si no, de referencia
    (sin lo que vaya entre paréntesis). Se imprime la tabla para revisarla.
    """
    filas = json.loads(_psql(_SQL_ZONAS))
    zonas = []
    for f in filas:
        crudo = re.sub(r"\(.*?\)", "", f["dist"] or f["ref"] or "")
        crudo = crudo.split("=", 1)[-1]
        zonas.append({
            "id": f["id"], "ref": f["ref"], "nombre": norm(crudo),
            "contenido": f["contenido"], "emb": json.loads(f["emb"]),
        })
    return zonas


def mostrar_zonas(zonas):
    print(f"Zonas cargadas: {len(zonas)}")
    for z in zonas:
        print(f"  id {z['id']:>4} | distrito derivado: {z['nombre']:<28} | "
              f"ref: {z['ref']} | {z['contenido'][:50]!r}")
    print()


def ranking(emb_pregunta, zonas):
    """Lista de (similitud, zona) de mayor a menor."""
    pares = [(coseno(emb_pregunta, z["emb"]), z) for z in zonas]
    return sorted(pares, key=lambda p: p[0], reverse=True)
