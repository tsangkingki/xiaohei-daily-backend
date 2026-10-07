#!/usr/bin/env python3
"""Build the xiaohei-daily backend into a Windows executable.

Usage:
    python build.py              # build folder-based exe (recommended)
    python build.py --onefile    # build a single-file exe

The first run will create .venv and install dependencies automatically.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
VENV = ROOT / ".venv"
DIST = ROOT / "dist"
BUILD = ROOT / "build"
SPEC = ROOT / "xiaohei-daily.spec"

ON_WINDOWS = sys.platform == "win32"
PY = VENV / ("Scripts/python.exe" if ON_WINDOWS else "bin/python")
PIP = VENV / ("Scripts/pip.exe" if ON_WINDOWS else "bin/pip")


def run(cmd, cwd=None, check=True):
    print(f"> {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, cwd=cwd, check=check)


def ensure_venv():
    if not VENV.exists():
        print("Creating virtual environment...")
        run([sys.executable, "-m", "venv", str(VENV)])

    print("Installing dependencies...")
    run([str(PIP), "install", "-r", str(ROOT / "requirements.txt")])


def build():
    onefile = "--onefile" in sys.argv
    mode = "onefile" if onefile else "onedir"

    ensure_venv()

    # Ensure PyInstaller itself is available in the venv
    try:
        run([str(PY), "-c", "import PyInstaller"])
    except subprocess.CalledProcessError:
        print("Installing PyInstaller...")
        run([str(PIP), "install", "pyinstaller>=6.0"])

    # Clean previous builds so the output is fresh
    for path in (BUILD, SPEC):
        if isinstance(path, Path) and path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    if DIST.exists():
        shutil.rmtree(DIST)

    cmd = [
        str(PY),
        "-m",
        "PyInstaller",
        "--name", "xiaohei-daily",
        "--noconfirm",
        "--clean",
        "--noconsole",  # run without a terminal window
        "--hidden-import", "openai",
        "--hidden-import", "flask_cors",
        "--hidden-import", "apscheduler.triggers.interval",
        "--hidden-import", "apscheduler.triggers.cron",
        "--add-data",
        f"{ROOT / 'frontend'}{os.pathsep}frontend",
        str(ROOT / "main.py"),
    ]
    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    run(cmd)

    # Copy the frontend dashboard next to the executable so users can open it
    src_frontend = ROOT / "frontend"
    if src_frontend.exists():
        dst = DIST / "xiaohei-daily" / "frontend"
        dst.mkdir(parents=True, exist_ok=True)
        if (dst / "xiaohei-dashboard.html").exists():
            shutil.rmtree(dst)
        shutil.copytree(src_frontend, dst)

    exe_path = DIST / "xiaohei-daily" / "xiaohei-daily.exe"
    print("\n" + "=" * 50)
    print(f"Build complete: {mode} mode")
    print(f"Executable: {exe_path}")
    print("=" * 50)
    print("Double-click the executable or use start.vbs to run it.")


if __name__ == "__main__":
    build()
