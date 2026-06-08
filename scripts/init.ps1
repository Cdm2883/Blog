$projectRoot = Join-Path $PSScriptRoot ".."
Push-Location $projectRoot
try {
    if (-not (Test-Path "venv"))
    {
        python -m venv venv
    }
    ./venv/Scripts/Activate.ps1

    Get-ChildItem plugins | ForEach-Object { pip install -e $_.FullName }
    pip install -r requirements.txt
    pip install mkdocs-material[recommended]
}
finally
{
    Pop-Location
}
