' 小黑日报助手 - 一键停止
' 双击此文件停止后台运行的服务

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "taskkill /IM ""xiaohei-daily.exe"" /F", 0, True
