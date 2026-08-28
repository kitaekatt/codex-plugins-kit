$ErrorActionPreference = "Stop"
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($Python) {
    & $Python.Source "$PSScriptRoot/manage.py" setup @args
} else {
    py -3 "$PSScriptRoot/manage.py" setup @args
}
exit $LASTEXITCODE
