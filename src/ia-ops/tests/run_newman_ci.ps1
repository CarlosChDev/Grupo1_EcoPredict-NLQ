# ==============================================================================
# Script de Ejecución Automatizada de Newman para PowerShell (HU-03 / T14)
# ==============================================================================
param (
    [string]$Target = "local"
)

$Collection = "src/ia-ops/tests/postman/EcoPredict_Sprint1_Collection.json"
$EnvFile = if ($Target -eq "oracle") {
    "src/ia-ops/tests/postman/eco_predict_oracle_cloud.postman_environment.json"
} else {
    "src/ia-ops/tests/postman/eco_predict_local.postman_environment.json"
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " 🧪 Ejecutando Newman QA - EcoPredict Sprint 1 ($Target)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

newman run $Collection -e $EnvFile --reporters cli --color on

Write-Host "========================================================" -ForegroundColor Green
Write-Host " ✅ Ejecución finalizada." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
