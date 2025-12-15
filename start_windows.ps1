$env:DATABASE_URL="sqlite:///chain.db"

Write-Host "Starting Backend..."
Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory "backend"

Write-Host "Starting Frontend..."
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "frontend"

Write-Host "Services launch initiated. Please check opened windows."
