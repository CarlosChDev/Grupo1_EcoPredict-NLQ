#!/usr/bin/env bash
# ==============================================================================
# Script de Ejecución Automatizada de Newman para CI/CD (HU-03 / T14)
# ==============================================================================
set -euo pipefail

COLLECTION_PATH="src/ia-ops/tests/postman/EcoPredict_Sprint1_Collection.json"
ENVIRONMENT_LOCAL="src/ia-ops/tests/postman/eco_predict_local.postman_environment.json"
ENVIRONMENT_ORACLE="src/ia-ops/tests/postman/eco_predict_oracle_cloud.postman_environment.json"

echo "========================================================"
echo " 🧪 Ejecutando Newman QA Automated Tests (Sprint 1)"
echo "========================================================"

# Verificar existencia de archivos
test -f "$COLLECTION_PATH" || (echo "Error: Colección no encontrada." && exit 1)
test -f "$ENVIRONMENT_LOCAL" || (echo "Error: Entorno local no encontrado." && exit 1)

# Ejecutar pruebas contra entorno Local
echo ">> Ejecutando pruebas contra Entorno Local (Docker)..."
newman run "$COLLECTION_PATH" \
  -e "$ENVIRONMENT_LOCAL" \
  --reporters cli \
  --color on

echo "========================================================"
echo " ✅ Ejecución de Newman finalizada exitosamente."
echo "========================================================"
