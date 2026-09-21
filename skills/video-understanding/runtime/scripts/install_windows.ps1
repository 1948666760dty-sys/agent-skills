param()

$ErrorActionPreference = "Stop"
$RuntimeRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RuntimeRoot

Write-Host "[video-understanding] Runtime root: $RuntimeRoot"

$PythonCommand = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    try {
        & py -3.12 -c "import sys; print(sys.version)" | Out-Null
        if ($LASTEXITCODE -eq 0) { $PythonCommand = @("py", "-3.12") }
    } catch {}
}
if (-not $PythonCommand -and (Get-Command python -ErrorAction SilentlyContinue)) {
    & python -c "import sys; assert (3,11) <= sys.version_info[:2] < (3,14)" 2>$null
    if ($LASTEXITCODE -eq 0) { $PythonCommand = @("python") }
}

if (-not $PythonCommand) {
    throw "Python 3.11-3.13 was not found. Install Python 3.12 x64, then run this script again."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[video-understanding] Creating .venv ..."
    if ($PythonCommand.Count -eq 2) {
        & $PythonCommand[0] $PythonCommand[1] -m venv .venv
    } else {
        & $PythonCommand[0] -m venv .venv
    }
}

$VenvPython = Join-Path $RuntimeRoot ".venv\Scripts\python.exe"

Write-Host "[video-understanding] Updating pip ..."
& $VenvPython -m pip install --upgrade pip

Write-Host "[video-understanding] Installing Runtime dependencies ..."
& $VenvPython -m pip install -e .

Write-Host "[video-understanding] Running preflight ..."
& $VenvPython scripts\preflight.py

Write-Host ""
Write-Host "Install complete."
Write-Host "Next: run scripts\run_windows.ps1"
