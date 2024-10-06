@echo off
set CURRENT_DIR=%cd%

if defined PYTHONPATH (
    set PYTHONPATH=%PYTHONPATH%;%CURRENT_DIR%
) else (
    set PYTHONPATH=%CURRENT_DIR%
)

echo PYTHONPATH is now: %PYTHONPATH%
