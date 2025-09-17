import asyncio
import logging
import sys

try:
    from livekit.agents import function_tool
except ImportError:
    def function_tool(func): 
        return func

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

# Setup encoding and logger
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# Focus utility
# -------------------------
async def focus_window(title_keyword: str) -> bool:
    if not gw:
        logger.warning("⚠ pygetwindow missing")
        return False

    await asyncio.sleep(1.5)  # wait for window
    title_keyword = title_keyword.lower().strip()

    for window in gw.getAllWindows():
        if title_keyword in window.title.lower():
            if window.isMinimized:
                window.restore()
            window.activate()
            return True
    return False

# -------------------------
# Open App (Start Menu search)
# -------------------------
@function_tool()
async def open_app(app_title: str) -> str:
    """
    Opens an app by searching in Start Menu (no need for path).
    Example:
    - "open facebook"
    - "notepad kholo"
    """
    app_title = app_title.lower().strip()

    try:
        if pyautogui:
            pyautogui.press("win")          # Open Start
            await asyncio.sleep(1)
            pyautogui.typewrite(app_title)  # Type app name
            await asyncio.sleep(1.2)
            pyautogui.press("enter")        # Launch app
            await asyncio.sleep(2)
            focused = await focus_window(app_title)
            return f"🚀 {app_title} खोला गया। Focus: {focused}"
        else:
            return "⚠ pyautogui missing"
    except Exception as e:
        return f"❌ {app_title} खोलने में समस्या आई: {e}"

# -------------------------
# Close App
# -------------------------
@function_tool()
async def close_app(window_title: str) -> str:
    """
    Closes the application window by matching title.
    Example:
    - "close facebook"
    - "notepad बंद करो"
    """
    if not win32gui:
        return "⚠ win32gui missing"

    closed = []

    def enumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                closed.append(hwnd)

    win32gui.EnumWindows(enumHandler, None)

    if closed:
        return f"🛑 '{window_title}' बंद कर दिया गया है।"
    else:
        return f"⚠ '{window_title}' नाम की कोई window नहीं मिली।"


@function_tool()
async def folder_file(path: str) -> str:
    """
    Opens a folder or file in File Explorer.
    Example:
    - "open downloads"
    - "folder D:\\Movies"
    """
    import os
    import subprocess

    try:
        if os.path.exists(path):
            subprocess.Popen(f'explorer "{path}"')
            return f"📂 '{path}' खोला गया।"
        else:
            return f"⚠ '{path}' मौजूद नहीं है।"
    except Exception as e:
        return f"❌ '{path}' खोलने में समस्या: {e}"
