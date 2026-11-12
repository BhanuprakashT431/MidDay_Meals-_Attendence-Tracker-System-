@echo off
title Smart-Nourish & Attend - Karnataka PM-POSHAN System
cd /d "%~dp0"
cls
echo ================================================================
echo   Launching Smart-Nourish & Attend Server
echo ================================================================
echo.
python run_server.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server encountered an error.
    pause
)
