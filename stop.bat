@echo off
echo Stopping PDF Note System...
taskkill /f /im python.exe /fi "WINDOWTITLE eq PDF Note System*" 2>nul
taskkill /f /im streamlit.exe 2>nul
taskkill /f /im uv.exe 2>nul
echo Service stopped
pause