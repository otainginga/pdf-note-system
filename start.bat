@echo off
chcp 65001 >nul
title PDF笔记系统

echo ========================================
echo    PDF双页阅读笔记系统
echo ========================================
echo.

:: 清理旧进程
echo [1/4] 清理旧进程...
taskkill /f /im python.exe /fi "WINDOWTITLE eq PDF笔记系统*" 2>nul
taskkill /f /im streamlit.exe 2>nul
taskkill /f /im uv.exe 2>nul
timeout /t 2 /nobreak >nul

:: 检查uv环境
echo [2/4] 检查uv环境...
uv --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到uv，请先安装uv
    echo 安装命令: pip install uv 或 winget install astral-sh.uv
    pause
    exit /b 1
)

:: 同步依赖
echo [3/4] 同步依赖包...
uv sync

:: 设置环境变量
set STREAMLIT_SERVER_PORT=8103
set STREAMLIT_SERVER_ADDRESS=0.0.0.0
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

:: 启动应用
echo [4/4] 启动应用...
echo 访问地址: http://localhost:8103
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

uv run streamlit run app.py --server.port 8103 --server.address 0.0.0.0

pause