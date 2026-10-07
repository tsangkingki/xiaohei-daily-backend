@echo off
chcp 65001 >nul

:: 一键停止小黑日报助手

taskkill /IM "xiaohei-daily.exe" /F 2>nul
if errorlevel 1 (
    echo 没有正在运行的 xiaohei-daily.exe。
) else (
    echo 已停止 xiaohei-daily.exe。
)

timeout /t 1 /nobreak >nul
