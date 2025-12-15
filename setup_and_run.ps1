Write-Host "Installing Backend Dependencies (to ensure they are in your environment)..."
pip install -r backend/requirements.txt

Write-Host "Starting Services..."
.\start_windows.ps1
