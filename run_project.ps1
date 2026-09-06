$ErrorActionPreference = 'Stop'

Write-Host "ProjectAim - judge/local launcher" -ForegroundColor Cyan

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    py -3 -m venv venv
}

$python = Join-Path $PWD "venv\Scripts\python.exe"

Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt

# Playwright is optional. If it is present, install its Chromium browser for
# JavaScript-rendered public pages. A failure here does not stop the app;
# the crawler has a requests fallback.
& $python -c "import importlib.util; print('PLAYWRIGHT_PRESENT' if importlib.util.find_spec('playwright') else 'PLAYWRIGHT_ABSENT')" | ForEach-Object {
    if ($_ -eq 'PLAYWRIGHT_PRESENT') {
        Write-Host "Installing Playwright Chromium (optional crawler enhancement)..." -ForegroundColor Yellow
        try { & $python -m playwright install chromium } catch { Write-Host "Playwright browser install skipped; requests crawler fallback will be used." -ForegroundColor DarkYellow }
    }
}

Write-Host "Starting Streamlit..." -ForegroundColor Green
& $python -m streamlit run app.py
