param($Port=8000)
$env:ASPNETCORE_URLS="http://0.0.0.0:$Port"
$proc = & python -m uvicorn app.main:app --host 0.0.0.0 --port $Port 2>&1
Start-Sleep -Seconds 3
try {
    $result = Invoke-RestMethod -Uri "http://localhost:$Port/api/health" -Method Get
    Write-Host "Health check result: $result"
} catch {
    Write-Host "Error: $_"
}