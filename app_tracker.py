"""Foreground app tracker — macOS (osascript) + Windows (ctypes). No extra deps."""

import platform
import subprocess
import logging
from datetime import datetime, timezone

log = logging.getLogger("app_tracker")

_current_app = None
_current_start = None

_SYSTEM = platform.system()  # "Darwin", "Windows", "Linux"

_FRONTMOST_SCRIPT = '''
tell application "System Events"
    set frontApp to first application process whose frontmost is true
    set appName to name of frontApp
    try
        set winTitle to title of front window of frontApp
    on error
        set winTitle to ""
    end try
    return appName & "||" & winTitle
end tell
'''


def _get_frontmost_context_macos() -> dict:
    try:
        result = subprocess.run(
            ["osascript", "-e", _FRONTMOST_SCRIPT],
            capture_output=True, text=True, timeout=5
        )
        out = result.stdout.strip()
        parts = out.split("||", 1)
        app = parts[0] if parts and parts[0] else "Unknown"
        title = parts[1] if len(parts) > 1 else ""
        return {"app": app, "windowTitle": title}
    except Exception as e:
        log.debug("get_frontmost_context (macOS) failed: %s", e)
        return {"app": "Unknown", "windowTitle": ""}


def _get_frontmost_context_windows() -> dict:
    """
    Uses only ctypes + the Win32 API (user32/kernel32) — no pywin32/psutil
    required. Reads the foreground window's title and the .exe name of the
    process that owns it.
    """
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        user32.GetForegroundWindow.restype = wintypes.HWND
        user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return {"app": "Unknown", "windowTitle": ""}

        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value or ""

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        app = "Unknown"
        if pid.value:
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            kernel32.OpenProcess.restype = wintypes.HANDLE
            kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
            if h_process:
                try:
                    buf_size = wintypes.DWORD(260)
                    name_buf = ctypes.create_unicode_buffer(buf_size.value)
                    kernel32.QueryFullProcessImageNameW.argtypes = [
                        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)
                    ]
                    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
                    ok = kernel32.QueryFullProcessImageNameW(h_process, 0, name_buf, ctypes.byref(buf_size))
                    if ok:
                        full_path = name_buf.value
                        exe_name = full_path.split("\\")[-1]
                        app = exe_name[:-4] if exe_name.lower().endswith(".exe") else exe_name
                finally:
                    kernel32.CloseHandle(h_process)

        return {"app": app or "Unknown", "windowTitle": title}
    except Exception as e:
        log.debug("get_frontmost_context (Windows) failed: %s", e)
        return {"app": "Unknown", "windowTitle": ""}


def get_frontmost_context() -> dict:
    """
    获取前台应用上下文：{app, windowTitle}。
    macOS 下窗口标题需要"辅助功能"权限；拿不到则降级为只有 app 名。
    Windows 下通常都能拿到标题；没有前台窗口（如刚切到桌面）时降级为 Unknown。
    """
    if _SYSTEM == "Darwin":
        return _get_frontmost_context_macos()
    elif _SYSTEM == "Windows":
        return _get_frontmost_context_windows()
    else:
        log.debug("get_frontmost_context: unsupported platform %s", _SYSTEM)
        return {"app": "Unknown", "windowTitle": ""}


def get_frontmost_app() -> str:
    """兼容旧接口：只返回应用名。"""
    return get_frontmost_context()["app"]


def tick():
    """
    周期调用（如每次截图间隔）。追踪前台应用切换，返回已结束的 session。
    返回 [(app_name, started_at_iso, ended_at_iso, duration_sec), ...]
    """
    global _current_app, _current_start

    now = datetime.now(timezone.utc)
    app = get_frontmost_app()
    sessions = []

    if app != _current_app:
        if _current_app and _current_start:
            duration = (now - _current_start).total_seconds()
            if duration > 5:  # 忽略极短切换
                sessions.append((
                    _current_app,
                    _current_start.isoformat(),
                    now.isoformat(),
                    int(duration),
                ))
        _current_app = app
        _current_start = now

    return sessions


def flush():
    """关闭时 flush 当前 session。"""
    global _current_app, _current_start
    sessions = []
    if _current_app and _current_start:
        now = datetime.now(timezone.utc)
        duration = (now - _current_start).total_seconds()
        if duration > 5:
            sessions.append((
                _current_app,
                _current_start.isoformat(),
                now.isoformat(),
                int(duration),
            ))
    _current_app = None
    _current_start = None
    return sessions