@echo off
title PDF Note System

echo ========================================
echo    PDF Dual-Page Note System
echo ========================================
echo.

:: Clean up old processes
echo [1/4] Cleaning up old processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq PDF Note System*" 2>nul
taskkill /f /im streamlit.exe 2>nul
taskkill /f /im uv.exe 2>nul
timeout /t 2 /nobreak >nul

:: Check uv environment
echo [2/4] Checking uv environment...
uv --version >nul 2>&1
if errorlevel 1 (
    echo Error: uv not found, please install uv first
    echo Install command: pip install uv or winget install astral-sh.uv
    pause
    exit /b 1
)

:: Sync dependencies
echo [3/4] Syncing dependencies...
uv sync

:: Set environment variables
set STREAMLIT_SERVER_PORT=8103
set STREAMLIT_SERVER_ADDRESS=0.0.0.0
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

:: Start application
echo [4/4] Starting application...
echo Access URL: http://localhost:8103
echo Press Ctrl+C to stop the service
echo ========================================
echo.

uv run streamlit run app.py --server.port 8103 --server.address 0.0.0.0

pause