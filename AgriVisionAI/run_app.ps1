# Run the Streamlit app from the project root.
Push-Location $PSScriptRoot
if (Test-Path .\.venv\Scripts\Activate.ps1) {
    Write-Host 'Activating local virtual environment...'
    . .\.venv\Scripts\Activate.ps1
} else {
    Write-Host 'No local virtual environment found. Using system Python.'
}
python -m streamlit run frontend/app.py
Pop-Location
