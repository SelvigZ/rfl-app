$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "Starting RFL App..." -ForegroundColor Cyan
Write-Host "Desktop: http://127.0.0.1:5000/" -ForegroundColor Gray
Write-Host "Phone on same Wi-Fi: http://<this-computer-ip>:5000/" -ForegroundColor Gray
Write-Host ""

Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:5000/"
python app.py
