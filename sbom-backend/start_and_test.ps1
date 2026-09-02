param($Port=8000)
$logfile = Join-Path $PSScriptRoot "server.log"
# Start the server in background, redirect output
$env:ASPNETCORE_URLS="http://0.0.0.0:$Port"
$proc = & python -m uvicorn app.main:app --host 0.0.0.0 --port $Port 2>&1 | Out-File -FilePath $logfile -Append
Start-Sleep -Seconds 3
try {
    $result = Invoke-RestMethod -Uri "http://localhost:$Port/api/health" -Method Get
    Write-Host "SUCCESS: Health check passed"
    Write-Host "Result: $result"
} catch {
    Write-Host "ERROR: $_"
    Write-Host "Last 50 lines of log:"
    Get-Content -Path $logfile -Tail 50
}