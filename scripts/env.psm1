function Invoke-MkDocs {
    param(
        [scriptblock]$ScriptBlock
    )

    $projectRoot = Join-Path $PSScriptRoot ".."
    Push-Location $projectRoot
    try {
        ./venv/Scripts/Activate.ps1
        $env:PYTHONPATH = (Get-Location).Path
        & $ScriptBlock
    }
    finally
    {
        Pop-Location
    }
}
