@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Double-click this file to build the executable.
:: Add --onefile after the command below if you want a single-file exe.

python build.py
if errorlevel 1 (
    echo.
    echo Build failed. Make sure Python is installed and on PATH.
    pause
)
