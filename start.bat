@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: 一键启动小黑日报助手
:: 优先使用已打包的 exe，否则用 Python 源码运行

if exist "dist\xiaohei-daily\xiaohei-daily.exe" (
    start "" "dist\xiaohei-daily\xiaohei-daily.exe"
    exit /b 0
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    echo 未找到打包的 exe，也未找到 .venv。
    echo 请先双击 build.bat 构建，或安装 Python 后运行 python main.py。
    pause
)
