# 在桌面创建小黑日报助手的一键启动快捷方式
# 右键 PowerShell 执行：.\create-shortcut.ps1

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exePath = Join-Path $projectDir "dist\xiaohei-daily\xiaohei-daily.exe"
$vbsPath = Join-Path $projectDir "start.vbs"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "小黑日报助手.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)

if (Test-Path $exePath) {
    $Shortcut.TargetPath = $exePath
    $Shortcut.WorkingDirectory = Split-Path -Parent $exePath
    $Shortcut.IconLocation = $exePath
    $Shortcut.Description = "一键启动小黑日报助手"
} else {
    $Shortcut.TargetPath = $vbsPath
    $Shortcut.WorkingDirectory = $projectDir
    $Shortcut.IconLocation = "shell32.dll, 15"
    $Shortcut.Description = "一键启动小黑日报助手（源码模式）"
}

$Shortcut.Save()

Write-Host "快捷方式已创建: $shortcutPath"
