$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$ModPath = Join-Path $PSScriptRoot "freecad_r8_mod\R8Live"
$MacroPath = $PSScriptRoot
$FcstdPath = Join-Path $RepoRoot "outputs\BambuMod_Orbiter25_Remix_R8\R8_Live_Workspace.FCStd"
$FreeCadExe = "C:\Program Files\FreeCAD 1.1\bin\freecad.exe"

if (-not (Test-Path $FcstdPath)) {
    & "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe" (Join-Path $PSScriptRoot "r8_live_builder.py")
}

Start-Process -FilePath $FreeCadExe -ArgumentList @(
    "-M", $ModPath,
    $FcstdPath
)
