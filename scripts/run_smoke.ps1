# Member Center Test Framework - Smoke suite (front 8081 + back 8082, HTTP-only, seconds)
# Usage:
#   .\scripts\run_smoke.ps1          # both sites
#   .\scripts\run_smoke.ps1 front    # front site only
#   .\scripts\run_smoke.ps1 back     # back site only
# Exit code: 0 = all passed; non-zero = failure (CI gate ready)
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

switch ($Target) {
    "front" { $paths = "tblocks/workflows/smoke/smoke_front_site.json" }
    "back"  { $paths = "tblocks/workflows/smoke/smoke_back_site.json" }
    Default { $paths = "tblocks/workflows/smoke" }
}

& $python -m pytest --tblocks-workflows $paths -q
exit $LASTEXITCODE
