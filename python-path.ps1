$currentDir = Get-Location

if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$env:PYTHONPATH;$currentDir"
} else {
    $env:PYTHONPATH = "$currentDir"
}

Write-Host "PYTHONPATH is now: $env:PYTHONPATH"
