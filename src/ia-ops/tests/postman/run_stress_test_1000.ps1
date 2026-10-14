<#
.SYNOPSIS
    Script automatizado de ejecución de Pruebas de Carga y Rate Limiting (1,000 Solicitudes) con Newman CLI.
.DESCRIPTION
    Permite ejecutar la proyección de 1,000 solicitudes solicitada para auditar:
    - Escenario A: Ataque DoS / Misma IP -> Validación de 429 Too Many Requests
    - Escenario B: Concurrencia Multi-IP -> Validación de 200 OK con aislamiento ciudadano
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File src/ia-ops/tests/postman/run_stress_test_1000.ps1 -Iterations 1000 -Scenario A
#>

param(
    [Parameter(Mandatory = $false)]
    [int]$Iterations = 1000,

    [Parameter(Mandatory = $false)]
    [ValidateSet("A", "B", "ALL")]
    [string]$Scenario = "A",

    [Parameter(Mandatory = $false)]
    [ValidateSet("oracle", "local")]
    [string]$Env = "oracle",

    [Parameter(Mandatory = $false)]
    [int]$DelayMs = 0,

    [Parameter(Mandatory = $false)]
    [switch]$HtmlReport
)

$CollectionPath = "$PSScriptRoot\EcoPredict_StressTest_1000_Requests_Collection.json"
if ($Env -eq "oracle") {
    $EnvPath = "$PSScriptRoot\eco_predict_oracle_cloud.postman_environment.json"
    $EnvName = "Oracle Cloud Infrastructure (Remoto)"
} else {
    $EnvPath = "$PSScriptRoot\eco_predict_local.postman_environment.json"
    $EnvName = "Entorno Local (Docker)"
}

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "   ECOPREDICT & NLQ — PROYECCIÓN DE $Iterations SOLICITUDES (RATE LIMITING & STRESS)" -ForegroundColor Yellow
Write-Host "   Entorno: $EnvName" -ForegroundColor Green
Write-Host "   Escenario Seleccionado: $Scenario" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan

# Determinar carpeta de Newman
$FolderArg = @()
if ($Scenario -eq "A") {
    $FolderArg = @("--folder", "1. Escenario A - Misma IP (Auditoría de Rate Limiting y Protección DoS)")
} elseif ($Scenario -eq "B") {
    $FolderArg = @("--folder", "2. Escenario B - Múltiples IPs (Concurrencia Ciudadana Distribuida)")
}

# Verificar instalación de Newman
$newmanCmd = Get-Command newman.cmd -ErrorAction SilentlyContinue
if (-not $newmanCmd) {
    $newmanCmd = Get-Command newman -ErrorAction SilentlyContinue
}
if (-not $newmanCmd) {
    Write-Host "[ERROR] Newman no está instalado globalmente." -ForegroundColor Red
    Write-Host "Por favor instala Newman ejecutando: npm install -g newman" -ForegroundColor Yellow
    exit 1
}

# Preparar comando
$ReportArgs = @("-r", "cli")
$ReportFile = "$PSScriptRoot\reporte_estres_$($Iterations)_solicitudes.html"

if ($HtmlReport) {
    $htmlextraInstalled = npm.cmd list -g newman-reporter-htmlextra 2>$null
    if ($LASTEXITCODE -eq 0 -or $htmlextraInstalled -match "newman-reporter-htmlextra") {
        $ReportArgs = @("-r", "cli,htmlextra", "--reporter-htmlextra-export", $ReportFile)
        Write-Host "Generando reporte interactivo en: $ReportFile" -ForegroundColor Magenta
    } else {
        Write-Host "[AVISO] newman-reporter-htmlextra no detectado. Ejecutando con reporte cli estándar." -ForegroundColor Yellow
    }
}

Write-Host "`nLanzando ejecución de $Iterations peticiones... (Delay: ${DelayMs}ms)" -ForegroundColor White

$DelayArg = @()
if ($DelayMs -gt 0) {
    $DelayArg = @("--delay-request", $DelayMs)
}

$cmdArgs = @(
    "run", $CollectionPath,
    "-e", $EnvPath,
    "-n", $Iterations
) + $DelayArg + $FolderArg + $ReportArgs

& newman.cmd @cmdArgs

$ExitCode = $LASTEXITCODE

Write-Host "`n================================================================================" -ForegroundColor Cyan
if ($ExitCode -eq 0) {
    Write-Host "✅ Proyección de $Iterations solicitudes completada exitosamente." -ForegroundColor Green
    if ($HtmlReport -and (Test-Path $ReportFile)) {
        Write-Host "📊 Reporte HTML generado: $ReportFile" -ForegroundColor Cyan
    }
} else {
    Write-Host "ℹ️ Ejecución finalizada con código: $ExitCode (Verificar desglose de códigos 200 vs 429)." -ForegroundColor Yellow
}
Write-Host "================================================================================" -ForegroundColor Cyan
