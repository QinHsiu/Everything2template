$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
python -m pip install -e ".[dev,research]"
python -m e2t version
python -m pytest -q
Write-Host "OK — try: e2t run examples/sample_inputs/demo_article.md"
