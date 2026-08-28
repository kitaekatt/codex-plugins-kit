$ErrorActionPreference = "Stop"
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($Python) {
    & $Python.Source "$PSScriptRoot/manage.py" doctor @args
} else {
    py -3 "$PSScriptRoot/manage.py" doctor @args
}
exit $LASTEXITCODE
