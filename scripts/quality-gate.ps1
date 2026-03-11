$ErrorActionPreference = "Stop"

Write-Host "Running backend tests..."
pytest backend/tests -q

Write-Host "Running frontend lint..."
Push-Location "frontend/grabon-underwriting"
try {
    npm run lint
    Write-Host "Running frontend production build..."
    npm run build
}
finally {
    Pop-Location
}
