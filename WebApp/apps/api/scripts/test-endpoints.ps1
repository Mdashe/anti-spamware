# Test REST endpoints against a running API + PostgreSQL.
# Usage: start the API first (go run ./cmd/server), then run this script.
$ErrorActionPreference = "Stop"
$BaseUrl = if ($env:API_BASE_URL) { $env:API_BASE_URL } else { "http://localhost:8080" }

function Invoke-Api {
    param(
        [string]$Method,
        [string]$Path,
        [object]$Body
    )
    $uri = "$BaseUrl$Path"
    $params = @{
        Uri             = $uri
        Method          = $Method
        UseBasicParsing = $true
    }
    if ($Body) {
        $params.ContentType = "application/json"
        $params.Body = ($Body | ConvertTo-Json -Compress)
    }
    return Invoke-WebRequest @params
}

Write-Host "Testing API at $BaseUrl" -ForegroundColor Cyan

# Health
$r = Invoke-Api -Method GET -Path "/health"
Write-Host "[OK] GET /health -> $($r.Content)" -ForegroundColor Green

$r = Invoke-Api -Method GET -Path "/health/db"
Write-Host "[OK] GET /health/db -> $($r.Content)" -ForegroundColor Green

# User
$email = "script-test-$(Get-Date -Format 'yyyyMMddHHmmss')@example.com"
$r = Invoke-Api -Method POST -Path "/api/v1/users" -Body @{
    email = $email
    name  = "Script Test User"
}
$user = $r.Content | ConvertFrom-Json
Write-Host "[OK] POST /api/v1/users -> id=$($user.id)" -ForegroundColor Green
$userId = $user.id

# Email account (direct SQL — fn_email_account_insert not ready yet)
$pgBin = $env:PG_BIN
if (-not $pgBin) { $pgBin = "psql" }
$dbUrl = if ($env:DATABASE_URL) { $env:DATABASE_URL } else { "postgres://postgres:admin@localhost:5433/postgres?sslmode=disable" }

$sql = "INSERT INTO email_accounts (user_id, provider, provider_email) VALUES ($userId, 'gmail', '$email') RETURNING id;"
$accountResult = & $pgBin $dbUrl -t -A -c $sql 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Could not seed email_account via psql. Skipping email/classification tests." -ForegroundColor Yellow
    Write-Host "       Install psql or set PG_BIN. Error: $accountResult" -ForegroundColor Yellow

    $r = Invoke-Api -Method POST -Path "/api/v1/rules" -Body @{
        user_id          = $userId
        name             = "Test Rule"
        condition_type   = "subject_contains"
        condition_value  = "lottery"
        action           = "mark_spam"
        enabled          = $true
    }
    $rule = $r.Content | ConvertFrom-Json
    Write-Host "[OK] POST /api/v1/rules -> id=$($rule.id)" -ForegroundColor Green
    Write-Host "Done (partial — email tests skipped)." -ForegroundColor Cyan
    exit 0
}

$accountId = [int]$accountResult.Trim()
Write-Host "[OK] Seeded email_account id=$accountId" -ForegroundColor Green

# Email
$r = Invoke-Api -Method POST -Path "/api/v1/emails" -Body @{
    user_id           = $userId
    account_id        = $accountId
    provider_email_id = "test-msg-001"
    thread_id         = "thread-001"
    subject           = "Test Subject"
    sender            = "sender@example.com"
    recipients        = @($email)
    snippet           = "Test snippet"
    received_at       = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    cached_body       = "Full email body for testing"
}
$mail = $r.Content | ConvertFrom-Json
Write-Host "[OK] POST /api/v1/emails -> id=$($mail.id)" -ForegroundColor Green

# Classification
$r = Invoke-Api -Method POST -Path "/api/v1/classifications" -Body @{
    email_id       = $mail.id
    label          = "spam"
    confidence     = 0.95
    model_version  = "v1.0"
    source         = "model"
}
$class = $r.Content | ConvertFrom-Json
Write-Host "[OK] POST /api/v1/classifications -> id=$($class.id)" -ForegroundColor Green

# Rule
$r = Invoke-Api -Method POST -Path "/api/v1/rules" -Body @{
    user_id          = $userId
    name             = "Test Rule"
    condition_type   = "subject_contains"
    condition_value  = "lottery"
    action           = "mark_spam"
    enabled          = $true
}
$rule = $r.Content | ConvertFrom-Json
Write-Host "[OK] POST /api/v1/rules -> id=$($rule.id)" -ForegroundColor Green

Write-Host "All endpoint tests passed." -ForegroundColor Green
