$ErrorActionPreference = "Stop"
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($Python) {
    & $Python.Source "$PSScriptRoot/manage.py" uninstall @args
} else {
    py -3 "$PSScriptRoot/manage.py" uninstall @args
}
exit $LASTEXITCODE
