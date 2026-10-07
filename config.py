"""Configuration management."""

import os
import sys
import json
from pathlib import Path


def _get_data_dir() -> Path:
    """Return the data directory.

    - When running from source: data/ next to the project.
    - When running as a PyInstaller bundle: a persistent user directory
      so screenshots and the SQLite DB survive app restarts.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller bundle
        if sys.platform == "win32":
            base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path.home() / ".local" / "share"
        return base / "XiaoheiDaily"
    return Path(__file__).parent / "data"


# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = _get_data_dir()
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "xiaohei.db"
SCREENSHOT_DIR = DATA_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

AI_BASE_URL = "http://localhost:11434/v1"
AI_API_KEY = "ollama"
AI_MODEL = "qwen3-vl:8b"

# Screenshot interval in seconds (configurable: 30, 60, 300)
SCREENSHOT_INTERVAL_SEC = int(os.environ.get("SCREENSHOT_INTERVAL_SEC", "60"))

# HTTP Server
HTTP_HOST = os.environ.get("HTTP_HOST", "127.0.0.1")
HTTP_PORT = int(os.environ.get("HTTP_PORT", "8089"))

# Preserve screenshots on disk
PRESERVE_SCREENSHOTS = True

# Max screenshots to keep (disk cleanup)
MAX_SCREENSHOTS = 2000
