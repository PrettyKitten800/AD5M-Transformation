@echo off
setlocal
for %%I in ("%~dp0..\..") do set "REPO_ROOT=%%~fI"
set "MOD_PATH=%~dp0freecad_r8_mod\R8Live"
set "FCSTD_PATH=%REPO_ROOT%\outputs\BambuMod_Orbiter25_Remix_R8\R8_Live_Workspace.FCStd"
set "BUILDER_PY=%~dp0r8_live_builder.py"
set "FREECAD_EXE=C:\Program Files\FreeCAD 1.1\bin\freecad.exe"
set "FREECADCMD_EXE=C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"

if not exist "%FCSTD_PATH%" (
    echo Building initial R8 live workspace...
    "%FREECADCMD_EXE%" "%BUILDER_PY%"
)

start "FreeCAD R8 Live" "%FREECAD_EXE%" -M "%MOD_PATH%" "%FCSTD_PATH%"
