param()

$ErrorActionPreference = "Stop"
$RuntimeRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RuntimeRoot

$VenvPython = Join-Path $RuntimeRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[video-understanding] .venv not found; running installer first."
    & (Join-Path $PSScriptRoot "install_windows.ps1")
}

Write-Host "[video-understanding] Starting MCP server at http://127.0.0.1:8765/mcp"
Write-Host "[video-understanding] Keep this window open while ChatGPT uses the app."
& $VenvPython -m video_understanding_runtime.server
