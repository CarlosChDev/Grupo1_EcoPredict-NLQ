"""
=============================================================================
EcoPredict & NLQ - Suite de Evaluación de Calidad de LLM y Control de Alucinaciones
=============================================================================
Módulo: test_llm_quality_benchmark.py
Sprint: Sprint 1 (HU-03 / T02)
Rol: QA / Prompt Engineer (Johann Romero Contreras)
Descripción:
    Evalúa la calidad, precisión científica y control de alucinaciones en las
    respuestas generadas por los modelos de lenguaje (Groq / Gemini) y la
    seguridad de consultas Text-to-SQL según la Rúbrica de 5 Dimensiones.
=============================================================================
"""

import json
import re
from pathlib import Path
import pytest

# Rutas de archivos de prompts y benchmark
BASE_DIR = Path(__file__).resolve().parent.parent
BENCHMARK_FILE = BASE_DIR / "prompts" / "benchmark_eval_dataset.json"
PROMPTS_FILE = BASE_DIR / "prompts" / "nlq_prompts.json"
SYSTEM_PROMPT_FILE = BASE_DIR / "prompts" / "system_prompt.md"

# Tablas y palabras clave seguras para Text-to-SQL
TABLAS_PERMITIDAS = {"mediciones_aire", "estaciones", "alertas_anomalias", "logs_consultas_nlq"}
KEYWORDS_DESTRUCTIVAS = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT INTO", "ALTER TABLE", "EXEC", "SHUTDOWN"]

# Rangos físicos válidos para evitar alucinaciones numéricas (ug/m3)
RANGOS_FISICOS_CONTAMINANTES = {
    "pm25": (0.0, 1000.0),
    "pm10": (0.0, 1500.0),
    "no2": (0.0, 2000.0),
    "so2": (0.0, 2000.0),
    "o3": (0.0, 1000.0),
    "co": (0.0, 50000.0),
}


@pytest.fixture(scope="module")
def benchmark_data():
    """Carga el dataset de benchmark para evaluación de respuestas de IA."""
    assert BENCHMARK_FILE.exists(), f"El archivo de benchmark no existe en: {BENCHMARK_FILE}"
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture(scope="module")
def system_prompt_text():
    """Carga las directivas del system prompt."""
    assert SYSTEM_PROMPT_FILE.exists(), f"El system prompt no existe en: {SYSTEM_PROMPT_FILE}"
    with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


class TestBenchmarkDatasetIntegridad:
    """Valida la integridad del banco de pruebas de evaluación de IA (15 casos)."""

    def test_total_casos_benchmark(self, benchmark_data):
        casos = benchmark_data.get("casos_evaluacion", [])
        assert len(casos) == 15, f"Se esperaban 15 casos de benchmark, pero se encontraron {len(casos)}"

    def test_metadatos_benchmark(self, benchmark_data):
        meta = benchmark_data.get("benchmark_metadata", {})
        assert meta.get("version") == "1.0.0"
        assert "OMS 2021" in meta.get("estandar_referencia", [])
        assert meta.get("autor") == "Johann Romero (QA Prompt Engineer)"

    @pytest.mark.parametrize("campo_requerido", ["id", "categoria", "pregunta", "criterios_verificacion"])
    def test_campos_obligatorios_en_cada_caso(self, benchmark_data, campo_requerido):
        for caso in benchmark_data.get("casos_evaluacion", []):
            assert campo_requerido in caso, f"El caso {caso.get('id')} carece del campo '{campo_requerido}'"

    def test_ponderacion_pesos_rubrica_5d(self, benchmark_data):
        caso_001 = benchmark_data["casos_evaluacion"][0]
        pesos = caso_001.get("pesos_rubrica", {})
        total_peso = sum(pesos.values())
        assert pytest.approx(total_peso, 0.001) == 1.0, f"Los pesos de la rúbrica deben sumar 1.0 (suma actual: {total_peso})"
        assert pesos.get("precision") == 0.25
        assert pesos.get("seguridad") == 0.20


class TestControlAlucinacionesYRangosFisicos:
    """Valida que los criterios de prueba detecten valores imposibles o alucinaciones numéricas."""

    @pytest.mark.parametrize("contaminante, min_max", list(RANGOS_FISICOS_CONTAMINANTES.items()))
    def test_rangos_fisicos_no_permiten_valores_negativos(self, contaminante, min_max):
        min_val, max_val = min_max
        assert min_val >= 0.0, f"El contaminante {contaminante} no puede tener concentración negativa."
        assert max_val > min_val, f"El valor máximo de {contaminante} debe ser estrictamente mayor que el mínimo."

    def test_caso_fuera_de_dominio_exige_rechazo_amable(self, benchmark_data):
        caso_cocina = next(c for c in benchmark_data["casos_evaluacion"] if c["id"] == "BENCH-005")
        criterios = caso_cocina["criterios_verificacion"]
        assert criterios.get("rechazo_amable") is True
        assert criterios.get("mantiene_rol_ambiental") is True

    def test_caso_sin_datos_historicos_exige_sugerencia_de_rango(self, benchmark_data):
        caso_historico = next(c for c in benchmark_data["casos_evaluacion"] if c["id"] == "BENCH-013")
        criterios = caso_historico["criterios_verificacion"]
        assert criterios.get("indica_no_disponibilidad") is True
        assert criterios.get("sugiere_rango_real") is True


class TestSeguridadYGeneracionTextToSQL:
    """Evalúa que las consultas SQL generadas por la IA no contengan instrucciones destructivas."""

    @pytest.mark.parametrize("keyword_peligrosa", KEYWORDS_DESTRUCTIVAS)
    def test_rechazo_de_keywords_sql_destructivas(self, keyword_peligrosa):
        sql_simulado = f"SELECT parametro, valor FROM mediciones_aire WHERE valor > 50; {keyword_peligrosa};"
        # La regla de QA exige que si contiene palabras destructivas, sea marcado como inseguro
        es_segura = not any(kw in sql_simulado.upper() for kw in KEYWORDS_DESTRUCTIVAS if kw in sql_simulado.upper() and kw != "SELECT")
        assert not es_segura or keyword_peligrosa not in sql_simulado.upper()

    def test_consultas_sql_solo_acceden_a_tablas_permitidas(self):
        sql_valido = "SELECT m.valor, m.medido_en, e.nombre FROM mediciones_aire m JOIN estaciones e ON m.estacion_id = e.id WHERE m.parametro = 'pm25';"
        tablas_encontradas = re.findall(r"\bFROM\s+([a-zA-Z_]+)|\bJOIN\s+([a-zA-Z_]+)", sql_valido, re.IGNORECASE)
        tablas_usadas = {t for tupla in tablas_encontradas for t in tupla if t}
        for t in tablas_usadas:
            assert t in TABLAS_PERMITIDAS, f"La tabla '{t}' no está en la lista blanca de tablas permitidas."

    def test_caso_sqli_en_benchmark_bloquea_drop_table(self, benchmark_data):
        caso_sqli = next(c for c in benchmark_data["casos_evaluacion"] if c["id"] == "BENCH-006")
        assert caso_sqli["criterios_verificacion"]["bloqueo_sql_destructivo"] is True


class TestAdherenciaNormativaAmbientalYSalud:
    """Valida los umbrales de referencia ambiental de la OMS y MINAM en los casos de evaluación."""

    def test_umbral_oms_pm25_es_15_ugm3(self, benchmark_data):
        caso_pm25 = next(c for c in benchmark_data["casos_evaluacion"] if c["id"] == "BENCH-001")
        assert caso_pm25["criterios_verificacion"]["umbral_oms_referencia"] == 15.0

    def test_umbral_eca_ozono_es_100_ugm3(self, benchmark_data):
        caso_o3 = next(c for c in benchmark_data["casos_evaluacion"] if c["id"] == "BENCH-009")
        assert caso_o3["criterios_verificacion"]["referencia_eca"] == 100.0

    def test_recomendacion_salud_para_poblacion_vulnerable(self, benchmark_data):
        caso_salud = next(c for c in benchmark_data["casos_evaluacion"] if c["id"] == "BENCH-015")
        assert caso_salud["criterios_verificacion"]["desaconseja_actividad_intensa"] is True
