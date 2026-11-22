@echo off
title The Arena - Autonomous Launcher
cd /d "%~dp0"
echo ===================================================
echo             STARTING THE ARENA (PC)
echo ===================================================
echo.
python launch_arena.py
if errorlevel 1 (
    echo.
    echo [Notice] Python was not found on PATH or encountered an error.
    echo Trying python3 or launching runner directly...
    py -3 launch_arena.py
    if errorlevel 1 (
        echo.
        echo Please ensure Python 3 is installed and added to your system PATH.
        pause
    )
)
pause
