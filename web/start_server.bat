@echo off
title Spectrum 分析工具 Web 服务器
echo.
echo ================================================
echo          Spectrum 分析工具 Web 版本
echo ================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo 正在检查依赖包...

REM 安装依赖包
pip install flask flask-cors psutil

if errorlevel 1 (
    echo 警告: 依赖包安装可能失败，但会尝试启动服务器...
    echo.
)

echo.
echo 正在启动 Web 服务器...
echo.
echo 服务器启动后请在浏览器中访问:
echo http://localhost:5000
echo.
echo 按 Ctrl+C 可以停止服务器
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 启动 Flask 应用
python app.py

pause
