$projectRoot = Join-Path $PSScriptRoot ".."
Push-Location $projectRoot
try
{
./venv/Scripts/Activate.ps1
$env:PYTHONPATH = (Get-Location)
mkdocs serve --watch-theme
}
finally
{
Pop-Location
}
