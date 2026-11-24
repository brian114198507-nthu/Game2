$ErrorActionPreference = 'Stop'
$godot = 'C:\Godot\Godot_v4.7.2-stable_win64.exe'
if (-not (Test-Path -LiteralPath $godot)) {
    throw "Godot 4.7.2 executable not found: $godot"
}
$publishDir = Join-Path $PSScriptRoot 'docs'
New-Item -ItemType Directory -Force -Path $publishDir | Out-Null
$output = Join-Path $publishDir 'index.html'
$started = Get-Date
$process = Start-Process -FilePath $godot -ArgumentList @(
    '--headless',
    '--export-release',
    'Web',
    'docs/index.html',
    'project.godot'
) -WorkingDirectory $PSScriptRoot -Wait -PassThru -NoNewWindow
if ($process.ExitCode -ne 0) {
    throw "Godot Web export failed with exit code $($process.ExitCode)"
}
if (-not (Test-Path -LiteralPath $output) -or (Get-Item -LiteralPath $output).LastWriteTime -lt $started) {
    throw "Godot completed without updating $output"
}
$html = Get-Content -LiteralPath $output -Raw -Encoding utf8
$html = $html.Replace('<html lang="en">', '<html lang="zh-Hant">')
[System.IO.File]::WriteAllText($output, $html, [System.Text.UTF8Encoding]::new($false))
Get-ChildItem -LiteralPath $publishDir -Filter '*.import' -File | Remove-Item -Force
Write-Output "Web build ready: $publishDir"
