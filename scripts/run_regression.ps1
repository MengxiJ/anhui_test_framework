# Member Center Test Framework - TBlocks workflow regression entry
# Usage:
#   .\scripts\run_regression.ps1                  # full regression (all workflow domains)
#   .\scripts\run_regression.ps1 -Suite quick     # smoke + api + performance + load + security
#   .\scripts\run_regression.ps1 -Suite load      # single domain: workflows/load
#   .\scripts\run_regression.ps1 -Suite security  # security baseline only
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

$logDir = Join-Path $root "output"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$log = Join-Path $logDir ("regression_{0}_{1}.log" -f $Suite, $stamp)

switch ($Suite) {
    "all" {
        $paths = "tblocks/workflows"
        & $python -m pytest --tblocks-workflows $paths -q 2>&1 | Tee-Object -FilePath $log
    }
    "quick" {
        & $python -m pytest -m "smoke or api or performance or load or security" -q 2>&1 |
            Tee-Object -FilePath $log
    }
    Default {
        $paths = "tblocks/workflows/$Suite"
        & $python -m pytest --tblocks-workflows $paths -q 2>&1 | Tee-Object -FilePath $log
    }
}

exit $LASTEXITCODE
