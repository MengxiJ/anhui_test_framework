# Member Center Test Framework - Smoke suite (front 8081 + back 8082, HTTP-only, seconds)
# Usage:
#   .\scripts\run_smoke.ps1          # both sites
#   .\scripts\run_smoke.ps1 front    # front site only
#   .\scripts\run_smoke.ps1 back     # back site only
# Reports (auto):
#   output/reports/report_smoke-<target>_<timestamp>.html
#   output/reports/junit_smoke-<target>_<timestamp>.xml
# Exit code: 0 = all passed; old log-only behavior replaced by HTML+XML reports.
param(
    [ValidateSet("all", "front", "back")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "venv python not found: $python"
    exit 2
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportDir = Join-Path $root "output\reports"
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}
$tag = "smoke-$Target"
$html = Join-Path $reportDir ("report_{0}_{1}.html" -f $tag, $stamp)
$junit = Join-Path $reportDir ("junit_{0}_{1}.xml" -f $tag, $stamp)

switch ($Target) {
    "front" { $paths = "tblocks/workflows/smoke/smoke_front_site.json" }
    "back"  { $paths = "tblocks/workflows/smoke/smoke_back_site.json" }
    Default { $paths = "tblocks/workflows/smoke" }
}

& $python -m pytest --tblocks-workflows $paths `
    "--html=$html" --self-contained-html `
    "--junitxml=$junit" -q
$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "===== Test reports ====="
Write-Host "HTML : $html"
Write-Host "JUnit: $junit"

exit $exitCode
