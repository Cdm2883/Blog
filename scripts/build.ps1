Import-Module (Join-Path $PSScriptRoot "env.psm1")

Invoke-MkDocs {
    mkdocs build
}
