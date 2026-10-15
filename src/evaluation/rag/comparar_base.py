"""Compara cinco métodos sobre un CSV de preguntas de lugares.

Uso: python3 comparar_base.py [archivo.csv]   (por defecto preguntas_eval.csv)

  1. lista_fija      : el nombre del distrito aparece literal en la pregunta
  2. lista_estaciones: lo anterior + nombres de estación del catálogo
  3. lista_alias     : lo anterior + tabla ALIAS (nombres populares)
  4. rag_top1        : zona más parecida, sin piso
  5. rag_piso        : top-1 solo si la similitud >= PISO

Solo se usan filas tipo 'zona' (13 candidatos). Las tres listas toman SOLO
datos del catálogo o nombres populares; nunca palabras de las preguntas.
"""
import csv
import os
import sys

from rag_util import AQUI, cargar_zonas, embed, mostrar_zonas, norm, ranking

PISO = 0.64
CSV_IN = os.path.join(AQUI, sys.argv[1] if len(sys.argv) > 1 else "preguntas_eval.csv")
CSV_OUT = CSV_IN.replace(".csv", "_resultados.csv")

# Estaciones del catálogo con nombre propio distintivo (ver textos de las zonas).
# Excluidas a propósito: PERU, LIMA, LOS ANDES (genéricas), US DIPLOMATIC POST.
ESTACIONES = {
    "Ate": ["Ceres", "Pariachi"],
    "Lurigancho-Chosica": ["Cajamarquilla", "Huachipa"],
    "Jesús María": ["Campo de Marte"],
    "Pachacámac": ["Quebrada Verde"],
}
# Nombres populares de uso común. Revísala en equipo antes de citar resultados.
ALIAS = {
    "sjl": "San Juan de Lurigancho",
    "smp": "San Martín de Porres",
    "vmt": "Villa María del Triunfo",
    "vitarte": "Ate",
    "chosica": "Lurigancho-Chosica",
}

zonas = cargar_zonas()
mostrar_zonas(zonas)
nombres = {z["nombre"] for z in zonas}

with open(CSV_IN, encoding="utf-8", newline="") as f:
    filas = list(csv.DictReader(f))
faltan = {norm(r["esperado"]) for r in filas} - {"ninguna"} - nombres
if faltan:
    print(f"AVISO: etiquetas que no coinciden con ninguna zona: {sorted(faltan)}\n")


def tabla(origen):
    t = {}
    for frase, distrito in origen.items():
        d = norm(distrito)
        if d in nombres:
            t[norm(frase)] = d
        else:
            print(f"AVISO: {frase!r} apunta a {distrito!r}, que no es una zona; se ignora.")
    return t


T_FIJA = {n: n for n in nombres}
T_EST = dict(T_FIJA)
T_EST.update(tabla({e: d for d, es in ESTACIONES.items() for e in es}))
T_ALIAS = dict(T_EST)
T_ALIAS.update(tabla(ALIAS))


def buscar(pregunta, t):
    nq = f" {norm(pregunta)} "
    hallados = [frase for frase in t if f" {frase} " in nq]
    return t[max(hallados, key=len)] if hallados else "ninguna"


METODOS = ["lista_fija", "lista_estaciones", "lista_alias", "rag_top1", "rag_piso"]
resultados = []
print(f"Vectorizando {len(filas)} preguntas (usa caché si ya existe)...")
for r in filas:
    q = r["pregunta"]
    sim1, z1 = ranking(embed(q, "RETRIEVAL_QUERY"), zonas)[0]
    pred = {
        "lista_fija": buscar(q, T_FIJA),
        "lista_estaciones": buscar(q, T_EST),
        "lista_alias": buscar(q, T_ALIAS),
        "rag_top1": z1["nombre"],
        "rag_piso": z1["nombre"] if sim1 >= PISO else "ninguna",
    }
    resultados.append({"id": r["id"], "esperado": norm(r["esperado"]),
                       "pregunta": q, "sim1": sim1, "pred": pred})

pos = [x for x in resultados if x["esperado"] != "ninguna"]
neg = [x for x in resultados if x["esperado"] == "ninguna"]
print(f"\nArchivo: {os.path.basename(CSV_IN)}")
print(f"Preguntas: {len(resultados)} ({len(pos)} con zona, {len(neg)} 'ninguna')\n")

print(f"{'método':<17} {'zona correcta':>14} {'zona equivocada':>16} {'falsos aceptados':>17}")
for m in METODOS:
    ok = sum(1 for x in pos if x["pred"][m] == x["esperado"])
    mal = sum(1 for x in pos if x["pred"][m] not in (x["esperado"], "ninguna"))
    falsos = sum(1 for x in neg if x["pred"][m] != "ninguna")
    print(f"{m:<17} {ok:>10}/{len(pos):<3} {mal:>12}/{len(pos):<3} {falsos:>13}/{len(neg):<3}")

print("\n--- Preguntas donde algún método falla ---")
for x in resultados:
    if any(x["pred"][m] != x["esperado"] for m in METODOS):
        print(f"\n#{x['id']} esperado={x['esperado']!r}  sim1={x['sim1']:.3f}")
        print(f"   {x['pregunta'][:90]}")
        for m in METODOS:
            marca = "ok " if x["pred"][m] == x["esperado"] else "MAL"
            print(f"   {marca} {m:<17} -> {x['pred'][m]}")

with open(CSV_OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "esperado", "sim1"] + METODOS + ["pregunta"])
    for x in resultados:
        w.writerow([x["id"], x["esperado"], f"{x['sim1']:.3f}"]
                   + [x["pred"][m] for m in METODOS] + [x["pregunta"]])
print(f"\nDetalle guardado en {CSV_OUT}")
