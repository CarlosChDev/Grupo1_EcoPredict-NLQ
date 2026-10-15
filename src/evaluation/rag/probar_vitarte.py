"""¿Por qué 'Vitarte' no recupera Ate?

Parte 1: cómo se ordenan las 13 zonas ante varias formas de preguntar por Vitarte.
Parte 2: qué pasa si el texto de la zona Ate se redacta distinto (se vectorizan
         variantes SOLO en memoria; no se toca la base).

Ojo: añadir "Vitarte" al texto de la zona equivale a una tabla de alias.
Si la parte 2 lo arregla, el arreglo es un alias, no mérito de la similitud.
"""
from rag_util import cargar_zonas, coseno, embed, mostrar_zonas, norm, ranking

CONSULTAS = [
    "Vitarte",
    "¿Cómo está el aire en Vitarte?",
    "aire en Vitarte, Ate",
    "calidad del aire Vitarte Lima",
]

zonas = cargar_zonas()
mostrar_zonas(zonas)

ate = [z for z in zonas if z["nombre"] == "ate"]
if not ate:
    raise SystemExit("No encontré una zona cuyo distrito derivado sea 'ate'. "
                     "Revisa la tabla de arriba.")
ate = ate[0]

print("=== PARTE 1: ranking de zonas por consulta (sim. coseno) ===")
for q in CONSULTAS:
    r = ranking(embed(q, "RETRIEVAL_QUERY"), zonas)
    pos = next(i for i, (_, z) in enumerate(r, 1) if z["id"] == ate["id"])
    print(f"\n{q!r}  -> Ate queda en el puesto {pos} de {len(r)}")
    for s, z in r[:5]:
        marca = "  <-- Ate" if z["id"] == ate["id"] else ""
        print(f"   {s:.3f}  {z['nombre']}{marca}")

print("\n=== PARTE 2: variantes del texto de Ate (solo en memoria) ===")
base = ate["contenido"]
variantes = {
    "original (recalculado)": base,
    "original + mención de Vitarte": base + " Incluye la zona de Vitarte.",
    "solo 'Ate'": "Ate",
    "'Ate, Vitarte'": "Ate, Vitarte",
}
emb_var = {k: embed(v, "RETRIEVAL_DOCUMENT") for k, v in variantes.items()}

print(f"\nControl: coseno entre el vector guardado y el recalculado del texto "
      f"original = {coseno(ate['emb'], emb_var['original (recalculado)']):.4f} "
      f"(debería ser ~1.0)")

otras = [z for z in zonas if z["id"] != ate["id"]]
for q in CONSULTAS[:2]:
    eq = embed(q, "RETRIEVAL_QUERY")
    mejor_otra = max(((coseno(eq, z["emb"]), z["nombre"]) for z in otras))
    print(f"\nConsulta {q!r}; mejor zona rival: {mejor_otra[1]} ({mejor_otra[0]:.3f})")
    for nombre, v in emb_var.items():
        s = coseno(eq, v)
        gana = "GANA" if s > mejor_otra[0] else "pierde"
        print(f"   {s:.3f}  {gana:<6} Ate con texto «{nombre}»")

print("\nLectura: si solo gana la variante que menciona Vitarte, el problema es "
      "que el texto no contiene el nombre popular, y eso se resuelve con un alias.")
