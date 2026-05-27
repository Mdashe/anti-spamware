# Compile and run a quick health check against the Go API.
$ErrorActionPreference = "Stop"
$api = Join-Path (Split-Path $PSScriptRoot -Parent) "apps\api"

Set-Location $api
Write-Host "Building API..." -ForegroundColor Cyan
go build -o server.exe ./cmd/server

Write-Host "Starting server on :8080 (5s test)..." -ForegroundColor Cyan
$job = Start-Job { Set-Location $using:api; .\server.exe }
Start-Sleep -Seconds 2

try {
    $r = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing
    Write-Host "Response: $($r.Content)" -ForegroundColor Green
    if ($r.StatusCode -eq 200) { Write-Host "[OK] API health check passed." -ForegroundColor Green }
} catch {
    Write-Host "[FAIL] Could not reach http://localhost:8080/health" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
} finally {
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -Force -ErrorAction SilentlyContinue
    Get-Process -Name "server" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $api "server.exe") -ErrorAction SilentlyContinue
}
