# Drusti - Development Startup Script (Windows)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DRUSTI - Starting Development Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Backend
Write-Host "`n[1/2] Starting FastAPI backend..." -ForegroundColor Yellow
$backendScript = @"
cd '$root\backend'
if (-not (Test-Path '.venv')) {
    Write-Host 'Creating Python virtual environment...' -ForegroundColor Yellow
    python -m venv .venv
}
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet
Write-Host 'Starting Drusti backend on http://localhost:8000' -ForegroundColor Green
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"@

$backendTemp = "$env:TEMP\drusti_backend.ps1"
Set-Content -Path $backendTemp -Value $backendScript
Start-Process powershell -ArgumentList "-NoExit", "-File", $backendTemp

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[2/2] Starting Next.js frontend..." -ForegroundColor Yellow
$frontendScript = @"
cd '$root\frontend'
npm install --silent
Write-Host 'Starting Drusti frontend on http://localhost:3000' -ForegroundColor Green
npm run dev
"@

$frontendTemp = "$env:TEMP\drusti_frontend.ps1"
Set-Content -Path $frontendTemp -Value $frontendScript
Start-Process powershell -ArgumentList "-NoExit", "-File", $frontendTemp

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
