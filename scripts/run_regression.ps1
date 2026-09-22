# Member Center Test Framework - TBlocks workflow regression entry
# Usage:
#   .\scripts\run_regression.ps1                  # full regression (all workflow domains)
#   .\scripts\run_regression.ps1 -Suite quick     # smoke + api + performance + load + security
#   .\scripts\run_regression.ps1 -Suite load      # single domain: workflows/load
#   .\scripts\run_regression.ps1 -Suite security  # security baseline only
# Reports (auto):
#   output/reports/report_<suite>_<timestamp>.html  (self-contained, open in browser)
#   output/reports/junit_<suite>_<timestamp>.xml    (CI consumable)
#   output/allure/report/                           (if allure CLI installed)
# Exit code: 0 = all passed; non-zero = failure (CI gate ready)
param(
    [ValidateSet("all", "quick", "smoke", "api", "portal", "functional", "member",
                 "finance", "invest", "ui", "backend", "business", "demo",
                 "performance", "load", "security")]
    [string]$Suite = "all"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "venv python not found: $python"
    exit 2
}

# Browser workflows require headless mode for CI/non-interactive runs.
$env:TBLOCKS_HEADLESS = "1"

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $root "output"
$reportDir = Join-Path $logDir "reports"
foreach ($dir in @($logDir, $reportDir)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}
$log = Join-Path $logDir ("regression_{0}_{1}.log" -f $Suite, $stamp)
$html = Join-Path $reportDir ("report_{0}_{1}.html" -f $Suite, $stamp)
$junit = Join-Path $reportDir ("junit_{0}_{1}.xml" -f $Suite, $stamp)

# --html self-contained: single-file report with CSS embedded, safe to mail/upload.
# --junitxml: standard result XML for CI platforms (GitHub Actions/Jenkins).
$reportArgs = @(
    "--html=$html", "--self-contained-html",
    "--junitxml=$junit"
)

switch ($Suite) {
    "all" {
        $paths = "tblocks/workflows"
        & $python -m pytest --tblocks-workflows $paths @reportArgs -q 2>&1 | Tee-Object -FilePath $log
    }
    "quick" {
        & $python -m pytest -m "smoke or api or performance or load or security" @reportArgs -q 2>&1 |
            Tee-Object -FilePath $log
    }
    Default {
        $paths = "tblocks/workflows/$Suite"
        & $python -m pytest --tblocks-workflows $paths @reportArgs -q 2>&1 | Tee-Object -FilePath $log
    }
}
$exitCode = $LASTEXITCODE

# Allure HTML report: results are written every run (pytest.ini --alluredir);
# render them into a browsable site only when the allure CLI is available.
$allure = Get-Command allure -ErrorAction SilentlyContinue
if ($allure) {
    $allureReport = Join-Path $logDir "allure\report"
    $allureResults = Join-Path $logDir "allure\results"
    & allure generate $allureResults -o $allureReport --clean | Out-Null
    Write-Host "Allure report: $allureReport\index.html"
} else {
    Write-Host "allure CLI not found, skip Allure HTML (HTML/JUnit reports still generated)."
}

Write-Host ""
Write-Host "===== Test reports ====="
Write-Host "HTML : $html"
Write-Host "JUnit: $junit"
Write-Host "Log  : $log"

exit $exitCode
