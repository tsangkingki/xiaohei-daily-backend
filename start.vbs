' 小黑日报助手 - 一键启动（无控制台窗口）
' 双击此文件即可后台启动服务

Set WshShell = CreateObject("WScript.Shell")
scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)
Set fso = CreateObject("Scripting.FileSystemObject")

exePath = scriptDir & "\dist\xiaohei-daily\xiaohei-daily.exe"
venvPython = scriptDir & "\.venv\Scripts\python.exe"
mainPath = scriptDir & "\main.py"

If fso.FileExists(exePath) Then
    ' 优先使用已打包的 exe
    WshShell.Run chr(34) & exePath & chr(34), 0, False
ElseIf fso.FileExists(venvPython) Then
    ' 退而求其次：使用项目虚拟环境
    WshShell.Run chr(34) & venvPython & chr(34) & " " & chr(34) & mainPath & chr(34), 0, False
Else
    ' 最后尝试：直接调用 python
    WshShell.Run "python " & chr(34) & mainPath & chr(34), 0, False
End If
