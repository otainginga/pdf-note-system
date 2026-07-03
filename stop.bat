@echo off
chcp 65001 >nul
echo 正在停止PDF笔记系统...
taskkill /f /im python.exe /fi "WINDOWTITLE eq PDF笔记系统*" 2>nul
taskkill /f /im streamlit.exe 2>nul
taskkill /f /im uv.exe 2>nul
echo 服务已停止
pause