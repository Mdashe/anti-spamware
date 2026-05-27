# Scaffold SvelteKit into apps/web (safe if package.json already exists).
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$apps = Join-Path $root "apps"
$web = Join-Path $apps "web"
$scaffold = Join-Path $apps "web-scaffold"

Set-Location $apps

if (Test-Path (Join-Path $web "package.json")) {
    Write-Host "[SKIP] apps/web/package.json already exists." -ForegroundColor Yellow
    exit 0
}

Write-Host "Creating web-scaffold..." -ForegroundColor Cyan
npx sv@latest create web-scaffold --template minimal --no-types --no-install --no-download-check --add sveltekit-adapter=adapter:auto

if (-not (Test-Path (Join-Path $scaffold "package.json"))) {
    Write-Host "[FAIL] web-scaffold was not created. Use --no-types (not --types js)." -ForegroundColor Red
    exit 1
}

Remove-Item (Join-Path $web "package-lock.json") -ErrorAction SilentlyContinue
Copy-Item "$scaffold\package.json", "$scaffold\svelte.config.js", "$scaffold\vite.config.js", "$scaffold\jsconfig.json", "$scaffold\.gitignore", "$scaffold\.npmrc" -Destination $web -Force
Copy-Item "$scaffold\src\app.html" -Destination "$web\src\" -Force
New-Item -ItemType Directory -Force -Path "$web\src\lib\assets" | Out-Null
Copy-Item "$scaffold\src\lib\assets\favicon.svg" -Destination "$web\src\lib\assets\" -Force
Copy-Item "$scaffold\static\robots.txt" -Destination "$web\static\" -Force
Copy-Item "$scaffold\src\routes\+layout.svelte", "$scaffold\src\routes\+page.svelte" -Destination "$web\src\routes\" -Force
(Get-Content "$web\package.json") -replace '"name": "web-scaffold"', '"name": "web"' | Set-Content "$web\package.json"

Remove-Item -Recurse -Force $scaffold
Set-Location $web
npm install
Write-Host "[OK] Web app initialized. Run: npm run dev" -ForegroundColor Green
