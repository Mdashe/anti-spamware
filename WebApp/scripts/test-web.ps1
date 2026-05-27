# Build the SvelteKit app (proves package.json and deps are valid).
$ErrorActionPreference = "Stop"
$web = Join-Path (Split-Path $PSScriptRoot -Parent) "apps\web"

if (-not (Test-Path (Join-Path $web "package.json"))) {
    Write-Host "[FAIL] Missing apps\web\package.json — run scripts\init-web.ps1 first." -ForegroundColor Red
    exit 1
}

Set-Location $web
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
}

Write-Host "Running npm run build..." -ForegroundColor Cyan
npm run build
Write-Host "[OK] Web build succeeded." -ForegroundColor Green
