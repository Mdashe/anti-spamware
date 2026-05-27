# Run tool checks, web build, and API health check.
$ErrorActionPreference = "Stop"
$scripts = Split-Path -Parent $MyInvocation.MyCommand.Path

& "$scripts\check-tools.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& "$scripts\test-web.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& "$scripts\test-api.ps1"
Write-Host "`n[OK] All tests passed." -ForegroundColor Green
