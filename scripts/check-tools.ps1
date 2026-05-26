# Verify Node, npm, and Go are installed and on PATH.
$ok = $true

function Test-Tool($name, $cmd) {
    try {
        $out = & $cmd 2>&1 | Select-Object -First 1
        Write-Host "[OK] $name : $out" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] $name : not found" -ForegroundColor Red
        $script:ok = $false
    }
}

Write-Host "=== Tool checks ===" -ForegroundColor Cyan
Test-Tool "Node" { node -v }
Test-Tool "npm" { npm -v }
Test-Tool "Go" { go version }

Write-Host ""
if ($ok) { Write-Host "All tools OK." -ForegroundColor Green; exit 0 }
Write-Host "Install missing tools, open a NEW terminal, run this script again." -ForegroundColor Yellow
exit 1
