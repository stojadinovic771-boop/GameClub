"""
GAMES - Xbox Controller Shortcut Launcher for Windows 11
Requirements : pip install pygame   (or pip install pygame-ce)
Optional      : pip install Pillow   (enables real .exe/.lnk icons)
Run           : python xbox_file_browser.py

Shortcuts (.lnk / .url / .exe / .bat / .cmd) are collected from the Shortcuts
Folder (and its subfolders) and sorted into three tabs: APPS, PC GAMES and
EMULATION. The category is auto-detected; press X on a shortcut to move it.
"""

import os
import re
import sys
import math
import time
import json
import tempfile
import threading
import subprocess
import urllib.request
import urllib.parse
import ssl
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode    = ssl.CERT_NONE
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import pygame

APP_NAME     = "GameClub"
# 64 px window / taskbar icon (the "Library" design), embedded so it also shows
# when running straight from PyCharm. The installer uses padhub.ico.
APP_ICON_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAMC0lEQVR42tVbTYxcRxH+qrrf/OyPvWt77cRxsJ2gJCI/2EocI8vR"
    "RhCCIyAXtOKSIIGEEJeIcACJy8pcEYEDFyIQiRC/BkVKLgk54FWC4wQWxcQ4ITEmENvrzf57d2bezOuu4vDezM6MZ3fe7Kzj9Vu1"
    "9Gbndb+u6qqvqr7uIazpGuXh4eMMAEtLS4RrePX19SkAjD34oODoUbma76Lh4WEL4JoK3O7qdI6pHhwZGTHHjh3z1c8PPPDFvY5x"
    "JwF7obpFVa+dUsjMEfAfIT1zcuyFs01zFgDajQI4GUAPHz4yJMY+pqARqO43xuaI6NrbgwKqCu9dhYhOKeGPVKFfnjjx/MWquwIr"
    "u8aK0x8dHeWjsU/RoeEvfAvAd42xO1QF3nuoqgdIN4bhKxGRYTZgNvDezUDxVLlw8Qfj4+NRswW3VUC1w/33H9llc+ZZY4NPe+cg"
    "Ig4AE4E2IBaoKhSAMJM1NoDz0Wtajr5y8uSfzq6kBGqx9IyjR+XA4Udus2xeMsbsca4SAbThAbDJMZyxQSBeLjlXfuSvJ15+s5US"
    "qJXPHzr00I1icicM827nnCOGheL6ughQgTPWWKh+COcOnTjx4r+bMYHru4yMjBBGR8lT8BtjzG7nIkd0HQqf2AARrHfeEfF2T/z7"
    "jx85kh0ZOdPgvqbZ7w+6nidsJvMNF1UiEIKPcsaxE3f2F0u6qiWwiI9sJrMrG3r38ovP/3lkZMScOXNG612AAODAgc9s4UzmXSIa"
    "UBUAxFd9mQCoVhXQ+P80dk7UfE8t8ZGIVBWhRnr7G2+8eD6xfuEkezIAlDLB49baLSIi8QOKq9lUFaIKVYGoQAAIAQKqNd/U6r8T"
    "Qq2/QhILkhbvAomoWGt7KNCvJzLzFRZw/6GHX2cT3Oe9E6pzjy4TydbmDq0lMdVpShRCReoMj1a0mthcFBxkQWxjlRDH8ZlazkvY"
    "GPLe/6snCO8eGxvzAGCrqHjw4Of2KPBJ9Y6oERzbpWFrQui4q0CVIOohorA374cZ3AmlBKeoRbfEXQiAlotwH/wDsjQNzuQBERAR"
    "tLUSWLxXAt1eqGTuAHB6dHSU7fDwcR4bg3iSu60JMt5FnohMGu8lEDjIdQQVKg7iyvHKKyDqoTaLvs8+gcxth+OxKDV8QBanUHjp"
    "x4jeH4fJ5CDQFVdPFd5aa8X7fQBOHz9+nO2yevUWAkE1bXpLMLk+UN0Q6TSQBcBw5QKEGL5SRs8DX0P2rochi1PJ0JQ29wP3bUXv"
    "kW9j4VdPQgozYGPrlEDNjyexn26tlvJcrecJNJgawFRgbCYWXrXDJmCbBYyBSgTuHUTm1oOQ0kK8+mwSK2AQc+2+ZWMDDZfA/UMI"
    "9t4LceWan6iuAr6ig1UugetzwNh/tCEIrTQM2KC7RI3jSWbyIJNpiXmhi2fCq8b5GFAo17c8t/p5NnzWGBu4MfUFAMxOz6IYlsDM"
    "IEJjorGyGtYY+ZfH1xXKKlXgjm0BRIFCpDBpoIGolkwti6yJ4AAzoxSGmJ2dr3WpOXAYVhC5OWQzFn39fQgCC5WqKXXglymD4Gph"
    "lAlYrCi+eW8PAkP44WtLODMVoS/DCAzgJR0+IIkGxAQXOSwuFVAuR3BuuR7i8epNouFisYTpqRnMz1+Gcz7xw0SzDa2rOiVeF9Uk"
    "oLV+qOSAfTcE+PmjA3jyU33IWcJ8qfW7FfVQExcCxATnPRYWFjE1PYtioViTFQDG6i1AAFDiIwrF0lIBxVIJ+VwOPT15BIEFEUGk"
    "OxdoXPnVx2ECRAHLhMfu6cHwniyeebOIV/5XRsW3tp8qSRVFEcIwRKkUwnsBMyW5gSbSNrlAooHEdAicvL1QKKBULCKTySCfzyOb"
    "zdQN1mUZkEKPTEAksSJu3mTwnUN9uLjocWoyQt5STZQ4hAvCMES5WEQURRBVMHEsS81EGuSvU0ASPWv+WY2ZFP8vLJcRhmUYa5AJ"
    "LAa35pG11BQzOpef2jwjCgSJyb7wboif/b2ImaJHzhIkkYeJUC6XMTc3D+UAEA9mqs0d2piC10OITQtYVQLUi2CpUEBPfwW5HoKK"
    "rg0g21iAArAcW8DpDyP8dLyI185XkLdANhG+rg6Ecw7Oe1iTqc0nzeLYK5CzDboRUUwKdukCRMk8qbXwhoC5kuDp8QKePVWEE2Ag"
    "G5u8aAtIqZYOq8lQ+64FBshyjZI6lq9deEKhUESxuICAezAgceqawA9UgR5L+NHJJSyEit4MIWcBv9qLpVoWdzb3OhCslqHaXkJd"
    "YxVYd0WVCsJiCZovt/QFBRB5oD8bm7toCn8SqZtbq+XUZSBswQl2QGYApdISiGt2l7KGUDAzRDwqlRKMDeALc3CFeYAtVH3DPIhi"
    "wqRdXQIQKjPnO5BBWisglRiiIGYsXp7D3MwkiOLNCGbbvhkDEcHU5HlElTKIGb50GTOv/hom2xPX9EQAmdWLoLrvg807sPTeG1h8"
    "+xVwkIOK70D8pjAI5XSmnfCQ05c+wOLCDIIgmyAurdghjtOKcrkUC08M9Q6cyWPu9edAbLB1+HHYnsEapdvOkVUc5v55HJdeeAoa"
    "hbXqlFYEs8QFpIMwuCqYMaMcFhGWih0BIDMvk6DiwTbA7Ku/xcKbL8Fu2l5Lv1vXC8ultZSLqMxeALFJhJeOqTqL8ToMpLriJ2Us"
    "q1JUnaTBy10SJXgPzvZAwgJKhfeaVp9W5ASJCCbIxmYvvqbglWWoyie1YqArCxDvkM3mYYNM6tynEhbhXARmk1DZsfP4qAJjLXp7"
    "BmJ3SZFHuKiCcljqKjVfGwYQoCLYtv0mDGzZEZtsysu7CB9efB9LiwtgEytBxaO3tx9DN+5GEAQN9FW7Wury/BSmJ88jITHaWGMV"
    "A3TtUQAEeO/Ru2kQW7fvSsBI0jXvYW2A7Tv3wgYBRASqAmaLHTv3IJvNpUsx6tKGrUM3oX9gG7xz8cKkDuRrzgMAqKC3d3NCa3eG"
    "GSKxEnL53ri/CLK5PGwmC0lo7bQtxq54LvU7TOiAyboyE0wZBrEeO6ZV1qZLVqE+0UrlAutRC3QrfjOBSV2OqR3MXbqpBtsjVFpW"
    "dDmN7Up0QsNW2epzuzIRusq7vxv/amKE0jE8morPSblB2kWBrU2cv6I9BsR80Kqc4DUCAeAj4Ribv7etVzYtr79+OwTrJ72mtLor"
    "ooCAlVLFde0yfKFuX6B+vG4PS2pbEE+KKJVuQfB6PDWVhhTtKJqujwPQup43SpEIrZwJAkrp04CY1KCOzbdKWEeVMkhjajiqlNfk"
    "DppsfERRGSIK5pR1RCMhEp+3V5IFatiyWuWlzJibmcCmwW3I5/sgIqlPdbAxmJ26gGLhMpgNiIAwLGB2egJDN3wM4n1qcGFilMMS"
    "ZqcvgpnrzgS01cBCfL9ENt4iBAg4F+8Gp9mFJkRRBf89+xa2bNuJTDaX2imKSwuYm7kUFzOqiPdVCJMXziEsFdDXP5hKAYTYCmen"
    "J1CphHUKaEdiAAqciz+MK1XPyw0N3XyrB95J3CJFlhPvxYn49GSExn5vTGsexnvXdPYvhQuwAVXp/JRspoHfPzV14RTi/Zdl1xwc"
    "2jXOxPs0PiVp1u0XFykhlK5uPBICWBRn56a3fwIYd/UgaAA4iP5OGfu1AyRaz4B4lYOrEDED8gdgPEpkd9U8wANAxWSeEfWXk1Oi"
    "erVPin6ETQFlUV8Ww0/XJf8NZm6iwvxiLreJmPkhqLq0bnAdXJ6YjYo8tTB9/lgilzS7XQKI9/LAlom/EPMBVXHd7h1sCOGJjKq+"
    "nc/ofRMTE2HDYbcr06TxSAP/ZRWZJJBNLOH6vBQeICOqCyR+ZGJiotgMN62A1wDwmzfv3EcGLxLRDlWpgsZ19JMZOCIKVHWelD4/"
    "N3fxRFW2ZmFbnk8olxcngt7+5wE9SMQfi0/0Va2BNqgiVGIByRCxUdW3SPyj8/OX/tZK+Haht9ohs3lwx/cAepKINy1vL8FvoLKQ"
    "ABgQVQ9LFVXxk8tZ/T4mJwsrCZ/2h5MCAAMDN+xW0q9C6Usg3EUbzAiSOuAdgJ4T536xuDj9XrMMa02+qulyVYM8OLj9Tq+4B+Bb"
    "QLrlmmID0ZwKzrH6txYWpk4DcHUWLOtppXydhETbCdFDa/Q32oCUuq5lxf8PA0uxVmuBN/UAAAAASUVORK5CYII="
)


def _set_window_icon() -> None:
    try:
        import base64, io
        icon = pygame.image.load(io.BytesIO(base64.b64decode("".join(APP_ICON_PNG))), "icon.png")
        pygame.display.set_icon(icon)
    except Exception:  # noqa: BLE001
        pass


APP_BUILD    = "2026-11-15 v48 (GameClub 1.0 - GameCube / Game Boy folders go to Emulation)"
CONFIG_FILE  = os.path.join(os.path.expanduser("~"), ".games_browser_config.json")
STATS_FILE   = os.path.join(os.path.expanduser("~"), ".games_browser_stats.json")
SORT_MODES   = ["A\u2013Z", "Recently played", "Most played"]
SORT_KEYS    = {"apps": "sort_apps", "pc_games": "sort_pc_games", "emulation": "sort_emulation"}

# Start Folder and SteamGridDB key are intentionally left blank here so that,
# on a fresh install, the user enters them manually via Settings.
# An empty start_folder makes the launcher fall back to Desktop/home on first
# launch (see _scan) and show a prompt to set the folder in Settings.
DEFAULT_CONFIG = {
    "start_folder": "",
    "icon_size":    100,
    "columns":      6,
    "scroll_speed": "Normal",
    "button_style": "Xbox",
    "accent":       "Blue",
    "background":   "Solid",
    "wallpaper":    "",
    "wallpaper_blur": "Off",
    "sort_apps":      "A\u2013Z",
    "sort_pc_games":  "A\u2013Z",
    "sort_emulation": "A\u2013Z",
    # Desktop mouse (controller as mouse after "Go to Desktop"), 1 = slow … 10 = fast
    "desktop_mouse": True,            # controller works as a mouse outside GameClub
    "mouse_speed":  3,
    "mouse_accel":  2,
    "mouse_scroll": 4,
    "mouse_stick":  "Right stick",    # stick that moves the pointer; the other one scrolls
    "mouse_clicks": "RT left \u00b7 LT right",   # or "LT left · RT right"
    "osk_pos":      "Bottom",         # where the on-screen keyboard opens
    "sgdb_api_key": "",
    "startup_with_windows": False,
    "secure_desktop": False,    # controller works on UAC prompts & the sign-in screen
    "scan_subfolders": True,
    "last_tab":     1,      # 0=Apps, 1=PC Games, 2=Emulation
    "categories":   {},     # manual overrides: {normalized path: category}
}

C_BG       = ( 40,  40,  45)
UI_SCALE   = 1.7   # global UI scale factor — increase for higher-DPI screens

def _s(n): return int(n * UI_SCALE)  # scale helper
C_PANEL    = ( 22,  24,  30)
C_CARD     = ( 30,  33,  42)
C_CARD_HOV = ( 38,  58,  94)
C_ACCENT   = ( 54, 147, 222)
C_ACCENT2  = (143, 200, 243)

# Accent color themes: (accent, light accent for text, selected-card fill)
ACCENTS = {
    "Blue":   (( 54, 147, 222), (143, 200, 243), ( 38,  58,  94)),
    "Purple": ((150, 110, 230), (200, 180, 250), ( 60,  46,  96)),
    "Teal":   (( 40, 180, 190), (140, 225, 230), ( 26,  70,  78)),
    "Green":  (( 60, 180, 120), (150, 225, 185), ( 34,  74,  58)),
    "Orange": ((235, 140,  50), (250, 200, 140), ( 92,  60,  30)),
    "Red":    ((220,  70,  80), (245, 160, 165), ( 90,  36,  42)),
    "Pink":   ((230,  90, 170), (248, 170, 215), ( 92,  38,  72)),
}
_accent_name = "Blue"


def set_accent(name: str) -> None:
    """Recolor every highlight in the app (read by draw code at draw time)."""
    global C_ACCENT, C_ACCENT2, C_CARD_HOV, _accent_name
    _accent_name = name if name in ACCENTS else "Blue"
    C_ACCENT, C_ACCENT2, C_CARD_HOV = ACCENTS[_accent_name]
C_TEXT     = (210, 220, 230)
C_TEXT_DIM = ( 90, 100, 115)
C_WHITE    = (255, 255, 255)
C_GREEN    = ( 77, 181, 108)
C_RED      = (194,  56,  56)
C_YELLOW   = (195, 155,  30)
C_GRAY     = ( 45,  50,  63)
C_BTN_A    = ( 77, 181, 108)
C_BTN_B    = (194,  56,  56)
C_BTN_X    = ( 54, 147, 222)
C_BTN_Y    = (195, 155,  30)

FILE_COLORS = {
    "folder":  ( 26, 159, 255),
    ".exe":    ( 54, 186, 118), ".bat":  ( 54, 186, 118), ".cmd": ( 54, 186, 118),
    ".py":     ( 54, 140, 210),
    ".pdf":    (210,  65,  65),
    ".jpg":    (160,  95, 190), ".jpeg": (160,  95, 190),
    ".png":    (160,  95, 190), ".gif":  (160,  95, 190),
    ".mp4":    (210, 120,  40), ".mkv":  (210, 120,  40), ".avi": (210, 120,  40),
    ".mp3":    (110,  75, 200), ".wav":  (110,  75, 200),
    ".zip":    ( 80, 165,  95), ".rar":  ( 80, 165,  95), ".7z":  ( 80, 165,  95),
    ".docx":   ( 54, 140, 210), ".doc":  ( 54, 140, 210),
    ".xlsx":   ( 20, 155,  75), ".xls":  ( 20, 155,  75),
    ".pptx":   (190,  75,  30),
    "default": ( 80,  95, 120),
}

ALWAYS_HIDE      = {"desktop.ini", "thumbs.db", "ntuser.dat", "$recycle.bin"}
CREATE_NO_WINDOW = 0x08000000

# ── CATEGORIES ────────────────────────────────────────────────────────────────
CATEGORIES      = ["apps", "pc_games", "emulation"]
CATEGORY_LABELS = {"apps": "APPS", "pc_games": "PC GAMES", "emulation": "EMULATION"}
CATEGORY_NAMES  = {"apps": "Apps", "pc_games": "PC Games", "emulation": "Emulation"}

LAUNCH_EXTS       = {".lnk", ".url", ".exe", ".bat", ".cmd"}
MAX_SCAN_DEPTH    = 4
TARGET_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".games_browser_targets.json")

# Executable name prefixes of emulators and emulation front-ends
EMULATOR_PREFIXES = (
    "retroarch", "dolphin", "pcsx2", "rpcs3", "yuzu", "ryujinx", "citron",
    "sudachi", "torzu", "suyu", "citra", "lime3ds", "azahar", "cemu", "xenia",
    "duckstation", "ppsspp", "melonds", "desmume", "mgba", "vita3k", "xemu",
    "flycast", "redream", "snes9x", "bsnes", "mesen", "project64", "simple64",
    "shadps4", "epsxe", "nestopia", "fceux", "dosbox", "scummvm", "es-de",
    "emulationstation", "retrobat", "launchbox", "bigbox", "pegasus-fe",
    "visualboyadvance", "visualboyadvance-m", "kega", "fusion", "mupen64",
    "openemu", "zsnes", "higan", "gopher64", "rmg", "xenos",
)
# Short names that must match exactly (too generic for a prefix match)
EMULATOR_EXACT = {"ares", "mame", "mame64", "eden", "pcsx", "nulldc", "fbneo"}

# Executable names that are apps / launchers rather than games
APP_STEMS = {
    "chrome", "firefox", "msedge", "opera", "brave", "vivaldi", "discord",
    "update", "spotify", "vlc", "mpc-hc", "mpc-hc64", "mpc-be64", "obs64",
    "obs", "explorer", "notepad", "notepad++", "code", "steam",
    "epicgameslauncher", "galaxyclient", "upc", "ubisoftconnect", "eadesktop",
    "origin", "battle.net", "battle.net launcher", "playnite.desktopapp",
    "playnite.fullscreenapp", "msiafterburner", "rtss", "teams", "ms-teams",
    "zoom", "telegram", "whatsapp", "kodi", "plex", "plex media player",
    "jellyfin media player", "moonlight", "parsec", "sunshine", "steamlink",
    "ds4windows", "x360ce", "rufus", "7zfm", "qbittorrent", "cmd",
    "powershell", "pwsh", "wt", "windowsterminal", "taskmgr", "control",
    "mmc", "snippingtool", "calc", "mspaint", "winword", "excel", "powerpnt",
    "outlook", "onenote", "acrobat", "acrord32", "gimp", "krita", "blender",
    "heroiclauncher", "heroic", "itch", "amazon games", "eaapp",
    "riotclientservices", "goggalaxy", "geforcenow", "nvidia app",
    "nvcontainer", "xboxpcapp", "gamebar", "displayfusion", "joytokey",
    "steamrommanager", "steam rom manager", "anydesk", "teamviewer",
}

# File extensions that mean "this is a ROM / disc image"
ROM_EXTS = (
    "iso", "cso", "chd", "cue", "rvz", "wbfs", "gcm", "gcz", "wia", "nsp",
    "xci", "nca", "nro", "3ds", "cia", "cci", "cxi", "nds", "gba", "gbc", "gb",
    "sfc", "smc", "nes", "z64", "n64", "v64", "pbp", "pkg", "wua", "wux",
    "rpx", "xex", "md", "gen", "sms", "gg", "pce", "32x", "ws", "wsc", "a26",
    "lnx", "ngp", "vb", "m3u", "cdi", "gdi",
)
ROM_EXT_SET = {"." + e for e in ROM_EXTS}
_ROM_RE     = re.compile(r"\.(" + "|".join(ROM_EXTS) + r")(?=[\"'\s]|$)", re.IGNORECASE)

GAME_URL_PREFIXES = (
    "steam://", "com.epicgames.launcher://", "uplay://", "origin://",
    "origin2://", "goggalaxy://", "battlenet://", "heroic://", "itch://",
    "amazon-games://", "eadesktop://", "link2ea://",
)


def _cat_key(path: str) -> str:
    """Normalised path used as the key for manual category overrides."""
    return os.path.normcase(os.path.abspath(path))


def _folder_hint(rel_dir: str):
    """Category implied by the subfolder a shortcut lives in (nearest wins)."""
    parts = [p.lower() for p in rel_dir.replace("/", "\\").split("\\") if p and p != "."]
    for part in reversed(parts):
        words = set(re.split(r"[^a-z0-9]+", part))
        if "emulat" in part or part.startswith("retro") or words & {"emu", "emus", "rom", "roms"}:
            return "emulation"
        if "application" in part or words & {"app", "apps", "tool", "tools",
                                             "utility", "utilities", "programs",
                                             "software"}:
            return "apps"
        # whole words only: "Games", "PC Games", "Steam Games" — but not system
        # names such as "GameCube", "Game Boy" or "Game Gear" (those are Emulation)
        if words & {"games", "pcgames"} or part in ("game", "pc", "pc game"):
            return "pc_games"
    return None


def _is_emulator_stem(stem: str) -> bool:
    return bool(stem) and (stem in EMULATOR_EXACT or stem.startswith(EMULATOR_PREFIXES))


def detect_category(full_path: str, rel_dir: str, target: str = "", args: str = "") -> str:
    """Best-guess category for a shortcut. Order of checks:
    subfolder name → URL scheme → emulator exe / ROM argument → known app → PC game.
    """
    hint = _folder_hint(rel_dir)
    if hint:
        return hint

    name      = os.path.basename(full_path)
    ext       = os.path.splitext(name)[1].lower()
    name_stem = os.path.splitext(name)[0].lower()

    if ext == ".url":
        url = target.strip().lower()
        if url.startswith(GAME_URL_PREFIXES):
            return "pc_games"
        if url.startswith(("http://", "https://")):
            return "apps"
        return "pc_games"

    tgt   = target if ext == ".lnk" else full_path
    tl    = (tgt or "").lower()
    stem  = os.path.splitext(os.path.basename(tl))[0]
    t_ext = os.path.splitext(tl)[1]

    if _is_emulator_stem(stem):
        return "emulation"
    if t_ext in ROM_EXT_SET or (args and _ROM_RE.search(args)):
        return "emulation"
    if stem in APP_STEMS:
        return "apps"
    windir = os.environ.get("WINDIR", r"C:\Windows").lower().rstrip("\\")
    if tl.startswith(windir + "\\"):
        return "apps"

    # Target unknown (e.g. Store/UWP shortcuts) — fall back to the shortcut's own name
    if not stem:
        if name_stem in EMULATOR_EXACT or name_stem in EMULATOR_PREFIXES:
            return "emulation"
        if name_stem in APP_STEMS:
            return "apps"
    return "pc_games"


# ── Sub-categories inside PC Games / Emulation (the categories rail) ──────────
# Folder names that only say which TAB a shortcut belongs to — never a category
_TAB_FOLDER_WORDS = {
    "game", "games", "pc games", "pc game", "pcgames", "pc", "steam games",
    "emulation", "emulators", "emulator", "emu", "emus", "rom", "roms", "retro",
    "app", "apps", "applications", "application", "tools", "tool", "programs",
    "software", "utilities", "utility", "shortcuts",
}


def folder_group(rel_dir: str) -> str:
    """Category from the subfolder a shortcut lives in: the nearest folder whose
    name isn't just a tab name (Games\\RPG\\x.lnk → "RPG"). "" = none."""
    parts = [p for p in rel_dir.replace("/", "\\").split("\\") if p and p != "."]
    for part in reversed(parts):
        norm = re.sub(r"\s+", " ", part.strip().lower())
        if norm and norm not in _TAB_FOLDER_WORDS:
            return part.strip()
    return ""


# Emulator executable prefix → system it plays (checked longest prefix first)
EMULATOR_SYSTEMS = {
    "ryujinx": "Switch", "yuzu": "Switch", "suyu": "Switch", "sudachi": "Switch",
    "citron": "Switch", "torzu": "Switch", "eden": "Switch",
    "pcsx2": "PS2", "rpcs3": "PS3", "shadps4": "PS4", "duckstation": "PS1",
    "epsxe": "PS1", "pcsx": "PS1", "ppsspp": "PSP", "vita3k": "PS Vita",
    "dolphin": "GameCube / Wii", "cemu": "Wii U",
    "citra": "3DS", "lime3ds": "3DS", "azahar": "3DS",
    "melonds": "DS", "desmume": "DS",
    "mgba": "GBA", "visualboyadvance": "GBA",
    "snes9x": "SNES", "bsnes": "SNES", "zsnes": "SNES", "higan": "SNES",
    "mesen": "NES", "nestopia": "NES", "fceux": "NES",
    "project64": "N64", "simple64": "N64", "mupen64": "N64", "rmg": "N64",
    "gopher64": "N64",
    "xemu": "Xbox", "xenia": "Xbox 360", "xenos": "Xbox 360",
    "flycast": "Dreamcast", "redream": "Dreamcast", "nulldc": "Dreamcast",
    "kega": "Mega Drive", "fusion": "Mega Drive",
    "mame": "Arcade", "fbneo": "Arcade",
    "dosbox": "DOS", "scummvm": "ScummVM",
}
_EMU_SYS_PREFIXES = sorted(EMULATOR_SYSTEMS, key=len, reverse=True)
# ROM / disc-image extension → system (only extensions that name one system)
ROM_SYSTEMS = {
    ".sfc": "SNES", ".smc": "SNES", ".nes": "NES",
    ".z64": "N64", ".n64": "N64", ".v64": "N64",
    ".gba": "GBA", ".gbc": "Game Boy Color", ".gb": "Game Boy",
    ".nds": "DS", ".3ds": "3DS", ".cia": "3DS", ".cci": "3DS", ".cxi": "3DS",
    ".nsp": "Switch", ".xci": "Switch", ".nca": "Switch", ".nro": "Switch",
    ".wua": "Wii U", ".wux": "Wii U", ".rpx": "Wii U",
    ".rvz": "GameCube / Wii", ".wbfs": "GameCube / Wii", ".gcm": "GameCube / Wii",
    ".gcz": "GameCube / Wii", ".wia": "GameCube / Wii",
    ".md": "Mega Drive", ".gen": "Mega Drive", ".32x": "32X",
    ".sms": "Master System", ".gg": "Game Gear", ".pce": "PC Engine",
    ".ws": "WonderSwan", ".wsc": "WonderSwan", ".a26": "Atari 2600",
    ".lnx": "Lynx", ".ngp": "Neo Geo Pocket", ".vb": "Virtual Boy",
    ".cdi": "Dreamcast", ".gdi": "Dreamcast", ".xex": "Xbox 360",
    ".pbp": "PSP", ".cso": "PSP",
}
# Front-ends / multi-system emulators: the system comes from the ROM only
_MULTI_EMUS = ("retroarch", "ares", "mednafen", "bizhawk", "emuhawk", "es-de",
               "emulationstation", "retrobat", "launchbox", "bigbox", "pegasus-fe",
               "openemu")
# Color dot for each system in the rail (others get a neutral gray)
SYSTEM_COLOURS = {
    "Switch": (230, 60, 60), "PS1": (150, 150, 165), "PS2": (80, 110, 220),
    "PS3": (60, 90, 190), "PS4": (40, 110, 230), "PSP": (110, 110, 130),
    "PS Vita": (70, 130, 230), "GameCube / Wii": (140, 90, 200), "Wii U": (0, 160, 200),
    "3DS": (220, 50, 70), "DS": (180, 180, 190), "GBA": (120, 80, 200),
    "Game Boy": (150, 170, 90), "Game Boy Color": (200, 160, 60), "SNES": (170, 170, 185),
    "NES": (200, 60, 60), "N64": (60, 160, 90), "Xbox": (80, 170, 70),
    "Xbox 360": (110, 190, 60), "Dreamcast": (240, 140, 50), "Mega Drive": (60, 60, 70),
    "Arcade": (230, 190, 50), "Emulators": (90, 170, 220),
}


def detect_system(target: str = "", args: str = "") -> str:
    """Emulation system for a shortcut: ROM extension first, then the emulator.
    "Emulators" for a front-end started without a game; "" if unknown."""
    tl    = (target or "").lower().replace("\\", "/")
    stem  = os.path.splitext(tl.rsplit("/", 1)[-1])[0]
    t_ext = os.path.splitext(tl)[1]
    if t_ext in ROM_SYSTEMS:                      # shortcut points straight at a ROM
        return ROM_SYSTEMS[t_ext]
    rom_ext = ""
    m = _ROM_RE.search(args or "")
    if m:
        rom_ext = "." + m.group(1).lower()
        if rom_ext in ROM_SYSTEMS:
            return ROM_SYSTEMS[rom_ext]
    if not stem:
        return ""
    if stem.startswith(_MULTI_EMUS):
        return "" if rom_ext else "Emulators"
    for pre in _EMU_SYS_PREFIXES:
        if stem == pre or (len(pre) > 4 and stem.startswith(pre)) or stem.startswith(pre + "-") \
                or stem.startswith(pre + "_") or re.match(re.escape(pre) + r"\d", stem):
            return EMULATOR_SYSTEMS[pre]
    return ""


GROUP_ALL  = "\x00all"     # rail entry "All"
GROUP_NONE = ""            # rail entry "Uncategorized"


_PS_LNK_BATCH = r"""
$sh  = New-Object -ComObject WScript.Shell
$out = New-Object System.Collections.ArrayList
foreach($p in [System.IO.File]::ReadAllLines('IN_PH', [System.Text.Encoding]::UTF8)){
    if(-not $p){continue}
    try{
        $l = $sh.CreateShortcut($p)
        [void]$out.Add([pscustomobject]@{p=$p; t=$l.TargetPath; a=$l.Arguments})
    }catch{}
}
$json = ConvertTo-Json -InputObject @($out) -Compress
[System.IO.File]::WriteAllText('OUT_PH', $json, (New-Object System.Text.UTF8Encoding($false)))
"""


def _load_target_cache() -> dict:
    try:
        with open(TARGET_CACHE_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_target_cache(cache: dict) -> None:
    try:
        with open(TARGET_CACHE_FILE, "w", encoding="utf-8") as fh:
            json.dump(cache, fh)
    except OSError:
        pass


def _resolve_lnk_targets(paths: list) -> dict:
    """Return {lnk_path: (target, arguments)}.

    Uses an on-disk cache keyed by file mtime, and resolves only new/changed
    shortcuts — all of them in ONE PowerShell call instead of one per file.
    """
    cache   = _load_target_cache()
    result  = {}
    missing = {}
    for p in paths:
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        c = cache.get(p)
        if c and c.get("m") == m:
            result[p] = (c.get("t", ""), c.get("a", ""))
        else:
            missing[p] = m

    if missing and sys.platform == "win32":
        fd_in,  tmp_in  = tempfile.mkstemp(suffix=".txt", prefix="games_lnk_in_")
        fd_out, tmp_out = tempfile.mkstemp(suffix=".json", prefix="games_lnk_out_")
        os.close(fd_in)
        os.close(fd_out)
        try:
            with open(tmp_in, "w", encoding="utf-8") as fh:
                fh.write("\n".join(missing.keys()))
            script = _PS_LNK_BATCH.replace("IN_PH", tmp_in.replace("'", "''")) \
                                  .replace("OUT_PH", tmp_out.replace("'", "''"))
            try:
                _run_ps(script, timeout=min(120, 15 + len(missing) // 10))
            except (OSError, subprocess.TimeoutExpired):
                pass
            try:
                with open(tmp_out, encoding="utf-8-sig") as fh:
                    raw = fh.read().strip()
                items = json.loads(raw) if raw else []
                if isinstance(items, dict):
                    items = [items]
            except (OSError, json.JSONDecodeError):
                items = []
            for it in items:
                p = it.get("p")
                if p in missing:
                    t = it.get("t") or ""
                    a = it.get("a") or ""
                    result[p] = (t, a)
                    cache[p]  = {"m": missing[p], "t": t, "a": a}
        finally:
            for f in (tmp_in, tmp_out):
                try:
                    os.remove(f)
                except OSError:
                    pass

    # Keep the cache limited to shortcuts that still exist in this scan
    _save_target_cache({p: cache[p] for p in paths if p in cache})
    return result


def _read_url_target(url_path: str) -> str:
    try:
        with open(url_path, "r", encoding="UTF-8", errors="ignore") as fh:
            for line in fh:
                if line.strip().lower().startswith("url="):
                    return line.strip().split("=", 1)[1].strip()
    except OSError:
        pass
    return ""


# ── STEAMGRIDDB ───────────────────────────────────────────────────────────────
SGDB_API_BASE  = "https://www.steamgriddb.com/api/v2"
SGDB_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".games_browser_sgdb")
os.makedirs(SGDB_CACHE_DIR, exist_ok=True)
SGDB_EXTS = {".lnk", ".exe", ".url"}
_sgdb_api_key: str = ""   # set by App._load_config / _save_config


def _sgdb_headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }


_SGDB_LOG = os.path.join(os.path.expanduser("~"), "games_browser_sgdb_debug.txt")

def _sgdb_log(msg: str) -> None:
    try:
        with open(_SGDB_LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
    except Exception:
        pass

def _sgdb_search_game_id(name: str, api_key: str):
    """Search SteamGridDB for a game by name, return best-match game ID or None."""
    try:
        url = f"{SGDB_API_BASE}/search/autocomplete/{urllib.parse.quote(name)}"
        _sgdb_log(f"SEARCH url={url} key={api_key[:6]}...")
        req = urllib.request.Request(url, headers=_sgdb_headers(api_key))
        with urllib.request.urlopen(req, timeout=8, context=_SSL_CTX) as resp:
            data = json.loads(resp.read())
        _sgdb_log(f"SEARCH result success={data.get('success')} count={len(data.get('data',[]))}")
        if data.get("success") and data.get("data"):
            return data["data"][0]["id"]
    except Exception as e:  # noqa: BLE001
        _sgdb_log(f"SEARCH error: {type(e).__name__}: {e}")
    return None


def _sgdb_fetch_grid_url(game_id: int, api_key: str):
    """Return URL of the best portrait grid (600x900) for a game ID."""
    try:
        url = f"{SGDB_API_BASE}/grids/game/{game_id}?dimensions=600x900&limit=20"
        req = urllib.request.Request(url, headers=_sgdb_headers(api_key))
        with urllib.request.urlopen(req, timeout=8, context=_SSL_CTX) as resp:
            data = json.loads(resp.read())
        if data.get("success") and data.get("data"):
            for item in data["data"]:
                if not item.get("is_nsfw") and not item.get("is_humor"):
                    return item["url"]
            return data["data"][0]["url"]
    except Exception:  # noqa: BLE001
        pass
    return None


def _sgdb_fetch_grid_list(game_name: str, api_key: str, limit: int = 24):
    """Return a list of portrait grid URLs for a game name (for the picker).

    Returns [] on any failure. Filters NSFW/humor. Includes both the full-size
    'url' and a 'thumb' for quick preview loading.
    """
    try:
        game_id = _sgdb_search_game_id(game_name, api_key)
        if not game_id:
            return []
        url = f"{SGDB_API_BASE}/grids/game/{game_id}?dimensions=600x900&limit={limit}"
        req = urllib.request.Request(url, headers=_sgdb_headers(api_key))
        with urllib.request.urlopen(req, timeout=8, context=_SSL_CTX) as resp:
            data = json.loads(resp.read())
        out = []
        if data.get("success") and data.get("data"):
            for item in data["data"]:
                if item.get("is_nsfw") or item.get("is_humor"):
                    continue
                full  = item.get("url")
                thumb = item.get("thumb") or full
                if full:
                    out.append({"url": full, "thumb": thumb})
        _sgdb_log(f"GRID LIST game={game_name!r} count={len(out)}")
        return out
    except Exception as e:  # noqa: BLE001
        _sgdb_log(f"GRID LIST error: {type(e).__name__}: {e}")
        return []


def _sgdb_cache_paths(game_name: str):
    """Return (cache_png_path, miss_path) for a game name."""
    safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in game_name).strip()
    return (os.path.join(SGDB_CACHE_DIR, f"{safe}.png"),
            os.path.join(SGDB_CACHE_DIR, f"{safe}.miss"))


def _sgdb_download_url_bytes(url: str, timeout: int = 15):
    """Download raw bytes from an SGDB CDN URL (no auth header). None on error."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        })
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            return resp.read()
    except Exception as e:  # noqa: BLE001
        _sgdb_log(f"URL bytes error: {type(e).__name__}: {e}")
        return None


def _sgdb_set_cover(game_name: str, url: str):
    """Download `url` and overwrite the cached cover for `game_name`.

    Returns the cache path on success, else None. Clears any .miss marker.
    """
    cache_path, miss_path = _sgdb_cache_paths(game_name)
    data = _sgdb_download_url_bytes(url)
    if not data:
        return None
    try:
        with open(cache_path, "wb") as f:
            f.write(data)
        if os.path.exists(miss_path):
            os.remove(miss_path)
        if os.path.getsize(cache_path) > 0:
            _sgdb_log(f"SET COVER ok game={game_name!r} -> {cache_path}")
            return cache_path
    except OSError as e:
        _sgdb_log(f"SET COVER error: {e}")
    return None


def _sgdb_download_art(game_name: str, api_key: str):
    """Search → grid URL → download to cache. Returns local PNG path or None."""
    safe       = "".join(c if c.isalnum() or c in "-_ " else "_" for c in game_name).strip()
    cache_path = os.path.join(SGDB_CACHE_DIR, f"{safe}.png")
    miss_path  = os.path.join(SGDB_CACHE_DIR, f"{safe}.miss")
    _sgdb_log(f"ART game={game_name!r} safe={safe!r} cache_exists={os.path.exists(cache_path)} miss_exists={os.path.exists(miss_path)} key_len={len(api_key)}")

    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
        _sgdb_log(f"ART cache hit: {cache_path}")
        return cache_path
    if os.path.exists(miss_path):
        _sgdb_log(f"ART miss file exists, skipping")
        return None

    game_id = _sgdb_search_game_id(game_name, api_key)
    if not game_id:
        open(miss_path, "w").close()
        return None

    grid_url = _sgdb_fetch_grid_url(game_id, api_key)
    if not grid_url:
        open(miss_path, "w").close()
        return None

    try:
        # CDN URL — no auth header needed, Bearer token causes 401
        req = urllib.request.Request(grid_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        })
        with urllib.request.urlopen(req, timeout=15, context=_SSL_CTX) as resp:
            data = resp.read()
        if data:
            with open(cache_path, "wb") as f:
                f.write(data)
        if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
            _sgdb_log(f"ART downloaded OK: {cache_path} ({os.path.getsize(cache_path)} bytes)")
            return cache_path
    except Exception as e:  # noqa: BLE001
        _sgdb_log(f"ART download error: {e}")

    open(miss_path, "w").close()
    return None


def _render_sgdb_card(art_path: str, target_w: int, target_h: int):
    """Return a pygame.Surface of (target_w, target_h) filled with SGDB art."""
    from PIL import Image as PilImage  # type: ignore[import]
    img   = PilImage.open(art_path).convert("RGBA")
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)
    img   = img.resize((new_w, new_h), getattr(PilImage, "Resampling", PilImage).LANCZOS)
    left  = (new_w - target_w) // 2
    top   = (new_h - target_h) // 2
    img   = img.crop((left, top, left + target_w, top + target_h))
    return pygame.image.fromstring(img.tobytes(), img.size, "RGBA")




def file_color(name, is_dir):
    if is_dir:
        return FILE_COLORS["folder"]
    return FILE_COLORS.get(os.path.splitext(name)[1].lower(), FILE_COLORS["default"])


def file_badge(name, is_dir):
    if is_dir:
        return "DIR"
    ext = os.path.splitext(name)[1].upper().lstrip(".")
    return ext[:4] if ext else "FILE"


def fit_text(font, text, max_w):
    """Return text shortened with '…' so it renders no wider than max_w px."""
    if font.size(text)[0] <= max_w:
        return text
    while text and font.size(text + "…")[0] > max_w:
        text = text[:-1]
    return text.rstrip() + "…"


def draw_rounded_rect(surf, color, rect, radius=10, alpha=255):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=radius)
    surf.blit(s, rect.topleft)


def draw_triangle_left(surf, cx, cy, size, color):
    h = size // 2
    pts = [(cx + h // 2, cy - h), (cx + h // 2, cy + h), (cx - h // 2, cy)]
    pygame.draw.polygon(surf, color, pts)


def draw_triangle_right(surf, cx, cy, size, color):
    h = size // 2
    pts = [(cx - h // 2, cy - h), (cx - h // 2, cy + h), (cx + h // 2, cy)]
    pygame.draw.polygon(surf, color, pts)


_badge_fonts: dict = {}


def _get_badge_font(size):
    if size not in _badge_fonts:
        _badge_fonts[size] = pygame.font.SysFont("Consolas", max(9, size // 10))
    return _badge_fonts[size]


_icon_cache:   dict = {}
_icon_pending: set  = set()
_icon_executor      = ThreadPoolExecutor(max_workers=6)

_PS_JUMBO = r"""
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class JumboIcon {
    [DllImport("shell32.dll",CharSet=CharSet.Unicode)]
    public static extern IntPtr SHGetFileInfo(string p,uint a,ref SFI s,uint b,uint f);
    [DllImport("shell32.dll",EntryPoint="#727")]
    public static extern int SHGetImageList(int i,ref Guid g,out IImageList l);
    [ComImport,Guid("46EB5926-582E-4017-9FDF-E8998DAA0950"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IImageList {
        [PreserveSig] int Add(IntPtr a,IntPtr b,ref int c);
        [PreserveSig] int ReplaceIcon(int a,IntPtr b,ref int c);
        [PreserveSig] int SetOverlayImage(int a,int b);
        [PreserveSig] int Replace(int a,IntPtr b,IntPtr c);
        [PreserveSig] int AddMasked(IntPtr a,int b,ref int c);
        [PreserveSig] int Draw(ref int p);
        [PreserveSig] int Remove(int i);
        [PreserveSig] int GetIcon(int i,int f,ref IntPtr ico);
    }
    [StructLayout(LayoutKind.Sequential,CharSet=CharSet.Unicode)]
    public struct SFI {
        public IntPtr hIcon; public int iIcon; public uint dwAttr;
        [MarshalAs(UnmanagedType.ByValTStr,SizeConst=260)] public string name;
        [MarshalAs(UnmanagedType.ByValTStr,SizeConst=80)]  public string type;
    }
    public static System.Drawing.Bitmap Get(string path) {
        var s=new SFI();
        SHGetFileInfo(path,0,ref s,(uint)System.Runtime.InteropServices.Marshal.SizeOf(s),0x4000);
        var g=new Guid("46EB5926-582E-4017-9FDF-E8998DAA0950");
        IImageList l; SHGetImageList(0,ref g,out l);
        IntPtr h=IntPtr.Zero; l.GetIcon(s.iIcon,1,ref h);
        if(h==IntPtr.Zero) return null;
        return Icon.FromHandle(h).ToBitmap();
    }
}
"@
$bmp=[JumboIcon]::Get('SRC_PH')
if($bmp){
    $d=New-Object System.Drawing.Bitmap(256,256)
    $g=[System.Drawing.Graphics]::FromImage($d)
    $g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.DrawImage($bmp,0,0,256,256);$g.Dispose()
    $d.Save('OUT_PH',[System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose();$d.Dispose()
}else{
    $i=[System.Drawing.Icon]::ExtractAssociatedIcon('SRC_PH')
    if($i){$b=$i.ToBitmap();$b.Save('OUT_PH',[System.Drawing.Imaging.ImageFormat]::Png);$b.Dispose();$i.Dispose()}
}
"""

_PS_ICO = r"""
Add-Type -AssemblyName System.Drawing
$bmp=$null
foreach($sz in @(256,128,64,48,32)){
    try{$bmp=(New-Object System.Drawing.Icon('SRC_PH',$sz,$sz)).ToBitmap();break}catch{}
}
if(-not $bmp){$ico=New-Object System.Drawing.Icon('SRC_PH');$bmp=$ico.ToBitmap();$ico.Dispose()}
$d=New-Object System.Drawing.Bitmap(256,256)
$g=[System.Drawing.Graphics]::FromImage($d)
$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.DrawImage($bmp,0,0,256,256);$g.Dispose()
$d.Save('OUT_PH',[System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose();$d.Dispose()
"""


def _run_ps(script: str, timeout: int = 12) -> None:
    subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, timeout=timeout,
        creationflags=CREATE_NO_WINDOW,
    )


def _read_url_icon(url_path: str):
    try:
        with open(url_path, "r", encoding="UTF-8", errors="ignore") as fh:
            for line in fh:
                if line.strip().lower().startswith("iconfile="):
                    p = line.strip().split("=", 1)[1].strip()
                    if os.path.exists(p):
                        return p
    except OSError:
        pass
    return None


def _name_score(stem: str, filename: str) -> int:
    stem_words = set(stem.lower().split())
    file_words = set(os.path.splitext(filename)[0].lower().split())
    return len(stem_words & file_words)


def _resolve_lnk(full_path: str, name: str) -> str:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command",
             f"$lnk=(New-Object -ComObject WScript.Shell).CreateShortcut('{full_path.replace(chr(39), chr(39)*2)}')\n"
             f"Write-Output \"ICO:$(($lnk.IconLocation -split ',')[0])\"\n"
             f"Write-Output \"TGT:$($lnk.TargetPath)\""],
            capture_output=True, text=True, timeout=4,
            creationflags=CREATE_NO_WINDOW,
        )
        ico_val = ""
        tgt_val = ""
        for line in result.stdout.strip().splitlines():
            if line.startswith("ICO:"):
                ico_val = line[4:].strip()
            elif line.startswith("TGT:"):
                tgt_val = line[4:].strip()
    except (OSError, subprocess.TimeoutExpired):
        return full_path

    if ico_val and os.path.exists(ico_val):
        return ico_val

    if tgt_val and "eden" in tgt_val.lower():
        game_stem    = os.path.splitext(name)[0]
        eden_appdata = os.path.join(os.environ.get("APPDATA", ""), "eden")
        eden_exe_dir = os.path.dirname(tgt_val)
        cache_dirs   = [
            os.path.join(eden_appdata, "cache", "game_list"),
            os.path.join(eden_exe_dir, "user", "cache", "game_list"),
            os.path.join(eden_appdata, "cache"),
        ]
        best_path  = None
        best_score = -1
        for cache_dir in cache_dirs:
            if not os.path.isdir(cache_dir):
                continue
            for filename in os.listdir(cache_dir):
                if not filename.lower().endswith(".png"):
                    continue
                score = _name_score(game_stem, filename)
                if score > best_score:
                    best_score = score
                    best_path  = os.path.join(cache_dir, filename)
        if best_path and best_score > 0:
            return best_path

    if tgt_val and os.path.exists(tgt_val):
        return tgt_val

    return full_path


def _load_png_as_surface(png_path: str, target_size: int):
    try:
        from PIL import Image as PilImage  # type: ignore[import]
        img = PilImage.open(png_path).convert("RGBA")
        img = img.resize((target_size, target_size), getattr(PilImage, "Resampling", PilImage).LANCZOS)
        return pygame.image.fromstring(img.tobytes(), img.size, "RGBA")
    except ImportError:
        surf = pygame.image.load(png_path).convert_alpha()
        return pygame.transform.smoothscale(surf, (target_size, target_size))



def _make_placeholder_card(game_name: str, target_w: int, target_h: int,
                            color: tuple) -> 'pygame.Surface':
    """
    Styled Steam Deck-style placeholder card for games with no SGDB art.
    Dark gradient background + centred game name text.
    """
    surf = pygame.Surface((target_w, target_h), pygame.SRCALPHA)

    # Background — dark gradient from color to near-black
    r, g, b = color
    for row in range(target_h):
        t      = row / target_h                     # 0 → 1 top to bottom
        factor = 0.55 - t * 0.40                    # brighter at top
        pygame.draw.line(surf, (int(r * factor), int(g * factor), int(b * factor)),
                         (0, row), (target_w, row))

    # Subtle inner border
    pygame.draw.rect(surf, (*color, 60), (0, 0, target_w, target_h), width=2, border_radius=6)

    # Game name — word-wrap into the card
    words   = game_name.replace("_", " ").replace("-", " ").split()
    lines   = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if len(test) <= 16:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    lines = lines[:4]   # max 4 lines
    if not lines:
        return surf

    # Choose font size that fits
    fsize = max(11, min(22, target_w // max(len(line) for line in lines) + 2))
    try:
        font = pygame.font.SysFont("Segoe UI", fsize, bold=True)
    except Exception:  # noqa: BLE001
        font = pygame.font.SysFont(None, fsize + 4, bold=True)

    total_h = len(lines) * (fsize + 4)
    start_y = (target_h - total_h) // 2
    for i, line in enumerate(lines):
        txt = font.render(line, True, (230, 235, 245))
        # subtle shadow
        shad = font.render(line, True, (0, 0, 0))
        x = (target_w - txt.get_width()) // 2
        y = start_y + i * (fsize + 4)
        surf.blit(shad, (x + 1, y + 1))
        surf.blit(txt,  (x,     y))

    return surf


def _make_icon_card(icon: 'pygame.Surface', target_w: int, target_h: int,
                    color: tuple) -> 'pygame.Surface':
    """Portrait card with the real program icon centred (used for apps and
    for shortcuts when no SteamGridDB key is set) — avoids stretching a
    square icon into a portrait card."""
    surf = _make_placeholder_card("", target_w, target_h, color)
    isz  = int(target_w * 0.62)
    ic   = pygame.transform.smoothscale(icon, (isz, isz))
    surf.blit(ic, ((target_w - isz) // 2, (target_h - isz) // 2))
    return surf


def _extract_icon_background(full_path: str, name: str,
                              target_size: int, is_dir: bool = False,
                              sgdb_key: str = "", allow_search: bool = True) -> None:
    safe    = "".join(c if c.isalnum() else "_" for c in full_path)[-80:]
    tmp_png = os.path.join(tempfile.gettempdir(), f"games_ico_{safe}.png")
    card_w    = target_size
    card_h    = int(target_size * 1.5)
    game_name = os.path.splitext(name)[0]
    color     = file_color(name, False)

    try:
        ext = os.path.splitext(name)[1].lower()

        # ── SteamGridDB art ───────────────────────────────────────────────────
        # Games/emulation: search SGDB automatically.
        # Apps: only use a cover the user picked manually (Y), else real icon.
        if sgdb_key and not is_dir and ext in SGDB_EXTS:
            _sgdb_log(f"EXTRACT triggered for {name!r} ext={ext!r} search={allow_search}")
            try:
                if allow_search:
                    art_path = _sgdb_download_art(game_name, sgdb_key)
                else:
                    cache_path, _ = _sgdb_cache_paths(game_name)
                    art_path = cache_path if (os.path.exists(cache_path)
                                              and os.path.getsize(cache_path) > 0) else None
                if art_path:
                    _icon_cache[full_path] = _render_sgdb_card(art_path, card_w, card_h)
                    return
                if allow_search:
                    # No art found — show styled placeholder with game name
                    _icon_cache[full_path] = _make_placeholder_card(game_name, card_w, card_h, color)
                    return
            except Exception:  # noqa: BLE001
                if allow_search:
                    # Network/PIL error — still show placeholder so card looks intentional
                    _icon_cache[full_path] = _make_placeholder_card(game_name, card_w, card_h, color)
                    return

        # ── Real program icon ─────────────────────────────────────────────────
        if ext == ".url":
            icon_src = _read_url_icon(full_path) or full_path
        elif ext == ".lnk":
            icon_src = _resolve_lnk(full_path, name)
        else:
            icon_src = full_path

        if not os.path.exists(tmp_png):
            src_ext = os.path.splitext(icon_src)[1].lower()

            if src_ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
                try:
                    from PIL import Image as PilImage  # type: ignore[import]
                    img = PilImage.open(icon_src).convert("RGBA")
                    img = img.resize((256, 256), getattr(PilImage, "Resampling", PilImage).LANCZOS)
                    img.save(tmp_png)
                except ImportError:
                    _icon_cache[full_path] = None
                    return
            elif src_ext == ".ico":
                script = _PS_ICO.replace("SRC_PH", icon_src.replace("'", "''")) \
                                 .replace("OUT_PH", tmp_png.replace("'", "''"))
                _run_ps(script, timeout=10)
            else:
                script = _PS_JUMBO.replace("SRC_PH", icon_src.replace("'", "''")) \
                                   .replace("OUT_PH", tmp_png.replace("'", "''"))
                _run_ps(script, timeout=12)

        if os.path.exists(tmp_png) and os.path.getsize(tmp_png) > 0:
            icon = _load_png_as_surface(tmp_png, target_size)
            _icon_cache[full_path] = _make_icon_card(icon, card_w, card_h, color)
        else:
            _icon_cache[full_path] = _make_placeholder_card(game_name, card_w, card_h, color)

    except Exception:  # noqa: BLE001
        _icon_cache[full_path] = None
    finally:
        _icon_pending.discard(full_path)


def get_file_icon(full_path: str, name: str, size: int, allow_search: bool = True):
    if full_path in _icon_cache:
        return _icon_cache[full_path]
    if sys.platform != "win32":
        return None
    ext = os.path.splitext(name)[1].lower()
    if ext in LAUNCH_EXTS and full_path not in _icon_pending:
        _icon_pending.add(full_path)
        _sgdb_log(f"SUBMIT {name!r} ext={ext!r} sgdb_key_len={len(_sgdb_api_key)} search={allow_search}")
        _icon_executor.submit(_extract_icon_background, full_path, name, size, False,
                              _sgdb_api_key, allow_search)
    return None


def draw_icon(surf, x, y, w, h, color, label, selected=False, icon_surf=None):
    pad    = 3
    rect   = pygame.Rect(x + pad, y + pad, w - pad * 2, h - pad * 2)
    radius = 8
    if selected:
        glow = pygame.Surface((w + 12, h + 12), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*C_ACCENT, 80), (0, 0, w + 12, h + 12), border_radius=radius + 5)
        surf.blit(glow, (x - 6, y - 6))
        pygame.draw.rect(surf, C_ACCENT, rect.inflate(4, 4), width=3, border_radius=radius + 2)
    pygame.draw.rect(surf, C_CARD_HOV if selected else C_CARD, rect, border_radius=radius)
    if not selected:
        pygame.draw.rect(surf, C_GRAY, rect, width=1, border_radius=radius)
    cx = x + w // 2
    cy = y + h // 2
    if icon_surf is not None:
        # Scale to fill the card exactly, then clip to rounded rect
        scaled = pygame.transform.smoothscale(icon_surf, (w - pad * 2, h - pad * 2))
        # Blit onto a rounded mask so art doesn't overflow card corners
        mask = pygame.Surface((w - pad * 2, h - pad * 2), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w - pad * 2, h - pad * 2), border_radius=radius)
        scaled.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(scaled, (x + pad, y + pad))
    else:
        isz   = w // 3
        brect = pygame.Rect(cx - isz // 2, cy - isz // 2, isz, isz)
        pygame.draw.rect(surf, color, brect, border_radius=6)
        font = _get_badge_font(w)
        txt  = font.render(label[:3], True, C_WHITE)
        surf.blit(txt, txt.get_rect(center=(cx, cy)))


# Face-button colors (flat, close to the real Xbox pad) and letter colors
BTN_FACE = {
    "A": (( 76, 175,  80), C_WHITE),
    "B": ((229,  57,  53), C_WHITE),
    "X": (( 30, 136, 229), C_WHITE),
    "Y": ((251, 192,  45), ( 28,  30,  36)),   # dark letter keeps yellow readable
}
BTN_KEYCAP_BG     = (44, 49, 62)
BTN_KEYCAP_BORDER = (78, 86, 104)


BUTTON_STYLES = ["Xbox", "PlayStation", "Nintendo"]
_button_style = "Xbox"   # set from config by App


def set_button_style(style: str) -> None:
    global _button_style
    _button_style = style if style in BUTTON_STYLES else "Xbox"


# Logical buttons are always the Xbox/XInput ones the app receives
# (A=bottom, B=right, X=left, Y=top). Each style only changes how they LOOK.
_PS_SHAPES = {   # logical button -> (shape, colour)
    "A": ("cross",    (124, 178, 232)),
    "B": ("circle",   (236,  96,  96)),
    "X": ("square",   (226, 140, 196)),
    "Y": ("triangle", ( 64, 200, 160)),
}
_CAP_TEXT = {
    "Xbox":        {"LB": "LB", "RB": "RB", "VIEW": "VIEW",   "START": "START",   "RS": "RS", "RT": "RT", "LS": "LS", "LT": "LT"},
    "PlayStation": {"LB": "L1", "RB": "R1", "VIEW": "CREATE", "START": "OPTIONS", "RS": "R3", "RT": "R2", "LS": "L3", "LT": "L2"},
    "Nintendo":    {"LB": "L",  "RB": "R",  "VIEW": "\u2212",  "START": "+",       "RS": "RS", "RT": "ZR", "LS": "LS", "LT": "ZL"},
}
# Nintendo letters by position: bottom=B, right=A, left=Y, top=X
_NINTENDO_LETTER = {"A": "B", "B": "A", "X": "Y", "Y": "X"}
_BTN_WORDS = {
    "Xbox":        {"A": "A", "B": "B", "X": "X", "Y": "Y"},
    "PlayStation": {"A": "Cross", "B": "Circle", "X": "Square", "Y": "Triangle"},
    "Nintendo":    _NINTENDO_LETTER,
}


def btn_text(btn: str) -> str:
    """Name of a logical button in the current style, for use inside sentences."""
    if _input_mode == "kbd":
        return KEY_NAMES.get(btn, btn)
    return pad_btn_text(btn)


def pad_btn_text(btn: str) -> str:
    """Controller name of a button in the current style (never a keyboard key)."""
    if btn in ("A", "B", "X", "Y"):
        return _BTN_WORDS[_button_style][btn]
    word = _CAP_TEXT[_button_style].get(btn, btn)
    return {"\u2212": "Minus", "+": "Plus"}.get(word, word.title() if len(word) > 3 else word)


# Keyboard mode: which key does each logical button's job
_input_mode = "pad"          # "pad" or "kbd" — set by App from the last input used
KEY_NAMES = {"A": "Enter", "B": "Backspace", "X": "X", "Y": "Y",
             "LB": "Shift+Tab", "RB": "Tab", "VIEW": "F2", "START": "Esc", "RS": "S",
             "LT": "PgUp", "RT": "PgDn", "MANAGE": "Del"}


def set_input_mode(mode: str) -> None:
    global _input_mode
    _input_mode = "kbd" if mode == "kbd" else "pad"


def _glyph(btn):
    """('face', letter, fill, ink) | ('ps', shape, color) | ('cap', text)"""
    if _input_mode == "kbd":
        return ("cap", KEY_NAMES.get(btn, btn))
    st = _button_style
    if btn in ("A", "B", "X", "Y"):
        if st == "PlayStation":
            shape, col = _PS_SHAPES[btn]
            return ("ps", shape, col)
        if st == "Nintendo":
            return ("face", _NINTENDO_LETTER[btn], (58, 63, 76), C_WHITE)
        fill, ink = BTN_FACE[btn]
        return ("face", btn, fill, ink)
    text = _CAP_TEXT[st].get(btn, btn)
    if st == "Nintendo" and text in ("\u2212", "+"):
        return ("face", text, (58, 63, 76), C_WHITE)
    return ("cap", text)


def _btn_size(font, btn):
    """(width, height) of a button glyph."""
    h = _s(24)
    g = _glyph(btn)
    if g[0] in ("face", "ps"):
        return h, h                                  # perfect circle
    return font.size(g[1])[0] + _s(18), h            # keycap pill (START, LB, RB…)


def _draw_ps_symbol(surf, shape, col, c, r):
    lw = max(2, _s(1.6))
    k  = r * 0.46
    cx, cy = c
    if shape == "cross":
        pygame.draw.line(surf, col, (cx - k, cy - k), (cx + k, cy + k), lw + 1)
        pygame.draw.line(surf, col, (cx - k, cy + k), (cx + k, cy - k), lw + 1)
    elif shape == "circle":
        pygame.draw.circle(surf, col, c, int(r * 0.52), lw)
    elif shape == "square":
        sq = pygame.Rect(0, 0, int(r * 0.98), int(r * 0.98))
        sq.center = c
        pygame.draw.rect(surf, col, sq, lw)
    elif shape == "triangle":
        t = r * 0.58
        pts = [(cx, cy - t), (cx + t * 0.95, cy + t * 0.62), (cx - t * 0.95, cy + t * 0.62)]
        pygame.draw.polygon(surf, col, pts, lw)


def draw_button(surf, font, btn, x, cy):
    """Draw one controller button glyph (in the chosen style) with its left edge
    at x, centred on cy. Returns its width."""
    w, h = _btn_size(font, btn)
    rect = pygame.Rect(x, cy - h // 2, w, h)
    g    = _glyph(btn)
    if g[0] == "ps":
        pygame.draw.circle(surf, BTN_KEYCAP_BG, rect.center, h // 2)
        pygame.draw.circle(surf, BTN_KEYCAP_BORDER, rect.center, h // 2, 1)
        _draw_ps_symbol(surf, g[1], g[2], rect.center, h // 2)
        return w
    if g[0] == "face":
        _, text, fill, ink = g
        pygame.draw.circle(surf, fill, rect.center, h // 2)
        if fill == (58, 63, 76):                     # Nintendo: subtle rim
            pygame.draw.circle(surf, BTN_KEYCAP_BORDER, rect.center, h // 2, 1)
    else:
        _, text = g
        ink = C_TEXT
        pygame.draw.rect(surf, BTN_KEYCAP_BG, rect, border_radius=_s(7))
        pygame.draw.rect(surf, BTN_KEYCAP_BORDER, rect, width=1, border_radius=_s(7))
    if text in ("\u2212", "+"):                      # draw −/+ as shapes (font-proof)
        cx, cyy = rect.center
        k, lw = h * 0.26, max(2, _s(1.6))
        pygame.draw.line(surf, ink, (cx - k, cyy), (cx + k, cyy), lw)
        if text == "+":
            pygame.draw.line(surf, ink, (cx, cyy - k), (cx, cyy + k), lw)
        return w
    bt = font.render(text, True, ink)
    surf.blit(bt, bt.get_rect(center=(rect.centerx, rect.centery)))
    return w


def draw_keycap(surf, font, text, x, cy, arrow=None):
    """A keyboard keycap (text or an arrow) with its left edge at x. Returns width."""
    h = _s(24)
    w = h if arrow else max(h, font.size(text)[0] + _s(18))
    r = pygame.Rect(x, cy - h // 2, w, h)
    pygame.draw.rect(surf, BTN_KEYCAP_BG, r, border_radius=_s(7))
    pygame.draw.rect(surf, BTN_KEYCAP_BORDER, r, width=1, border_radius=_s(7))
    if arrow:
        c, k = r.center, h * 0.22
        pts = {"up":    [(c[0], c[1] - k), (c[0] + k, c[1] + k * 0.6), (c[0] - k, c[1] + k * 0.6)],
               "down":  [(c[0], c[1] + k), (c[0] + k, c[1] - k * 0.6), (c[0] - k, c[1] - k * 0.6)],
               "left":  [(c[0] - k, c[1]), (c[0] + k * 0.6, c[1] - k), (c[0] + k * 0.6, c[1] + k)],
               "right": [(c[0] + k, c[1]), (c[0] - k * 0.6, c[1] - k), (c[0] - k * 0.6, c[1] + k)]}[arrow]
        pygame.draw.polygon(surf, C_TEXT, pts)
    else:
        t = font.render(text, True, C_TEXT)
        surf.blit(t, t.get_rect(center=r.center))
    return w


_HINT_GAP_IN  = 6    # between button and its label (unscaled)
_HINT_GAP_OUT = 20   # between one hint and the next
_HINT_GAP_BTN = 5    # between two buttons that share one label (LB RB)


def hints_width(font, hints):
    """Total width draw_hints() will use — for centring/right-aligning."""
    w = 0
    for i, (btn, label) in enumerate(hints):
        w += _btn_size(font, btn)[0]
        if label:
            w += _s(_HINT_GAP_IN) + font.size(label)[0]
            if i < len(hints) - 1:
                w += _s(_HINT_GAP_OUT)
        elif i < len(hints) - 1:
            w += _s(_HINT_GAP_BTN)
    return w


def draw_hints(surf, font, hints, x, y):
    """Draw [(button, label), …] left to right, vertically centred on y.
    An empty label groups the button with the next one (e.g. LB RB Switch Tab)."""
    bx = x
    for btn, label in hints:
        bx += draw_button(surf, font, btn, bx, y)
        if label:
            bx += _s(_HINT_GAP_IN)
            lt = font.render(label, True, C_TEXT_DIM)
            surf.blit(lt, (bx, y - lt.get_height() // 2))
            bx += lt.get_width() + _s(_HINT_GAP_OUT)
        else:
            bx += _s(_HINT_GAP_BTN)


# ── WINDOW RESTORE (bring the app back after a game closes) ───────────────────
# Foreground window classes that mean "nothing is running, only the desktop"
_IDLE_WINDOW_CLASSES = {"Progman", "WorkerW", "Shell_TrayWnd",
                        "Shell_SecondaryTrayWnd", ""}

# Store / launcher programs that pop up when a game closes
LAUNCHER_EXES = {
    "eadesktop.exe", "ealauncher.exe", "origin.exe",                 # EA app / Origin
    "steam.exe", "steamwebhelper.exe",                               # Steam
    "epicgameslauncher.exe",                                         # Epic
    "upc.exe", "ubisoftconnect.exe", "uplaywebcore.exe",             # Ubisoft Connect
    "galaxyclient.exe",                                              # GOG Galaxy
    "battle.net.exe",                                                # Battle.net
    "amazon games ui.exe",                                           # Amazon Games
    "xboxpcapp.exe",                                                 # Xbox app
    "rockstarservice.exe", "socialclubhelper.exe",                   # Rockstar
    # helper programs launchers run games through / show windows from
    "ubisoftgamelauncher.exe", "ubisoftgamelauncher64.exe", "uplay.exe",
    "epicwebhelper.exe", "galaxyclient helper.exe", "gogalaxynotifications.exe",
    "eabackgroundservice.exe", "link2ea.exe", "battle.net helper.exe",
}

# Overlays / tools that open windows on top of games — never "the game"
OVERLAY_EXES = {
    "gameoverlayui.exe", "gameoverlayui64.exe",                      # Steam overlay
    "gamebar.exe", "gamebarftserver.exe", "gamebarpresencewriter.exe",  # Xbox Game Bar
    "nvidia overlay.exe", "nvidia share.exe", "nvcontainer.exe",     # NVIDIA
    "radeonsoftware.exe", "amdrsserv.exe", "amdow.exe",              # AMD
    "rtss.exe", "msiafterburner.exe", "overwolf.exe", "medal.exe",
    "playnite.fullscreenapp.exe", "joyxoff.exe",
}


HWND_TOPMOST, HWND_NOTOPMOST = -1, -2

def win_set_pos(hwnd, after, x, y, cx, cy, flags) -> None:
    """SetWindowPos with proper 64-bit argument types (HWND_TOPMOST = -1 must be
    passed as a pointer-sized value, or Windows silently ignores it)."""
    import ctypes
    from ctypes import wintypes
    f = ctypes.windll.user32.SetWindowPos
    f.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                  ctypes.c_int, ctypes.c_int, ctypes.c_uint]
    f.restype = wintypes.BOOL
    f(hwnd, after, x, y, cx, cy, flags)


def cursor_pos():
    import ctypes
    from ctypes import wintypes
    pt = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def set_cursor_pos(x, y) -> None:
    import ctypes
    ctypes.windll.user32.SetCursorPos(int(x), int(y))


def cursor_hidden() -> bool:
    """True if Windows isn't drawing the mouse pointer. Right after boot (no mouse
    moved yet) or after touch input Windows "suppresses" the pointer, and moving it
    with SetCursorPos doesn't bring it back — only real mouse input does."""
    import ctypes
    from ctypes import wintypes

    class CURSORINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("flags", wintypes.DWORD),
                    ("hCursor", wintypes.HANDLE), ("ptScreenPos", wintypes.POINT)]
    ci = CURSORINFO()
    ci.cbSize = ctypes.sizeof(CURSORINFO)
    if not ctypes.windll.user32.GetCursorInfo(ctypes.byref(ci)):
        return False
    return not (ci.flags & 0x1)          # CURSOR_SHOWING missing (0x2 = suppressed)


def wake_cursor() -> None:
    """Make Windows show the pointer: a tiny injected mouse move counts as real
    mouse input (the pointer ends up where it was)."""
    _send_inputs([("mouse", 1, 0, 0x0001), ("mouse", -1, 0, 0x0001)])


# ── Controller battery ────────────────────────────────────────────────────────
# 1) Windows.Gaming.Input (optional package "winrt-Windows.Gaming.Input"):
#    exact percentage for Xbox pads over Bluetooth / Xbox Wireless Adapter.
# 2) XInput: a level (empty / low / medium / full) or "wired".
# 3) SDL's power level (from the App, as a last resort).
_wgi_gamepad = None
_wgi_tried   = False


def _wgi_battery():
    """{"pct", "charging"} from Windows.Gaming.Input, or None."""
    global _wgi_gamepad, _wgi_tried
    if not _wgi_tried:
        _wgi_tried = True
        for mod in ("winrt.windows.gaming.input", "winsdk.windows.gaming.input"):
            try:
                _wgi_gamepad = __import__(mod, fromlist=["Gamepad"]).Gamepad
                break
            except Exception:  # noqa: BLE001
                continue
        if _wgi_gamepad is not None:
            try:
                list(_wgi_gamepad.gamepads)      # first look starts enumeration
                time.sleep(1.0)
            except Exception:  # noqa: BLE001
                pass
    if _wgi_gamepad is None:
        return None
    try:
        for gp in list(_wgi_gamepad.gamepads):
            rep = gp.try_get_battery_report()
            if rep is None:
                continue
            status = int(getattr(rep, "status", 0) or 0)   # 0 not present, 1 discharging, 2 idle, 3 charging
            full = rep.full_charge_capacity_in_milliwatt_hours
            left = rep.remaining_capacity_in_milliwatt_hours
            full = getattr(full, "value", full)
            left = getattr(left, "value", left)
            if status == 0 or not full or left is None:
                continue
            pct = max(0, min(100, round(100 * left / full)))
            return {"pct": pct, "level": None, "wired": False, "charging": status == 3}
    except Exception:  # noqa: BLE001
        return None
    return None


def _xinput_battery():
    """Battery level of the first connected XInput pad, or None."""
    try:
        import ctypes

        class XBI(ctypes.Structure):
            _fields_ = [("BatteryType", ctypes.c_ubyte), ("BatteryLevel", ctypes.c_ubyte)]
        dll = None
        for name in ("xinput1_4", "xinput1_3", "xinput9_1_0"):
            try:
                dll = getattr(ctypes.windll, name)
                break
            except OSError:
                continue
        if dll is None or not hasattr(dll, "XInputGetBatteryInformation"):
            return None
        for idx in range(4):
            info = XBI()
            if dll.XInputGetBatteryInformation(idx, 0, ctypes.byref(info)) != 0:
                continue
            if info.BatteryType == 0:                  # disconnected
                continue
            if info.BatteryType == 1:                  # wired
                return {"pct": None, "level": None, "wired": True, "charging": False}
            if info.BatteryType == 0xFF:               # unknown (many 3rd-party pads)
                continue
            level = ("empty", "low", "medium", "full")[min(3, info.BatteryLevel)]
            return {"pct": None, "level": level, "wired": False, "charging": False}
    except Exception:  # noqa: BLE001
        return None
    return None

# GameSir (Cyclone 2 and friends) — the same way GameSir Connect does it: the
# vendor HID collection (usage page 0xFFF0) of the 2.4 GHz dongle / cable sends
# live state reports (ID 0x12) while it gets a heartbeat (0F F2 00) every second.
# In those reports byte 35 = charging, byte 36 = battery %. Needs "hidapi" (pip).
GAMESIR_VID  = 0x3537
GAMESIR_SKIP = {0x0575}            # dongle with no controller paired / switched on


def _gamesir_battery():
    try:
        import hid  # type: ignore[import]
    except Exception:  # noqa: BLE001
        return None
    try:
        devs = [d for d in hid.enumerate(GAMESIR_VID, 0)
                if d.get("usage_page") == 0xFFF0 and d.get("product_id") not in GAMESIR_SKIP]
    except Exception:  # noqa: BLE001
        return None
    heartbeat = bytes([0x0F, 0xF2, 0x00]) + bytes(61)
    for d in devs:
        dev = None
        try:
            if hasattr(hid, "device"):                 # "hidapi" package
                dev = hid.device()
                dev.open_path(d["path"])
                read = lambda: dev.read(64, 120)
            else:                                      # "hid" package
                dev = hid.Device(path=d["path"])
                read = lambda: dev.read(64, 120)
            end = time.time() + 1.5
            next_hb = 0.0
            while time.time() < end:
                if time.time() >= next_hb:
                    dev.write(heartbeat)
                    next_hb = time.time() + 0.9
                data = bytes(read() or b"")
                if len(data) > 36 and data[0] == 0x12:
                    pct = data[36]
                    if 0 <= pct <= 100:
                        return {"pct": pct, "level": None, "wired": False,
                                "charging": data[35] == 1}
        except Exception:  # noqa: BLE001
            continue
        finally:
            try:
                if dev is not None:
                    dev.close()
            except Exception:  # noqa: BLE001
                pass
    return None


def read_battery():
    if sys.platform != "win32":
        return None
    return _gamesir_battery() or _wgi_battery() or _xinput_battery()


_SDL_POWER = {"empty": "empty", "low": "low", "medium": "medium", "full": "full",
              "max": "full", "wired": "wired"}


def draw_battery(surf, font, x_right, cy, bat, colour):
    """Battery icon + "78%" / level, right-aligned at x_right. Returns its width."""
    if not bat:
        return 0
    if bat.get("wired") and bat.get("pct") is None:
        t = font.render("Wired", True, colour)
        surf.blit(t, t.get_rect(midright=(x_right, cy)))
        return t.get_width()
    pct   = bat.get("pct")
    frac  = pct / 100 if pct is not None else {"empty": 0.05, "low": 0.25, "medium": 0.6,
                                               "full": 1.0}.get(bat.get("level"), 0)
    label = f"{pct}%" if pct is not None else (bat.get("level") or "").title()
    col   = (C_RED if frac <= 0.15 else C_YELLOW if frac <= 0.3 else colour)
    t     = font.render(label, True, col)
    w, h  = _s(22), _s(11)
    tx    = x_right - t.get_width()
    bx    = tx - _s(6) - w - _s(2)
    body  = pygame.Rect(bx, cy - h // 2, w, h)
    pygame.draw.rect(surf, col, body, 1, border_radius=2)
    pygame.draw.rect(surf, col, (body.right, cy - h // 4, _s(2), h // 2))
    fill = int((w - 4) * max(0.0, min(1.0, frac)))
    if fill > 0:
        pygame.draw.rect(surf, col, (body.x + 2, body.y + 2, fill, h - 4), border_radius=1)
    if bat.get("charging"):                          # lightning bolt over the icon
        c = body.center
        k = h * 0.45
        pts = [(c[0] + k * 0.3, c[1] - k), (c[0] - k * 0.5, c[1] + k * 0.15),
               (c[0] + k * 0.05, c[1] + k * 0.15), (c[0] - k * 0.3, c[1] + k),
               (c[0] + k * 0.5, c[1] - k * 0.15), (c[0] - k * 0.05, c[1] - k * 0.15)]
        pygame.draw.polygon(surf, C_WHITE, pts)
    surf.blit(t, (tx, cy - t.get_height() // 2))
    return x_right - bx


def _joyxoff_window_open() -> bool:
    """Fallback detection: any top-level window whose title mentions JoyXoff."""
    import ctypes
    from ctypes import wintypes
    user32, found = ctypes.windll.user32, []
    PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def cb(hwnd, _lp):
        buf = ctypes.create_unicode_buffer(256)
        if user32.GetWindowTextW(hwnd, buf, 256) and "joyxoff" in buf.value.lower():
            found.append(hwnd)
            return False
        return True

    user32.EnumWindows(PROC(cb), 0)
    return bool(found)


def joyxoff_running() -> bool:
    """True if a JoyXoff process is running (matched by name, any variant)."""
    if sys.platform != "win32":
        return False
    import ctypes

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [("dwSize", ctypes.c_uint32), ("cntUsage", ctypes.c_uint32),
                    ("th32ProcessID", ctypes.c_uint32), ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", ctypes.c_uint32), ("cntThreads", ctypes.c_uint32),
                    ("th32ParentProcessID", ctypes.c_uint32), ("pcPriClassBase", ctypes.c_int32),
                    ("dwFlags", ctypes.c_uint32), ("szExeFile", ctypes.c_wchar * 260)]
    k32  = ctypes.windll.kernel32
    snap = k32.CreateToolhelp32Snapshot(0x2, 0)             # TH32CS_SNAPPROCESS
    if snap in (0, -1, ctypes.c_void_p(-1).value):
        return False
    try:
        e = PROCESSENTRY32W()
        e.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        ok = k32.Process32FirstW(snap, ctypes.byref(e))
        while ok:
            if "joyxoff" in e.szExeFile.lower():
                return True
            ok = k32.Process32NextW(snap, ctypes.byref(e))
    finally:
        k32.CloseHandle(snap)
    try:
        return _joyxoff_window_open()
    except Exception:  # noqa: BLE001
        return False


def _win_process_exe(hwnd) -> str:
    """Lower-case exe file name of the process that owns a window ('' if unknown)."""
    import ctypes
    from ctypes import wintypes
    pid = wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid.value)   # QUERY_LIMITED_INFORMATION
    if not h:
        return ""
    try:
        buf  = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(1024)
        if ctypes.windll.kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            return os.path.basename(buf.value).lower()
    finally:
        ctypes.windll.kernel32.CloseHandle(h)
    return ""


def _win_foreground():
    """Return (hwnd, class_name) of the current foreground window (Windows only)."""
    import ctypes
    user32 = ctypes.windll.user32
    hwnd   = user32.GetForegroundWindow()
    if not hwnd:
        return 0, ""
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return hwnd, buf.value


# ── UNINSTALL & REMOVE SHORTCUT ──────────────────────────────────────────────
_STEAM_ID_RE = re.compile(r"(?:-applaunch\s+|steam://(?:rungameid|run)/)(\d+)", re.IGNORECASE)
# Folders too generic to identify a single program by "exe lives inside it"
_GENERIC_DIRS = {"program files", "program files (x86)", "programdata", "games",
                 "common", "steamapps", "windows", "users", "appdata", "local",
                 "roaming", "programs", "epic games", "gog galaxy", "xboxgames"}


def _norm_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def _steam_app_id(entry: dict):
    """Steam app id if the shortcut launches a Steam game, else None."""
    m = _STEAM_ID_RE.search(f"{entry.get('target', '')} {entry.get('args', '')}")
    return m.group(1) if m else None


def _registry_uninstallers() -> list:
    """All programs from the Windows 'Installed apps' registry keys."""
    if sys.platform != "win32":
        return []
    import winreg
    roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    out = []
    for hive, path in roots:
        try:
            root = winreg.OpenKey(hive, path)
        except OSError:
            continue
        i = 0
        while True:
            try:
                sub = winreg.EnumKey(root, i)
            except OSError:
                break
            i += 1
            try:
                with winreg.OpenKey(root, sub) as k:
                    def val(n, k=k):
                        try:
                            return winreg.QueryValueEx(k, n)[0]
                        except OSError:
                            return ""
                    if val("SystemComponent") == 1:
                        continue
                    cmd  = str(val("UninstallString") or "").strip()
                    name = str(val("DisplayName") or "").strip()
                    if cmd and name:
                        out.append({"name": name, "cmd": cmd,
                                    "loc": str(val("InstallLocation") or "").strip().strip('"')})
            except OSError:
                continue
        winreg.CloseKey(root)
    return out


def find_uninstaller(entry: dict):
    """Work out how to uninstall what a shortcut launches.

    Returns {"name": program name, "cmd": command or steam:// URL, "kind": ...}
    or None when nothing reliable is found.
    """
    app_id = _steam_app_id(entry)
    if app_id:
        return {"name": entry["name"], "cmd": f"steam://uninstall/{app_id}", "kind": "steam"}

    target = entry.get("target", "")
    if not target or "://" in target:
        return None          # e.g. Epic / Store URL shortcuts — no uninstaller to call
    t_dir   = os.path.normcase(os.path.dirname(os.path.abspath(target)))
    progs   = _registry_uninstallers()

    # 1) The program whose install folder contains the shortcut's exe (most specific wins)
    best, best_len = None, 0
    for p in progs:
        loc = p["loc"]
        if not loc:
            continue
        loc_n = os.path.normcase(os.path.abspath(loc)).rstrip("\\")
        parts = [x for x in loc_n.split("\\") if x]
        if len(parts) < 2 or parts[-1] in _GENERIC_DIRS:
            continue
        if (t_dir == loc_n or t_dir.startswith(loc_n + "\\")) and len(loc_n) > best_len:
            best, best_len = p, len(loc_n)
    if best:
        return {"name": best["name"], "cmd": best["cmd"], "kind": "program"}

    # 2) Same name as the shortcut
    want = _norm_name(entry["name"])
    if len(want) >= 4:
        for p in progs:
            if _norm_name(p["name"]) == want:
                return {"name": p["name"], "cmd": p["cmd"], "kind": "program"}
    return None


INSTALLED_APPS_URI = "ms-settings:appsfeatures"
_GOG_ID_RE  = re.compile(r"(?:/gameId=|gameId=|openGameView/|launch/)(\d{6,})", re.IGNORECASE)
_UPLAY_ID_RE = re.compile(r"uplay://launch/(\d+)", re.IGNORECASE)


def find_uninstall_route(entry: dict):
    """How to uninstall a shortcut's game/app, best option first.

    kind = "steam" / "program"  → runs a real uninstaller (asks for confirmation)
    kind = "launcher"           → opens the launcher's library page for the game
    kind = "settings"           → opens Windows Settings › Installed apps
    """
    exact = find_uninstaller(entry)
    if exact:
        return exact

    target = entry.get("target", "") or ""
    blob   = f"{target} {entry.get('args', '')}".lower()
    name   = entry["name"]

    # Epic: games aren't listed in Installed apps — uninstall from Epic's library
    if blob.startswith("com.epicgames.launcher://") or "com.epicgames.launcher://" in blob \
            or "\\epic games\\" in blob:
        return {"name": "Epic Games library", "cmd": "com.epicgames.launcher://store/library",
                "kind": "launcher", "game": name}
    # GOG Galaxy: open the game's page (it has the Uninstallation option)
    if "goggalaxy" in blob or "galaxyclient.exe" in blob:
        m = _GOG_ID_RE.search(blob)
        if m:
            return {"name": "GOG Galaxy", "cmd": f"goggalaxy://openGameView/{m.group(1)}",
                    "kind": "launcher", "game": name}
    # Ubisoft Connect
    m = _UPLAY_ID_RE.search(blob)
    if m:
        return {"name": "Ubisoft Connect", "cmd": f"uplay://uninstall/{m.group(1)}",
                "kind": "launcher", "game": name}
    # Microsoft Store / Xbox, EA app, other launcher links, anything unmatched
    return {"name": "Installed apps", "cmd": INSTALLED_APPS_URI, "kind": "settings", "game": name}


def is_elevated() -> bool:
    """True if GameClub runs as administrator (the installed GameClub.exe does)."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:  # noqa: BLE001
        return False


def open_as_user(path: str) -> None:
    """Open a shortcut / program the way a double click would. When GameClub runs as
    administrator, games must NOT inherit that (Steam & co. complain, and it isn't
    safe), so Explorer — which runs as the normal user — opens it for us."""
    if is_elevated():
        if not os.path.exists(path):
            raise OSError(f"Not found: {path}")
        subprocess.Popen(["explorer.exe", path], creationflags=CREATE_NO_WINDOW)
    else:
        os.startfile(path)  # type: ignore[attr-defined]


_TASK_XML = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>Start GameClub when you sign in</Description></RegistrationInfo>
  <Triggers>
    <LogonTrigger><Enabled>true</Enabled><UserId>{user}</UserId></LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{user}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>4</Priority>
    <IdleSettings><StopOnIdleEnd>false</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings>
  </Settings>
  <Actions Context="Author">
    <Exec><Command>"{exe}"</Command><WorkingDirectory>{cwd}</WorkingDirectory></Exec>
  </Actions>
</Task>
"""


def set_startup_task(enable: bool, exe: str = "") -> bool:
    """Start with Windows for an administrator GameClub: a scheduled task that runs
    at sign-in with full rights (a Run-key entry can't start an admin program
    without a UAC prompt — Windows just skips it). Returns True on success."""
    from xml.sax.saxutils import escape
    try:
        if not enable:
            r = subprocess.run(["schtasks", "/Delete", "/TN", "GameClub", "/F"],
                               capture_output=True, creationflags=CREATE_NO_WINDOW)
            return r.returncode == 0
        user = f"{os.environ.get('USERDOMAIN', '')}\\{os.environ.get('USERNAME', '')}".lstrip("\\")
        xml  = _TASK_XML.format(user=escape(user), exe=escape(exe),
                                cwd=escape(os.path.dirname(exe)))
        path = os.path.join(tempfile.gettempdir(), "padhub_task.xml")
        with open(path, "w", encoding="utf-16") as fh:
            fh.write(xml)
        r = subprocess.run(["schtasks", "/Create", "/TN", "GameClub", "/XML", path, "/F"],
                           capture_output=True, creationflags=CREATE_NO_WINDOW)
        try:
            os.remove(path)
        except OSError:
            pass
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def run_uninstaller(cmd: str) -> bool:
    """Start an uninstallation command. ShellExecute handles the UAC prompt."""
    if "://" in cmd.split(" ")[0] or cmd.lower().startswith("ms-settings:"):
        os.startfile(cmd)  # type: ignore[attr-defined]
        return True
    cmd = cmd.strip()
    if cmd.startswith('"'):
        end = cmd.find('"', 1)
        exe, params = cmd[1:end], cmd[end + 1:].strip()
    else:
        m = re.match(r"(.+?\.exe)(\s.*)?$", cmd, re.IGNORECASE)
        exe, params = (m.group(1), (m.group(2) or "").strip()) if m else (cmd, "")
    if os.path.basename(exe).lower() == "msiexec.exe" or exe.lower() == "msiexec":
        params = re.sub(r"/I(?=\s*\{)", "/X", params, flags=re.IGNORECASE)  # repair -> uninstall
    import ctypes
    rc = ctypes.windll.shell32.ShellExecuteW(None, "open", exe, params or None, None, 1)
    return rc > 32


def move_to_recycle_bin(path: str) -> bool:
    """Send a file to the Recycle Bin (never a permanent delete)."""
    if sys.platform != "win32":
        return False
    import ctypes
    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT),
                    ("pFrom", wintypes.LPCWSTR), ("pTo", wintypes.LPCWSTR),
                    ("fFlags", ctypes.c_uint16), ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", wintypes.LPCWSTR)]
    FO_DELETE = 3
    flags = 0x40 | 0x10 | 0x04 | 0x400   # ALLOWUNDO | NOCONFIRMATION | SILENT | NOERRORUI
    op = SHFILEOPSTRUCTW(None, FO_DELETE, path + "\0", None, flags, False, None, None)
    rc = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    return rc == 0 and not op.fAnyOperationsAborted and not os.path.exists(path)


def _win_big_windows() -> dict:
    """{hwnd: pid} of visible, normal-sized top-level windows (game candidates)."""
    import ctypes
    from ctypes import wintypes
    user32, out = ctypes.windll.user32, {}
    own_pid = os.getpid()
    PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def cb(hwnd, _lp):
        if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
            return True
        if user32.GetWindowLongW(hwnd, -20) & 0x80:          # WS_EX_TOOLWINDOW
            return True
        r = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(r))
        if r.right - r.left < 640 or r.bottom - r.top < 360:  # skip small pop-ups
            return True
        cloaked = wintypes.DWORD(0)
        try:
            ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 14, ctypes.byref(cloaked), 4)
        except Exception:  # noqa: BLE001
            pass
        if cloaked.value:                                     # hidden Store/UWP frames
            return True
        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf, 256)
        if buf.value in _IDLE_WINDOW_CLASSES:
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value != own_pid:
            out[hwnd] = pid.value
        return True

    user32.EnumWindows(PROC(cb), 0)
    return out


def _win_all_visible() -> set:
    """Every visible top-level window, minimized ones included."""
    import ctypes
    from ctypes import wintypes
    user32, out = ctypes.windll.user32, set()
    PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def cb(hwnd, _lp):
        if user32.IsWindowVisible(hwnd):
            out.add(hwnd)
        return True

    user32.EnumWindows(PROC(cb), 0)
    return out


# ── Hiding the Windows pointer over full-screen games ─────────────────────────
# Some games never hide the pointer, so it sits in the middle of the picture.
# While such a game (launched from GameClub) is in front and you're on the pad,
# every standard Windows pointer shape is swapped for an invisible one; one call
# (SPI_SETCURSORS) puts the user's normal pointers back.
_OCR_IDS = (32512, 32513, 32514, 32515, 32516, 32642, 32643, 32644, 32645, 32646,
            32648, 32649, 32650, 32651)
_blank_cursor_handle = None


def hide_system_cursor() -> bool:
    global _blank_cursor_handle
    import ctypes
    from ctypes import wintypes
    u32 = ctypes.windll.user32
    u32.CreateCursor.restype = wintypes.HANDLE
    u32.CopyImage.restype = wintypes.HANDLE
    if not _blank_cursor_handle:
        and_mask = (ctypes.c_ubyte * 128)(*([0xFF] * 128))     # 32×32: all transparent
        xor_mask = (ctypes.c_ubyte * 128)()
        _blank_cursor_handle = u32.CreateCursor(None, 0, 0, 32, 32, and_mask, xor_mask)
    if not _blank_cursor_handle:
        return False
    ok = True
    for ocr in _OCR_IDS:   # SetSystemCursor takes ownership — hand it a fresh copy each time
        h = u32.CopyImage(wintypes.HANDLE(_blank_cursor_handle), 2, 0, 0, 0)   # IMAGE_CURSOR
        ok = bool(h and u32.SetSystemCursor(wintypes.HANDLE(h), ocr)) and ok
    return ok


def restore_system_cursor() -> None:
    """Put the user's own pointer scheme back (also safe if it was never hidden)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, None, 0)    # SPI_SETCURSORS
    except Exception:  # noqa: BLE001
        pass


def _last_input_tick() -> int:
    """Time of the last real keyboard / mouse input (controllers don't count)."""
    import ctypes
    from ctypes import wintypes

    class LII(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]
    li = LII()
    li.cbSize = ctypes.sizeof(LII)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li))
    return li.dwTime


def _win_pid(hwnd) -> int:
    import ctypes
    from ctypes import wintypes
    pid = wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def _pid_alive(pid) -> bool:
    import ctypes
    k32 = ctypes.windll.kernel32
    h = k32.OpenProcess(0x00100000 | 0x1000, False, pid)        # SYNCHRONIZE | QUERY_LIMITED
    if not h:
        return False
    try:
        return k32.WaitForSingleObject(h, 0) == 0x102             # WAIT_TIMEOUT = still running
    finally:
        k32.CloseHandle(h)


def _close_pid_windows(pids) -> int:
    """Ask a program to close, like clicking its X: WM_CLOSE to its visible windows."""
    import ctypes
    u32, n = ctypes.windll.user32, 0
    for h in _win_all_visible():
        if _win_pid(h) in pids:
            u32.PostMessageW(h, 0x0010, 0, 0)                     # WM_CLOSE
            n += 1
    return n


def _kill_pid(pid) -> bool:
    import ctypes
    k32 = ctypes.windll.kernel32
    h = k32.OpenProcess(0x0001, False, pid)                       # PROCESS_TERMINATE
    if not h:
        return False
    try:
        return bool(k32.TerminateProcess(h, 1))
    finally:
        k32.CloseHandle(h)


# ── Synthetic keyboard / mouse input (for the on-screen keyboard) ────────────
VK_BACK, VK_TAB, VK_RETURN, VK_SHIFT = 0x08, 0x09, 0x0D, 0x10


def _sendinput_types():
    import ctypes

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_uint16), ("wScan", ctypes.c_uint16),
                    ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32),
                    ("dwExtraInfo", ctypes.c_size_t)]

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_int32), ("dy", ctypes.c_int32),
                    ("mouseData", ctypes.c_uint32), ("dwFlags", ctypes.c_uint32),
                    ("time", ctypes.c_uint32), ("dwExtraInfo", ctypes.c_size_t)]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", ctypes.c_uint32), ("wParamL", ctypes.c_uint16),
                    ("wParamH", ctypes.c_uint16)]

    class _U(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_uint32), ("u", _U)]

    return INPUT, KEYBDINPUT, MOUSEINPUT


def _send_inputs(items) -> None:
    """items: list of ('key', vk, scan, flags) / ('mouse', dx, dy, flags)."""
    import ctypes
    INPUT, KEYBDINPUT, MOUSEINPUT = _sendinput_types()
    arr = (INPUT * len(items))()
    for i, it in enumerate(items):
        if it[0] == "key":
            arr[i].type = 1
            arr[i].u.ki = KEYBDINPUT(it[1], it[2], it[3], 0, 0)
        elif it[0] == "wheel":
            arr[i].type = 0
            arr[i].u.mi = MOUSEINPUT(0, 0, it[1] & 0xFFFFFFFF, it[2], 0, 0)
        else:
            arr[i].type = 0
            arr[i].u.mi = MOUSEINPUT(it[1], it[2], 0, it[3], 0, 0)
    ctypes.windll.user32.SendInput(len(items), arr, ctypes.sizeof(INPUT))


def send_text(text: str) -> None:
    """Type text into the focused window (Unicode — works for any character)."""
    ev = []
    for ch in text:
        ev += [("key", 0, ord(ch), 0x0004), ("key", 0, ord(ch), 0x0004 | 0x0002)]
    _send_inputs(ev)


def send_vk(vk: int, shift: bool = False) -> None:
    ev = [("key", VK_SHIFT, 0, 0)] if shift else []
    ev += [("key", vk, 0, 0), ("key", vk, 0, 0x0002)]
    if shift:
        ev += [("key", VK_SHIFT, 0, 0x0002)]
    _send_inputs(ev)


def mouse_move(dx: int, dy: int) -> None:
    _send_inputs([("mouse", dx, dy, 0x0001)])


def mouse_button(down: bool, right: bool = False) -> None:
    flag = (0x0008 if down else 0x0010) if right else (0x0002 if down else 0x0004)
    _send_inputs([("mouse", 0, 0, flag)])


def mouse_middle(down: bool) -> None:
    _send_inputs([("mouse", 0, 0, 0x0020 if down else 0x0040)])


def mouse_wheel(delta: int, horizontal: bool = False) -> None:
    """Scroll by delta (120 = one notch; + = up / right)."""
    _send_inputs([("wheel", delta, 0x01000 if horizontal else 0x0800)])


VK_LEFT, VK_UP, VK_RIGHT, VK_DOWN = 0x25, 0x26, 0x27, 0x28


def send_arrow(vk: int) -> None:
    """Tap an arrow key (extended-key flag so it isn't read as the numpad)."""
    _send_inputs([("key", vk, 0, 0x0001), ("key", vk, 0, 0x0001 | 0x0002)])


def _win_bring_to_front(hwnd) -> None:
    """Put another program's window in front (used for the game just launched)."""
    import ctypes
    user32 = ctypes.windll.user32
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)                            # SW_RESTORE
    user32.keybd_event(0x12, 0, 0, 0)                         # Alt tap lifts the
    user32.keybd_event(0x12, 0, 2, 0)                         # focus-steal lock
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)


def _win_restore_and_focus(hwnd) -> None:
    """Un-minimize our window and force it to the foreground."""
    import ctypes
    user32 = ctypes.windll.user32
    user32.ShowWindow(hwnd, 9 if user32.IsIconic(hwnd) else 5)   # SW_RESTORE / SW_SHOW
    # Windows only lets the foreground process change focus; a synthetic Alt
    # tap lifts that restriction for this call.
    user32.keybd_event(0x12, 0, 0, 0)
    user32.keybd_event(0x12, 0, 2, 0)
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)


# ── SHARED PANEL STYLE (Power, Move-to and Settings) ─────────────────────────
PANEL_TOP    = (34, 38, 48)
PANEL_BOT    = (20, 22, 28)
PANEL_BORDER = (58, 64, 80)
PANEL_DIV    = (52, 58, 72)


def draw_panel(surf, rect, rad):
    """Rounded panel with soft drop shadow and a gentle vertical gradient."""
    px, py, pw, ph = rect
    for i, a in enumerate((60, 40, 22)):
        grow = _s(6) * (i + 1)
        sh = pygame.Surface((pw + grow * 2, ph + grow * 2), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, a), sh.get_rect(), border_radius=rad + grow)
        surf.blit(sh, (px - grow, py - grow + _s(6)))
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for yy in range(ph):
        t = yy / max(1, ph - 1)
        c = tuple(int(PANEL_TOP[k] + (PANEL_BOT[k] - PANEL_TOP[k]) * t) for k in range(3))
        pygame.draw.line(panel, c, (0, yy), (pw, yy))
    mask = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rad)
    panel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(panel, (px, py))
    pygame.draw.rect(surf, PANEL_BORDER, pygame.Rect(rect), width=1, border_radius=rad)


def draw_panel_header(surf, fonts, rect, header_h, title, subtitle=None):
    """Title (and optional subtitle) centred between the panel top and a divider."""
    px, py, pw, _ = rect
    div_y = py + header_h
    t  = fonts["title"].render(title, True, C_WHITE)
    st = None
    if subtitle:
        sub = subtitle if len(subtitle) <= 34 else subtitle[:32] + "..."
        st  = fonts["hint"].render(sub, True, C_ACCENT2)
    block_h = t.get_height() + (st.get_height() + _s(2) if st else 0)
    ty = py + (header_h - block_h) // 2
    surf.blit(t, t.get_rect(centerx=px + pw // 2, y=ty))
    if st:
        surf.blit(st, st.get_rect(centerx=px + pw // 2, y=ty + t.get_height() + _s(2)))
    pygame.draw.line(surf, PANEL_DIV, (px + _s(20), div_y), (px + pw - _s(20), div_y))


def draw_panel_footer(surf, font, rect, footer_h, hints):
    """Divider + centred button hints at the bottom of a panel."""
    px, py, pw, ph = rect
    fy = py + ph - footer_h
    pygame.draw.line(surf, PANEL_DIV, (px + _s(20), fy), (px + pw - _s(20), fy))
    width = hints_width(font, hints)
    draw_hints(surf, font, hints, px + (pw - width) // 2, fy + footer_h // 2)


def draw_tab(surf, rect, active):
    """Tab pill in the shared panel style; active = blue fill and outline."""
    rad = _s(8)
    tab = pygame.Surface(rect.size, pygame.SRCALPHA)
    for yy in range(rect.height):
        t = yy / max(1, rect.height - 1)
        c = tuple(int(PANEL_TOP[k] + (PANEL_BOT[k] - PANEL_TOP[k]) * t) for k in range(3))
        pygame.draw.line(tab, c, (0, yy), (rect.width, yy))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rad)
    tab.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tab, rect.topleft)
    if active:
        draw_rounded_rect(surf, C_ACCENT, rect, radius=rad, alpha=55)
        pygame.draw.rect(surf, C_ACCENT, rect, width=2, border_radius=rad)
    else:
        pygame.draw.rect(surf, PANEL_BORDER, rect, width=1, border_radius=rad)


def draw_row_highlight(surf, rr, col):
    """Selected-row style: tinted fill and outline."""
    draw_rounded_rect(surf, col, rr, radius=_s(12), alpha=50)
    pygame.draw.rect(surf, col, rr, width=2, border_radius=_s(12))


# ── ON-SCREEN KEYBOARD (controller typing for launcher logins) ───────────────
def _osk_char_row(pairs):
    return [{"kind": "char", "n": n, "s": sh, "w": 1.0} for n, sh in pairs]


OSK_ROWS = [
    _osk_char_row(list(zip("`1234567890-=", "~!@#$%^&*()_+"))),
    _osk_char_row([(c, c.upper()) for c in "qwertyuiop"] + [("[", "{"), ("]", "}"), ("\\", "|")]),
    _osk_char_row([(c, c.upper()) for c in "asdfghjkl"] + [(";", ":"), ("'", '"')]),
    _osk_char_row([(c, c.upper()) for c in "zxcvbnm"] + [(",", "<"), (".", ">"), ("/", "?")]),
    [{"kind": "shift", "label": "Shift", "w": 2.0},
     {"kind": "char", "n": "@", "s": "@", "w": 1.0},
     {"kind": "space", "label": "Space", "w": 4.0},
     {"kind": "text", "label": ".com", "text": ".com", "w": 1.6},
     {"kind": "bksp", "label": "Backspace", "w": 2.4},
     {"kind": "tab", "label": "Tab", "w": 1.6},
     {"kind": "enter", "label": "Enter", "w": 2.0}],
]
OSK_UNITS = max(sum(k["w"] for k in row) for row in OSK_ROWS)


# Same keys as the controller keyboard; bottom row has Paste and Done instead of
# .com / Tab / Enter (folder paths need ":" and "\\" — both are on the keyboard)
SETTINGS_OSK_ROWS = OSK_ROWS[:4] + [[
    {"kind": "shift", "label": "Shift", "w": 2.0},
    {"kind": "char", "n": "@", "s": "@", "w": 1.0},
    {"kind": "space", "label": "Space", "w": 3.6},
    {"kind": "paste", "label": "Paste", "w": 1.8},
    {"kind": "bksp", "label": "Backspace", "w": 2.4},
    {"kind": "done", "label": "Done", "w": 2.4},
]]
SETTINGS_OSK_UNITS = max(sum(k["w"] for k in row) for row in SETTINGS_OSK_ROWS)


def clipboard_text() -> str:
    try:
        import tkinter as _tk
        root = _tk.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        return (text or "").strip()
    except Exception:  # noqa: BLE001
        return ""


# ── Folder / image picker (Settings → Shortcuts Folder, Wallpaper Image) ─────
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif", ".tga"}
_picker_executor = ThreadPoolExecutor(max_workers=2)


def _fmt_bytes(n):
    if n is None:
        return ""
    for unit, k in (("TB", 1 << 40), ("GB", 1 << 30), ("MB", 1 << 20), ("KB", 1 << 10)):
        if n >= k:
            v = n / k
            return f"{v:.0f} {unit}" if v >= 10 or unit in ("GB", "TB") else f"{v:.1f} {unit}"
    return f"{n} B"


def list_drives():
    """[(root, label, free bytes or None)] for the picker's drive list."""
    if sys.platform != "win32":
        try:
            import shutil
            free = shutil.disk_usage("/").free
        except OSError:
            free = None
        return [("/", "Root", free)]
    import ctypes
    import string
    k32  = ctypes.windll.kernel32
    prev = k32.SetErrorMode(1)            # no "insert a disk" dialogs for empty readers
    out  = []
    try:
        mask = k32.GetLogicalDrives()
        for i, letter in enumerate(string.ascii_uppercase):
            if not mask & (1 << i):
                continue
            root  = f"{letter}:\\"
            dtype = k32.GetDriveTypeW(ctypes.c_wchar_p(root))
            if dtype in (0, 1):                       # unknown / not a drive
                continue
            label, free = "", None
            if dtype == 4:                            # network: don't wait on it
                label = "Network drive"
            else:
                buf = ctypes.create_unicode_buffer(261)
                ok  = k32.GetVolumeInformationW(ctypes.c_wchar_p(root), buf, 261,
                                                None, None, None, None, 0)
                if not ok and dtype in (2, 5):        # empty card reader / DVD drive
                    continue
                label = buf.value if ok else ""
                fb = ctypes.c_ulonglong(0)
                if k32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(root), ctypes.byref(fb), None, None):
                    free = fb.value
            if not label:
                label = {2: "USB drive", 3: "Local Disk", 5: "DVD drive"}.get(dtype, "Drive")
            out.append((root, label, free))
    finally:
        k32.SetErrorMode(prev)
    return out


# Windows "known folder" IDs — these follow OneDrive / moved folders
_KNOWN_FOLDERS = [
    ("Desktop",   "{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}"),
    ("Documents", "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}"),
    ("Downloads", "{374DE290-123F-4565-9164-39C4925E467B}"),
    ("Pictures",  "{33E28130-4E1E-4676-835A-98395C3BC3BB}"),
]


def user_places():
    """[(path, name)] of Desktop, Documents, Downloads, Pictures that exist."""
    out = []
    for name, guid in _KNOWN_FOLDERS:
        path = None
        if sys.platform == "win32":
            try:
                import ctypes
                import uuid
                from ctypes import wintypes

                class GUID(ctypes.Structure):
                    _fields_ = [("d1", ctypes.c_uint32), ("d2", ctypes.c_uint16),
                                ("d3", ctypes.c_uint16), ("d4", ctypes.c_ubyte * 8)]
                u = uuid.UUID(guid)
                g = GUID(u.time_low, u.time_mid, u.time_hi_version,
                         (ctypes.c_ubyte * 8).from_buffer_copy(u.bytes[8:]))
                buf = ctypes.c_wchar_p()
                fn = ctypes.windll.shell32.SHGetKnownFolderPath
                fn.argtypes = [ctypes.POINTER(GUID), wintypes.DWORD, wintypes.HANDLE,
                               ctypes.POINTER(ctypes.c_wchar_p)]
                if fn(ctypes.byref(g), 0, None, ctypes.byref(buf)) == 0:
                    path = buf.value
                    ctypes.windll.ole32.CoTaskMemFree(buf)
            except Exception:  # noqa: BLE001
                path = None
        if not path:
            path = os.path.join(os.path.expanduser("~"), name)
        if os.path.isdir(path):
            out.append((path, name))
    return out


def _count_shortcuts(path, max_depth=3, budget=4000):
    """How many launchable shortcuts a folder holds (subfolders included)."""
    n, seen = 0, 0
    stack = [(path, 0)]
    while stack and seen < budget:
        d, depth = stack.pop()
        try:
            with os.scandir(d) as it:
                for de in it:
                    seen += 1
                    try:
                        if de.is_dir(follow_symlinks=False):
                            if depth < max_depth and not de.name.startswith((".", "$")):
                                stack.append((de.path, depth + 1))
                        elif os.path.splitext(de.name)[1].lower() in LAUNCH_EXTS:
                            n += 1
                    except OSError:
                        continue
        except OSError:
            continue
    return n


def _load_preview(path, box_w, box_h):
    """(surface, (w, h) of the original) for the wallpaper preview, or None."""
    try:
        try:
            from PIL import Image as PilImage  # type: ignore[import]
            img = PilImage.open(path)
            size = img.size
            img = img.convert("RGB")
            img.thumbnail((box_w * 2, box_h * 2))
            surf = pygame.image.fromstring(img.tobytes(), img.size, "RGB")
        except ImportError:
            surf = pygame.image.load(path)
            size = surf.get_size()
        sw, sh = surf.get_size()
        k = max(box_w / sw, box_h / sh)                     # cover-crop like the wallpaper
        sc = pygame.transform.smoothscale(surf, (max(1, int(sw * k)), max(1, int(sh * k))))
        out = pygame.Surface((box_w, box_h))
        out.blit(sc, ((box_w - sc.get_width()) // 2, (box_h - sc.get_height()) // 2))
        return out, size
    except Exception:  # noqa: BLE001
        return None


class FilePicker:
    """Browse drives and folders with the controller or keyboard.
    mode "folder": pick a folder (Y). mode "image": pick an image file (A)."""

    def __init__(self, mode, title, fonts, width, height):
        self.mode, self.title = mode, title
        self.fonts, self.width, self.height = fonts, width, height
        self.path    = None          # None = "This PC" (drive list)
        self.items   = []
        self.cursor  = 0
        self.start   = 0             # first visible row
        self.focus   = "list"        # or "drives"
        self.dcursor = 0
        self.error   = ""
        self.drives  = None          # filled in the background
        self.places  = user_places() # Desktop, Documents, Downloads, Pictures
        self._counts = {}            # folder → shortcut count (or "…")
        self._prev   = {}            # image path → (surface, size) / None / "…"
        self._want   = (None, 0.0)   # highlighted item + since when
        self._drv_job = _picker_executor.submit(list_drives)
        self._load()

    # ── listing ─────────────────────────────────────────────────────────────
    def _poll_drives(self):
        if self.drives is None and self._drv_job.done():
            try:
                self.drives = self._drv_job.result()
            except Exception:  # noqa: BLE001
                self.drives = []
            if self.path is None:
                self._load()

    def _load(self, select=None):
        self.error = ""
        if self.path is None:
            drives = self.drives or []
            self.items = [{"kind": "drive", "name": f"{r.rstrip(chr(92))}  {lbl}" if r != "/" else lbl,
                           "path": r, "info": (f"{_fmt_bytes(fr)} free" if fr is not None else "")}
                          for r, lbl, fr in drives]
            self.items += [{"kind": "folder", "icon": "place:" + nm, "name": nm, "path": pth, "info": ""}
                           for pth, nm in self.places]
        else:
            items = [{"kind": "up", "name": "Up one level", "path": self._parent(self.path), "info": ""}]
            folders, files = [], []
            try:
                with os.scandir(self.path) as it:
                    for de in it:
                        nm = de.name
                        if nm.startswith((".", "$")) or nm.lower() in ALWAYS_HIDE:
                            continue
                        try:
                            if sys.platform == "win32":
                                attrs = de.stat(follow_symlinks=False).st_file_attributes
                                if attrs & 0x6:                       # hidden / system
                                    continue
                            if de.is_dir():
                                folders.append({"kind": "folder", "name": nm, "path": de.path, "info": ""})
                            elif self.mode == "image" and os.path.splitext(nm)[1].lower() in IMAGE_EXTS:
                                files.append({"kind": "image", "name": nm, "path": de.path,
                                              "info": _fmt_bytes(de.stat().st_size),
                                              "mtime": de.stat().st_mtime})
                        except OSError:
                            continue
            except OSError:
                self.error = "Can’t open this folder"
            folders.sort(key=lambda d: d["name"].lower())
            files.sort(key=lambda d: d["name"].lower())
            self.items = items + folders + files
        self.cursor = 0
        if select is not None:
            for i, it in enumerate(self.items):
                if os.path.normcase(it["path"] or "") == os.path.normcase(select):
                    self.cursor = i
                    break
        elif self.path is not None and len(self.items) > 1:
            self.cursor = 1                          # first real item, not "Up"
        self.start = 0
        self._keep_visible()

    @staticmethod
    def _parent(path):
        """Folder above this one; None above a drive root (= the drive list)."""
        p = path.rstrip("\\/")
        if sys.platform == "win32":
            if len(p) <= 2:                          # "D:" → drive list
                return None
            par = os.path.dirname(p)
            if len(par) == 2 and par[1] == ":":
                par += "\\"
            return par
        if not p:                                    # "/"
            return None
        return os.path.dirname(p) or "/"

    def _open(self, path, select=None):
        self.path = path
        self.focus = "list"
        self._load(select)

    def _go_up(self):
        if self.path is None:
            return "cancel"
        came_from = self.path
        self._open(self._parent(self.path), select=came_from)
        return None

    # ── geometry ────────────────────────────────────────────────────────────
    ROW_H, PITCH = _s(30), _s(34)

    def _layout(self):
        pw = min(self.width - _s(40), _s(920))
        ph = min(self.height - _s(30), _s(520))
        px, py = (self.width - pw) // 2, (self.height - ph) // 2
        hh, fh = _s(46), _s(42)
        top, bottom = py + hh + _s(12), py + ph - fh - _s(10)
        lw = _s(165)
        lx = px + _s(14) + lw + _s(22)
        rw = px + pw - _s(14) - lx
        prev_w = _s(236) if self.mode == "image" else 0
        if prev_w:
            rw -= prev_w + _s(14)
        note_h = _s(40) if self.mode == "folder" else 0
        list_top = top + _s(32)
        rows = max(3, (bottom - note_h - list_top) // self.PITCH)
        return dict(rect=pygame.Rect(px, py, pw, ph), hh=hh, fh=fh, top=top, bottom=bottom,
                    lw=lw, lx=lx, rw=rw, prev_w=prev_w, list_top=list_top, rows=rows, note_h=note_h)

    def _keep_visible(self):
        rows = self._layout()["rows"]
        if self.cursor < self.start:
            self.start = self.cursor
        elif self.cursor >= self.start + rows:
            self.start = self.cursor - rows + 1
        self.start = max(0, min(self.start, max(0, len(self.items) - rows)))

    def _cur(self):
        return self.items[self.cursor] if 0 <= self.cursor < len(self.items) else None

    def _column(self):
        """Left column: drives, then the user folders. [(path, name, icon)]"""
        col = [(r, f"{r.rstrip(chr(92))}  {lbl}" if r != "/" else lbl, "drive")
               for r, lbl, _f in (self.drives or [])]
        return col + [(pth, nm, "place:" + nm) for pth, nm in self.places]

    def _column_current(self):
        """Index of the column entry the current folder is inside (longest match)."""
        cur = os.path.normcase(self.path or "")
        best, best_len = None, -1
        for i, (pth, _n, _i) in enumerate(self._column()):
            base = os.path.normcase(pth).rstrip("\\/")
            if cur == base or cur.startswith(base + os.sep) or (base == "" and cur.startswith(os.sep)):
                if len(base) > best_len:
                    best, best_len = i, len(base)
        return best

    # ── input ───────────────────────────────────────────────────────────────
    def handle_button(self, btn):
        """None, "cancel" or ("pick", path)."""
        self._poll_drives()
        if btn in ("start", "back"):
            return "cancel"
        if self.focus == "drives":
            col = self._column()
            if btn in ("up", "down") and col:
                self.dcursor = (self.dcursor + (-1 if btn == "up" else 1)) % len(col)
            elif btn in ("A", "right") and col:
                self._open(col[self.dcursor][0])
            elif btn == "B":
                self.focus = "list"
            return None
        n = len(self.items)
        if btn in ("up", "down", "LT", "RT") and n:
            step = {"up": -1, "down": 1, "LT": -10, "RT": 10}[btn]
            self.cursor = (self.cursor + step) % n if btn in ("up", "down") \
                else max(0, min(n - 1, self.cursor + step))
            self._keep_visible()
        elif btn == "left":
            if self._column():
                self.focus = "drives"
                cur = self._column_current()
                if cur is not None:
                    self.dcursor = cur
        elif btn == "B":
            return self._go_up()
        elif btn == "A":
            it = self._cur()
            if not it:
                return None
            if it["kind"] == "up":
                return self._go_up()
            if it["kind"] in ("drive", "folder"):
                self._open(it["path"])
            elif it["kind"] == "image":
                return ("pick", it["path"])
        elif btn == "Y" and self.mode == "folder":
            it = self._cur()
            if it and it["kind"] in ("drive", "folder"):
                return ("pick", it["path"])
            if self.path is not None:
                return ("pick", self.path)
        return None

    # ── background work for the highlighted row ─────────────────────────────
    def _update_side_info(self, prev_box):
        it = self._cur()
        key = it["path"] if it and self.focus == "list" else None
        now = time.time()
        if key != self._want[0]:
            self._want = (key, now)
        if not it or now - self._want[1] < 0.15:
            return
        if self.mode == "folder" and it["kind"] in ("folder", "drive") and key not in self._counts:
            self._counts[key] = "…"
            fut = _picker_executor.submit(_count_shortcuts, key)
            fut.add_done_callback(lambda f, k=key: self._counts.__setitem__(
                k, f.result() if not f.exception() else 0))
        if self.mode == "image" and it["kind"] == "image" and key not in self._prev:
            self._prev[key] = "…"
            if len(self._prev) > 40:
                self._prev.pop(next(iter(self._prev)))
            fut = _picker_executor.submit(_load_preview, key, *prev_box)
            fut.add_done_callback(lambda f, k=key: self._prev.__setitem__(
                k, f.result() if not f.exception() else None))

    # ── drawing ─────────────────────────────────────────────────────────────
    def _icon(self, surf, kind, x, cy):
        s = _s(16)
        y = cy - s // 2
        if kind == "folder":
            pygame.draw.rect(surf, (222, 178, 72), (x, y + s * 0.05, s * 0.45, s * 0.3), border_radius=3)
            pygame.draw.rect(surf, (244, 204, 104), (x, y + s * 0.2, s, s * 0.72), border_radius=4)
        elif kind == "drive":
            pygame.draw.rect(surf, (150, 160, 178), (x, y + s * 0.2, s, s * 0.6), border_radius=4)
            pygame.draw.rect(surf, (90, 98, 116), (x + 4, y + s * 0.56, s - 8, 3))
            pygame.draw.circle(surf, C_GREEN, (int(x + s - 6), int(y + s * 0.38)), 3)
        elif kind == "image":
            pygame.draw.rect(surf, (90, 150, 220), (x, y + 2, s, s - 4), border_radius=4)
            pygame.draw.polygon(surf, (240, 240, 250),
                                [(x + 3, y + s - 5), (x + s * 0.45, y + s * 0.4), (x + s * 0.78, y + s - 5)])
            pygame.draw.circle(surf, (255, 220, 90), (int(x + s - 6), int(y + 7)), 3)
        elif kind.startswith("place:"):
            name = kind[6:]
            col = {"Desktop": (90, 170, 220), "Documents": (150, 160, 178),
                   "Downloads": (77, 181, 108), "Pictures": (190, 110, 210)}.get(name, (150, 160, 178))
            pygame.draw.rect(surf, col, (x, y, s, s), border_radius=5)
            w = (255, 255, 255)
            if name == "Desktop":                      # little monitor
                pygame.draw.rect(surf, w, (x + 3, y + 4, s - 6, s * 0.45), 2, border_radius=2)
                pygame.draw.line(surf, w, (x + s // 2, y + s * 0.62), (x + s // 2, y + s - 4), 2)
                pygame.draw.line(surf, w, (x + 5, y + s - 4), (x + s - 5, y + s - 4), 2)
            elif name == "Documents":                  # page with lines
                pygame.draw.rect(surf, w, (x + 4, y + 3, s - 8, s - 6), 2, border_radius=2)
                for k in (0.38, 0.55, 0.72):
                    pygame.draw.line(surf, w, (x + 7, y + s * k), (x + s - 7, y + s * k), 1)
            elif name == "Downloads":                  # down arrow on a tray
                pygame.draw.line(surf, w, (x + s // 2, y + 3), (x + s // 2, y + s * 0.62), 2)
                pygame.draw.polygon(surf, w, [(x + s // 2, y + s * 0.72), (x + 4, y + s * 0.42),
                                              (x + s - 4, y + s * 0.42)])
                pygame.draw.line(surf, w, (x + 3, y + s - 3), (x + s - 3, y + s - 3), 2)
            else:                                      # Pictures: mountain + sun
                pygame.draw.polygon(surf, w, [(x + 3, y + s - 4), (x + s * 0.42, y + s * 0.42),
                                              (x + s * 0.7, y + s - 4)])
                pygame.draw.circle(surf, w, (int(x + s * 0.72), int(y + s * 0.3)), max(2, s // 8))
        elif kind == "up":
            pygame.draw.polygon(surf, C_TEXT_DIM, [(x + s // 2, y + 1), (x + s - 2, y + s // 2),
                                                   (x + 2, y + s // 2)])
            pygame.draw.rect(surf, C_TEXT_DIM, (x + s // 2 - 3, y + s // 2, 6, s // 2 - 1))

    def _row(self, surf, r, text, kind, sel, focused, info="", dim=False):
        if sel:
            if focused:
                draw_rounded_rect(surf, C_ACCENT, r, radius=_s(7), alpha=70)
                pygame.draw.rect(surf, C_ACCENT, r, 2, border_radius=_s(7))
            else:
                pygame.draw.rect(surf, C_ACCENT, (r.x, r.y + _s(5), _s(3), r.h - _s(10)), border_radius=2)
        self._icon(surf, kind, r.x + _s(10), r.centery)
        it = self.fonts["hint"].render(info, True, C_ACCENT2 if sel else C_TEXT_DIM) if info else None
        room = r.w - _s(46) - (it.get_width() + _s(16) if it else 0)
        t = self.fonts["ui"].render(fit_text(self.fonts["ui"], text, room), True,
                                    C_TEXT_DIM if dim else (C_WHITE if sel else C_TEXT))
        surf.blit(t, (r.x + _s(36), r.centery - t.get_height() // 2))
        if it:
            surf.blit(it, (r.right - it.get_width() - _s(10), r.centery - it.get_height() // 2))

    def _crumbs(self):
        if self.path is None:
            return ["This PC"]
        p = self.path.replace("/", "\\") if sys.platform == "win32" else self.path
        sep = "\\" if sys.platform == "win32" else "/"
        parts = [x for x in p.split(sep) if x]
        if sys.platform != "win32":
            parts = ["/"] + parts
        return parts or [p]

    def _hints(self):
        cancel = ("VIEW", "Cancel") if _input_mode != "kbd" else ("START", "Cancel")
        if self.focus == "drives":
            return [("A", "Open"), ("B", "Back to list"), cancel]
        it = self._cur()
        # On the drive list B also cancels — show it once, next to VIEW / Esc
        back = [("B", "Up"), cancel] if self.path is not None else [("B", ""), cancel]
        on_up = bool(it) and it["kind"] == "up"
        if self.mode == "image":
            if on_up:                                   # A and B both go up: one label
                return [("A", ""), ("B", "Up"), cancel]
            return [("A", "Use image" if it and it["kind"] == "image" else "Open")] + back
        if on_up:
            return [("Y", "Use this folder"), ("A", ""), ("B", "Up"), cancel]
        hints = [("A", "Open")]
        if (it and it["kind"] in ("drive", "folder")) or self.path is not None:
            hints.append(("Y", "Use this folder"))
        return hints + back

    def draw(self, surf):
        self._poll_drives()
        L = self._layout()
        ov = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ov.fill((8, 10, 14, 200))
        surf.blit(ov, (0, 0))
        rect = L["rect"]
        draw_panel(surf, rect, _s(14))
        draw_panel_header(surf, self.fonts, rect, L["hh"], self.title)
        draw_panel_footer(surf, self.fonts["hint"], rect, L["fh"], self._hints())
        top, bottom = L["top"], L["bottom"]

        # drives column
        dx = rect.x + _s(14)
        surf.blit(self.fonts["hint"].render("PLACES", True, C_TEXT_DIM), (dx + _s(8), top))
        y = top + _s(26)
        here = self._column_current() if self.path is not None else None
        n_drv = len(self.drives or [])
        if self.drives is None:
            lt = self.fonts["hint"].render("Loading drives\u2026", True, C_TEXT_DIM)
            surf.blit(lt, (dx + _s(8), y))
            y += self.PITCH
        for i, (_pth, name, icon) in enumerate(self._column()):
            if i == n_drv and i > 0:                   # divider between drives and folders
                pygame.draw.line(surf, PANEL_DIV, (dx + _s(8), y + _s(4)), (dx + L["lw"] - _s(8), y + _s(4)))
                y += _s(10)
            if y + self.ROW_H > bottom:
                break
            r = pygame.Rect(dx, y, L["lw"], self.ROW_H)
            if self.focus == "drives":
                self._row(surf, r, name, icon, i == self.dcursor, True)
            else:
                self._row(surf, r, name, icon, i == here, False)
            y += self.PITCH
        pygame.draw.line(surf, PANEL_DIV, (dx + L["lw"] + _s(10), top), (dx + L["lw"] + _s(10), bottom))

        # breadcrumb (drop leading parts if too long)
        lx, rw = L["lx"], L["rw"] + (L["prev_w"] + _s(14) if L["prev_w"] else 0)
        parts = self._crumbs()
        f, sep = self.fonts["tab"], "  ›  "
        def width(ps):
            return sum(f.size(x)[0] for x in ps) + f.size(sep)[0] * (len(ps) - 1)
        shown = parts[:]
        while len(shown) > 1 and width(shown if shown == parts else ["…"] + shown) > rw:
            shown = shown[1:]
        if shown != parts:
            shown = ["…"] + shown
        x = lx
        for i, part in enumerate(shown):
            last = i == len(shown) - 1
            t = f.render(fit_text(f, part, rw) if last else part, True, C_ACCENT2 if last else C_TEXT_DIM)
            surf.blit(t, (x, top))
            x += t.get_width()
            if not last:
                st = f.render(sep, True, C_TEXT_DIM)
                surf.blit(st, (x, top))
                x += st.get_width()

        # list
        y = L["list_top"]
        if self.path is None and self.drives is None:
            lt = self.fonts["ui"].render("Looking for drives…", True, C_TEXT_DIM)
            surf.blit(lt, (lx + _s(10), y))
        elif self.error:
            lt = self.fonts["ui"].render(self.error, True, C_RED)
            surf.blit(lt, (lx + _s(10), y + self.PITCH))
        if self.path is not None and len(self.items) <= 1 and not self.error:
            msg = "No folders here" if self.mode == "folder" else "No folders or images here"
            lt = self.fonts["hint"].render(msg, True, C_TEXT_DIM)
            surf.blit(lt, (lx + _s(36), y + self.PITCH + _s(6)))
        rows = L["rows"]
        for i in range(self.start, min(len(self.items), self.start + rows)):
            it  = self.items[i]
            r   = pygame.Rect(lx, y + (i - self.start) * self.PITCH, L["rw"], self.ROW_H)
            sel = i == self.cursor and self.focus == "list"
            info = it["info"]
            if sel and self.mode == "folder" and it["kind"] in ("folder", "drive"):
                c = self._counts.get(it["path"])
                if isinstance(c, int):
                    info = f"{c} shortcut{'s' if c != 1 else ''}" if c else "no shortcuts"
                elif c:
                    info = "…"
            self._row(surf, r, it["name"], it.get("icon", it["kind"]), sel, True, info,
                      dim=it["kind"] == "up")
        if self.start > 0 or self.start + rows < len(self.items):
            vis_h = rows * self.PITCH
            sbx = lx + L["rw"] + _s(4)
            pygame.draw.rect(surf, C_GRAY, (sbx, y, _s(3), vis_h), border_radius=2)
            th = max(_s(16), int(vis_h * rows / len(self.items)))
            ty = y + int((vis_h - th) * self.start / max(1, len(self.items) - rows))
            pygame.draw.rect(surf, C_ACCENT, (sbx, ty, _s(3), th), border_radius=2)

        if L["note_h"]:
            nr = pygame.Rect(lx, bottom - _s(32), L["rw"], _s(30))
            draw_rounded_rect(surf, C_GREEN, nr, radius=_s(7), alpha=35)
            pygame.draw.rect(surf, C_GREEN, nr, 1, border_radius=_s(7))
            yb = btn_text("Y")
            nt = self.fonts["hint"].render(fit_text(self.fonts["hint"],
                 f"{yb} picks the highlighted folder — on “Up one level”, the folder you’re in",
                 nr.w - _s(24)), True, C_WHITE)
            surf.blit(nt, (nr.x + _s(12), nr.centery - nt.get_height() // 2))

        # image preview
        if L["prev_w"]:
            pw_ = L["prev_w"]
            pr  = pygame.Rect(rect.right - _s(14) - pw_, L["list_top"], pw_, int(pw_ * 9 / 16))
            self._update_side_info(pr.size)
            it  = self._cur()
            pv  = self._prev.get(it["path"]) if it and it["kind"] == "image" else None
            pygame.draw.rect(surf, PANEL_BOT, pr)
            if isinstance(pv, tuple):
                surf.blit(pv[0], pr)
            else:
                msg = ("Loading…" if pv == "…" else
                       "Can’t show this image" if it and it["kind"] == "image" else "Pick an image")
                lt = self.fonts["hint"].render(msg, True, C_TEXT_DIM)
                surf.blit(lt, lt.get_rect(center=pr.center))
            pygame.draw.rect(surf, PANEL_BORDER, pr, 1)
            if it and it["kind"] == "image":
                facts = [("Type", os.path.splitext(it["name"])[1].lstrip(".").upper()),
                         ("File size", it["info"])]
                if isinstance(pv, tuple):
                    facts.insert(0, ("Size", f"{pv[1][0]} × {pv[1][1]}"))
                if it.get("mtime"):
                    facts.append(("Modified", time.strftime("%d %b %Y", time.localtime(it["mtime"]))))
                yy = pr.bottom + _s(10)
                for k, v in facts:
                    surf.blit(self.fonts["hint"].render(k, True, C_TEXT_DIM), (pr.x, yy))
                    vt = self.fonts["hint"].render(v, True, C_TEXT)
                    surf.blit(vt, (pr.right - vt.get_width(), yy))
                    yy += _s(22)
        else:
            self._update_side_info((1, 1))


# ── Bluetooth controller pairing (no keyboard needed) ─────────────────────────
# Uses Windows' own pairing (Windows.Devices.Enumeration — optional package
# "winrt-Windows.Devices.Enumeration"; "winrt-Windows.Devices.Radios" to switch
# Bluetooth on). Only devices that look like game controllers are paired, and
# Windows' "Pair?" question is answered by GameClub — so it works with no keyboard.
_PAD_NAME_RE = re.compile(r"controller|gamepad|joy-?con|8bitdo|gamesir|dualsense|dualshock|"
                          r"xbox|joystick|\bpad\b", re.IGNORECASE)
_NOT_PAD_RE  = re.compile(r"headset|headphone|earbud|buds|speaker|keyboard|mouse|watch|"
                          r"phone|tv\b|remote", re.IGNORECASE)
_BT_CLASSIC  = "{e0cbf06c-cd8b-4647-bb8a-263b43f0f974}"
_BT_LE       = "{bb7bb05e-5972-42b5-94fc-76eaa7084d49}"


def looks_like_controller(name: str) -> bool:
    return bool(name) and bool(_PAD_NAME_RE.search(name)) and not _NOT_PAD_RE.search(name)


_AUDIO_RE = re.compile(r"head ?phone|headset|ear ?bud|buds|airpods|earphone|\bwh-|\bwf-|"
                       r"jabra|bose|beats|soundcore|sennheiser|momentum|freebuds|\bqc ?\d|"
                       r"\btune \d|\blive \d|\belite\b", re.IGNORECASE)
_NOT_AUDIO_RE = re.compile(r"speaker|soundbar|boombox|\bflip\b|\bcharge\b|\bgo ?\d|controller|"
                           r"gamepad|keyboard|mouse|\bphone\b|watch|\btv\b|car\b", re.IGNORECASE)
# Bluetooth "class of device": major 4 = audio/video; minor 1 headset, 2 hands-free,
# 6 headphones (5 = loudspeaker, 8 = car audio… are left out on purpose)
_AEP_COD_MAJOR = "System.Devices.Aep.Bluetooth.Cod.Major"
_AEP_COD_MINOR = "System.Devices.Aep.Bluetooth.Cod.Minor"


def _aep_prop(info, key):
    try:
        props = info.properties
        return props.lookup(key) if props.has_key(key) else None
    except Exception:  # noqa: BLE001
        try:
            return info.properties[key]
        except Exception:  # noqa: BLE001
            return None


def looks_like_headphones(info) -> bool:
    """Headphones / headsets / earbuds only — not speakers, pads, phones…"""
    try:
        name = info.name or ""
    except Exception:  # noqa: BLE001
        return False
    major, minor = _aep_prop(info, _AEP_COD_MAJOR), _aep_prop(info, _AEP_COD_MINOR)
    if major is not None and int(major) != 0:
        return int(major) == 4 and int(minor or 0) in (1, 2, 6, 4, 8, 24) \
            and not _NOT_AUDIO_RE.search(name)
    return bool(_AUDIO_RE.search(name)) and not _NOT_AUDIO_RE.search(name)


def set_default_audio_output(endpoint_id: str) -> bool:
    """Make an audio endpoint Windows' default output (all roles) — the same call
    Windows' own sound menu uses (IPolicyConfig)."""
    import ctypes
    from ctypes import wintypes

    class GUID(ctypes.Structure):
        _fields_ = [("d1", ctypes.c_uint32), ("d2", ctypes.c_uint16),
                    ("d3", ctypes.c_uint16), ("d4", ctypes.c_ubyte * 8)]

    def guid(text):
        import uuid
        u = uuid.UUID(text)
        return GUID(u.time_low, u.time_mid, u.time_hi_version,
                    (ctypes.c_ubyte * 8).from_buffer_copy(u.bytes[8:]))
    ole = ctypes.windll.ole32
    ole.CoInitializeEx(None, 0)                      # fine if already initialised
    clsid = guid("870af99c-171d-4f9e-af0d-e63df40c2bc9")   # PolicyConfigClient
    iid   = guid("f8679f50-850a-41cf-9c72-430f290290c8")   # IPolicyConfig
    ptr   = ctypes.c_void_p()
    if ole.CoCreateInstance(ctypes.byref(clsid), None, 0x17, ctypes.byref(iid),
                            ctypes.byref(ptr)) != 0 or not ptr:
        return False
    vtbl = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))[0]
    set_default = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, wintypes.LPCWSTR,
                                     ctypes.c_int)(vtbl[13])
    release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtbl[2])
    try:
        return all(set_default(ptr, endpoint_id, role) == 0 for role in (0, 1, 2))
    finally:
        release(ptr)


class BluetoothPairing:
    """Background search + automatic pairing over Bluetooth.
    kind "controller": game controllers; kind "audio": headphones / headsets
    (and then sound is switched to them). The UI only reads .state / .device /
    .message (thread-safe enough)."""

    def __init__(self, log=lambda m: None, kind="controller"):
        self.kind    = kind
        self.state   = "starting"   # starting / searching / pairing / paired / failed /
        self.device  = ""           # bt_off / no_bt / unavailable / stopped
        self.message = ""
        self.paired_at = 0.0
        self._log    = log
        self._stop   = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        import asyncio
        try:
            asyncio.run(self._main())
        except ImportError:
            self.state = "unavailable"
            self._log("pairing: winrt Bluetooth packages not installed")
        except Exception as exc:  # noqa: BLE001
            self.state, self.message = "failed", str(exc)
            self._log(f"pairing: crashed ({exc!r})")

    async def _switch_sound(self, name):
        self.message = "Switching sound\u2026"
        try:
            out = await _switch_sound_to(name, self._log)
        except Exception as exc:  # noqa: BLE001
            self._log(f"pairing: sound switch failed ({exc!r})")
            out = ""
        self.message = ("Sound switched to them" if out
                        else "Paired \u2014 pick them in Windows' sound menu if you hear nothing")

    async def _bluetooth_on(self):
        """True if Bluetooth is (now) on. Switches it on if it was off."""
        try:
            from winrt.windows.devices.radios import Radio, RadioKind, RadioState
        except ImportError:
            return True                       # can't check — just try to search
        try:
            await Radio.request_access_async()
            radios = [r for r in await Radio.get_radios_async() if r.kind == RadioKind.BLUETOOTH]
        except Exception as exc:  # noqa: BLE001
            self._log(f"pairing: radio check failed ({exc!r})")
            return True
        if not radios:
            self.state = "no_bt"
            return False
        for r in radios:
            if r.state != RadioState.ON:
                self.state = "bt_off"
                self._log("pairing: Bluetooth was off -> switching it on")
                try:
                    await r.set_state_async(RadioState.ON)
                except Exception as exc:  # noqa: BLE001
                    self._log(f"pairing: couldn't switch Bluetooth on ({exc!r})")
                await asyncio_sleep(1.5)
                if r.state != RadioState.ON:
                    self.message = "Bluetooth is off — GameClub couldn't switch it on"
                    return False
        return True

    async def _main(self):
        from winrt.windows.devices.enumeration import (DeviceInformation,
                                                       DeviceInformationKind,
                                                       DevicePairingKinds,
                                                       DevicePairingResultStatus)
        import asyncio
        loop = asyncio.get_running_loop()
        while not await self._bluetooth_on():
            if self._stop.is_set():
                return
            await asyncio.sleep(3)
        found = asyncio.Queue()
        seen  = {}                               # device id -> time of last attempt

        def added(_w, info):
            try:
                name = info.name or ""
            except Exception:  # noqa: BLE001
                return
            ok = looks_like_headphones(info) if self.kind == "audio" else looks_like_controller(name)
            if ok:
                loop.call_soon_threadsafe(found.put_nowait, info)

        watchers = []
        unpaired = "System.Devices.Aep.IsPaired:=System.StructuredQueryType.Boolean#False"
        for proto, extra in ((_BT_CLASSIC, " AND System.Devices.Aep.Bluetooth.IssueInquiry:="
                                           "System.StructuredQueryType.Boolean#True"),
                             (_BT_LE, "")):
            aqs = f'System.Devices.Aep.ProtocolId:="{proto}" AND {unpaired}{extra}'
            props = [_AEP_COD_MAJOR, _AEP_COD_MINOR] if self.kind == "audio" else []
            try:
                w = DeviceInformation.create_watcher(aqs, props,
                                                     DeviceInformationKind.ASSOCIATION_ENDPOINT)
            except Exception:  # noqa: BLE001  (older Windows: no class-of-device props)
                w = DeviceInformation.create_watcher(aqs, [],
                                                     DeviceInformationKind.ASSOCIATION_ENDPOINT)
            w.add_added(added)
            w.add_updated(lambda _w, _u: None)
            w.add_removed(lambda _w, _u: None)
            w.start()
            watchers.append(w)
        self.state = "searching"
        self._log(f"pairing: searching for Bluetooth {'headphones' if self.kind == 'audio' else 'controllers'}")
        try:
            while not self._stop.is_set():
                try:
                    info = await asyncio.wait_for(found.get(), 0.5)
                except asyncio.TimeoutError:
                    continue
                if time.time() - seen.get(info.id, 0) < 15:
                    continue
                seen[info.id] = time.time()
                self.state, self.device = "pairing", info.name
                self._log(f"pairing: found '{info.name}' -> pairing")
                custom = info.pairing.custom

                def requested(_s, args):
                    try:                          # answer Windows' question ourselves
                        if args.pairing_kind == DevicePairingKinds.PROVIDE_PIN:
                            args.accept("0000")   # old pads that ask for a PIN use 0000
                        else:
                            args.accept()         # "Pair?" / "Does the PIN match?" → yes
                    except Exception as exc:  # noqa: BLE001
                        self._log(f"pairing: couldn't answer Windows ({exc!r})")
                custom.add_pairing_requested(requested)
                kinds = (DevicePairingKinds.CONFIRM_ONLY | DevicePairingKinds.DISPLAY_PIN |
                         DevicePairingKinds.PROVIDE_PIN | DevicePairingKinds.CONFIRM_PIN_MATCH)
                try:
                    res = await custom.pair_async(kinds)
                    ok = res.status in (DevicePairingResultStatus.PAIRED,
                                        DevicePairingResultStatus.ALREADY_PAIRED)
                except Exception as exc:  # noqa: BLE001
                    ok, res = False, exc
                if ok:
                    self._log(f"pairing: '{info.name}' paired")
                    if self.kind == "audio":
                        await self._switch_sound(info.name)
                    self.state, self.paired_at = "paired", time.time()
                    return
                self.state = "failed"
                self.message = f"Couldn't pair {info.name} — put it in pairing mode again"
                self._log(f"pairing: '{info.name}' failed ({getattr(res, 'status', res)})")
                await asyncio.sleep(3)
                self.state = "searching"
        finally:
            for w in watchers:
                try:
                    w.stop()
                except Exception:  # noqa: BLE001
                    pass
            if self.state not in ("paired",):
                self.state = "stopped" if self._stop.is_set() else self.state


async def _switch_sound_to(name, log, wait=15.0):
    """After pairing headphones: wait for their sound output to appear, then make
    it the default. Returns the output's name, or "" if it didn't work."""
    import asyncio
    from winrt.windows.devices.enumeration import DeviceInformation
    aqs = ('System.Devices.InterfaceClassGuid:="{e6327cad-dcec-4949-ae8a-991e976a79d2}" AND '
           'System.Devices.InterfaceEnabled:=System.StructuredQueryType.Boolean#True')
    want = [w for w in re.split(r"[\s()]+", name.lower()) if len(w) > 2]
    end = time.time() + wait
    while time.time() < end:
        try:
            outs = list(await DeviceInformation.find_all_async(aqs))
        except Exception as exc:  # noqa: BLE001
            log(f"pairing: listing sound outputs failed ({exc!r})")
            return ""
        best = None
        for d in outs:
            dn = (d.name or "").lower()
            if want and all(w in dn for w in want):
                if "hands-free" not in dn and "headset" not in dn:
                    best = d                      # stereo "Headphones (…)" — the good one
                    break
                best = best or d
        if best is not None:
            m = re.search(r"\{0\.0\.0\.00000000\}\.\{[0-9a-fA-F-]+\}", best.id or "")
            if m and set_default_audio_output(m.group(0)):
                log(f"pairing: sound switched to '{best.name}'")
                return best.name
            log(f"pairing: couldn't switch sound to '{best.name}'")
            return ""
        await asyncio.sleep(1.0)
    log("pairing: no sound output appeared for the headphones")
    return ""


async def asyncio_sleep(sec):
    import asyncio
    await asyncio.sleep(sec)



class SettingsScreen:
    OPTIONS = [
        ("Shortcuts Folder", "start_folder",  "path"),
        ("SteamGridDB Key","sgdb_api_key", "path"),
        ("Scan Subfolders", "scan_subfolders", "bool"),
        ("Start with Windows", "startup_with_windows", "bool"),
        ("Controller on UAC & Sign-in", "secure_desktop", "bool"),
        ("Button Style",  "button_style",  "choice", ["Xbox", "PlayStation", "Nintendo"]),
        ("Accent Colour", "accent",        "choice", list(ACCENTS)),
        ("Background",    "background",    "choice", ["Solid", "Wallpaper"]),
        ("Wallpaper Image", "wallpaper",   "path"),
        ("Wallpaper Blur", "wallpaper_blur", "choice", ["Off", "Light", "Medium", "Strong"]),
        ("Sort Apps",      "sort_apps",      "choice", SORT_MODES),
        ("Sort PC Games",  "sort_pc_games",  "choice", SORT_MODES),
        ("Sort Emulation", "sort_emulation", "choice", SORT_MODES),
        ("Desktop Mouse",       "desktop_mouse", "bool"),
        ("Pointer Speed", "mouse_speed",  "choice", list(range(1, 11))),
        ("Acceleration",  "mouse_accel",  "choice", list(range(1, 11))),
        ("Wheel Speed",   "mouse_scroll", "choice", list(range(1, 11))),
        ("Pointer Stick",  "mouse_stick",  "choice", ["Right stick", "Left stick"]),
        ("Clicks",         "mouse_clicks", "choice", ["RT left \u00b7 LT right", "LT left \u00b7 RT right"]),
        ("Keyboard Position",   "osk_pos",      "choice", ["Bottom", "Top"]),
        ("Icon Size",     "icon_size",     "choice", [64, 80, 100, 120, 150, 170, 190, 200]),
        ("Columns",       "columns",       "choice", [4, 5, 6, 7, 8]),
        ("Scroll Speed",  "scroll_speed",  "choice", ["Slow", "Normal", "Fast"]),
    ]

    def __init__(self, config, fonts, width, height):
        self.config     = config.copy()
        self.fonts      = fonts
        self.width      = width
        self.height     = height
        self.cursor      = 0
        self.scroll_y    = 0.0
        self.target_sy   = 0.0
        self.editing     = False
        self.editing_key = "start_folder"
        self.path_input  = self.config["start_folder"]
        self.kbd         = None    # on-screen keyboard while editing with a controller
        self.picker      = None    # FilePicker for Shortcuts Folder / Wallpaper Image
        self._edit_t     = 0.0

    # Two pages: GameClub's own settings, and the controller-as-mouse outside GameClub
    PAGES      = ("GameClub", "Desktop & Mouse")
    MOUSE_KEYS = {"desktop_mouse", "mouse_speed", "mouse_accel", "mouse_scroll",
                  "mouse_stick", "mouse_clicks", "osk_pos"}

    def _page_opts(self, page):
        return [o for o in self.OPTIONS if (o[1] in self.MOUSE_KEYS) == (page == 1)]

    def _opts(self):
        return self._page_opts(getattr(self, "page", 0))

    def switch_page(self, step):
        cur = getattr(self, "page_cursor", {0: 0, 1: 0})
        cur[getattr(self, "page", 0)] = self.cursor
        self.page = (getattr(self, "page", 0) + step) % len(self.PAGES)
        self.page_cursor = cur
        self.cursor = cur.get(self.page, 0)
        self.scroll_y = self.target_sy = 0.0
        self._scroll_to_settings_cursor()
        self.scroll_y = self.target_sy

    PICKABLE = {"start_folder": ("folder", "Choose Shortcuts Folder"),
                "wallpaper":    ("image",  "Choose Wallpaper Image")}

    def busy(self):
        """Typing or browsing — LB/RB must not switch tabs."""
        return self.editing or self.picker is not None

    def _begin_edit(self, key):
        self.editing_key = key
        self.editing     = True
        self.path_input  = self.config.get(key, "")
        self._edit_t     = time.time()
        pygame.event.set_grab(False)   # release grab so keyboard works
        pygame.key.start_text_input()
        if _input_mode != "kbd":       # using the controller: show the keyboard
            self.kbd = {"sel": [1, 0], "shift": False, "error": ""}

    def _picker_result(self, res):
        if res == "cancel":
            self.picker = None
        elif isinstance(res, tuple) and res[0] == "pick":
            key = self.picker_key
            self.config[key] = res[1]
            if key == "wallpaper" and self.config.get("background") != "Wallpaper":
                self.config["background"] = "Wallpaper"     # picking one means "use it"
            self.picker = None

    # ── editing helpers (shared by keyboard and controller) ──────────────────
    def _commit_edit(self):
        """Store the typed value. Returns False (and keeps editing) if a folder
        doesn't exist."""
        if self.editing_key == "start_folder":
            if not os.path.isdir(self.path_input):
                return False
            self.config["start_folder"] = self.path_input
        else:
            self.config[self.editing_key] = self.path_input.strip()
        self._end_edit()
        return True

    def _cancel_edit(self):
        self.path_input = self.config.get(self.editing_key, "")
        self._end_edit()

    def _end_edit(self):
        self.editing = False
        self.kbd     = None
        pygame.key.stop_text_input()
        pygame.event.set_grab(True)

    def _edit_label(self):
        return next(o[0] for o in self.OPTIONS if o[1] == self.editing_key)

    # ── on-screen keyboard (controller) ─────────────────────────────────────
    def _kbd_layout(self):
        kw   = min(self.width - _s(40), _s(900))
        unit = (kw - _s(32)) / SETTINGS_OSK_UNITS
        kh   = int(min(unit * 0.86, _s(40), self.height * 0.052))
        gap  = _s(5)
        field_h, hints_h = _s(56), _s(40)
        kht  = _s(10) + field_h + len(SETTINGS_OSK_ROWS) * (kh + gap) + hints_h
        kx   = (self.width - kw) // 2
        ky   = self.height - kht - _s(14)
        rows, y = [], ky + _s(10) + field_h
        for row in SETTINGS_OSK_ROWS:
            x = kx + (kw - sum(k["w"] for k in row) * unit) / 2
            out = []
            for k in row:
                w = k["w"] * unit
                out.append((pygame.Rect(int(x + gap / 2), y, int(w - gap), kh), k))
                x += w
            rows.append(out)
            y += kh + gap
        return pygame.Rect(kx, ky, kw, kht), rows, field_h

    def _kbd_move(self, dx, dy):
        r, c = self.kbd["sel"]
        rows = SETTINGS_OSK_ROWS
        if dx:
            c = (c + dx) % len(rows[r])
        if dy:
            _rect, lay, _f = self._kbd_layout()
            cx = lay[r][c][0].centerx
            r  = (r + dy) % len(rows)
            c  = min(range(len(lay[r])), key=lambda i: abs(lay[r][i][0].centerx - cx))
        self.kbd["sel"] = [r, c]

    def _kbd_press(self, key):
        k, sh = key["kind"], self.kbd["shift"]
        self.kbd["error"] = ""
        if k == "char":
            self.path_input += key["s"] if sh else key["n"]
        elif k == "space":
            self.path_input += " "
        elif k == "bksp":
            self.path_input = self.path_input[:-1]
        elif k == "shift":
            self.kbd["shift"] = not sh
        elif k == "paste":
            self.path_input += clipboard_text()
        elif k == "done":
            self._kbd_done()

    def _kbd_done(self):
        if not self._commit_edit():
            self.kbd["error"] = "Folder not found \u2014 check the path"

    def _kbd_button(self, btn):
        if btn in ("up", "down", "left", "right"):
            self._kbd_move(*{"left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1)}[btn])
        elif btn == "A":
            r, c = self.kbd["sel"]
            self._kbd_press(SETTINGS_OSK_ROWS[r][c])
        elif btn == "B":
            self.path_input = self.path_input[:-1]
        elif btn == "X":
            self.path_input += " "
        elif btn == "Y":
            self.kbd["shift"] = not self.kbd["shift"]
        elif btn == "start":
            self._kbd_done()
        elif btn == "back":
            self._cancel_edit()
        return None

    def _kbd_draw(self, surf):
        ov = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ov.fill((8, 10, 14, 150))
        surf.blit(ov, (0, 0))
        rect, rows, field_h = self._kbd_layout()
        draw_panel(surf, rect, _s(16))
        pygame.draw.rect(surf, C_ACCENT, rect, width=2, border_radius=_s(16))
        # field preview: label + what's typed (the API key stays hidden)
        label = self._edit_label()
        is_api = self.editing_key == "sgdb_api_key"
        text = ("*" * len(self.path_input) if is_api else self.path_input) + "|"
        fr = pygame.Rect(rect.x + _s(16), rect.y + _s(10), rect.w - _s(32), field_h - _s(10))
        pygame.draw.rect(surf, BTN_KEYCAP_BG, fr, border_radius=_s(8))
        pygame.draw.rect(surf, BTN_KEYCAP_BORDER, fr, width=1, border_radius=_s(8))
        lt = self.fonts["hint"].render(label, True, C_ACCENT2)
        surf.blit(lt, (fr.x + _s(12), fr.centery - lt.get_height() // 2))
        tx = fr.x + _s(24) + lt.get_width()
        tt = self.fonts["path"].render(fit_text(self.fonts["path"], text[-200:], fr.right - tx - _s(12))
                                       if self.fonts["path"].size(text)[0] <= fr.right - tx - _s(12)
                                       else "\u2026" + text[-60:], True, C_WHITE)
        tt_w = min(tt.get_width(), fr.right - tx - _s(12))
        surf.blit(tt, (fr.right - _s(12) - tt_w, fr.centery - tt.get_height() // 2),
                  area=pygame.Rect(tt.get_width() - tt_w, 0, tt_w, tt.get_height()))
        sh = self.kbd["shift"]
        for r, row in enumerate(rows):
            for c, (kr, k) in enumerate(row):
                sel = [r, c] == self.kbd["sel"]
                on  = k["kind"] == "shift" and sh
                pygame.draw.rect(surf, BTN_KEYCAP_BG, kr, border_radius=_s(7))
                if sel or on:
                    draw_rounded_rect(surf, C_ACCENT, kr, radius=_s(7), alpha=90 if sel else 45)
                pygame.draw.rect(surf, C_ACCENT if sel else BTN_KEYCAP_BORDER, kr,
                                 width=2 if sel else 1, border_radius=_s(7))
                lab = (k["s"] if sh else k["n"]) if k["kind"] == "char" else k["label"]
                t = (self.fonts["ui"] if k["kind"] == "char" else self.fonts["hint"]).render(
                    lab, True, C_WHITE if sel else C_TEXT)
                surf.blit(t, t.get_rect(center=kr.center))
        hy = rect.bottom - _s(22)
        if self.kbd.get("error"):
            et = self.fonts["hint"].render(self.kbd["error"], True, C_RED)
            surf.blit(et, et.get_rect(center=(rect.centerx, hy)))
        else:
            hints = [("A", "Type"), ("B", "Delete"), ("X", "Space"), ("Y", "Shift"),
                     ("START", "Done"), ("VIEW", "Cancel")]
            hw = hints_width(self.fonts["hint"], hints)
            draw_hints(surf, self.fonts["hint"], hints, rect.centerx - hw // 2, hy)

    def handle_key(self, event):
        if not self.editing:
            return
        if event.key == pygame.K_RETURN:
            if not self._commit_edit() and self.kbd is not None:
                self.kbd["error"] = "Folder not found \u2014 check the path"
            elif self.editing:          # keyboard user, folder missing: keep old value
                self._cancel_edit()
        elif event.key == pygame.K_ESCAPE:
            self._cancel_edit()
        elif event.key == pygame.K_BACKSPACE:
            self.path_input = self.path_input[:-1]
        elif event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
            self.path_input += clipboard_text()

    def handle_text_input(self, text):
        if self.editing:
            # X (type path) starts editing — its own letter arrives as text right after
            swallow, self._swallow_x = getattr(self, "_swallow_x", False), False
            if swallow and text in ("x", "X") and time.time() - self._edit_t < 1.0:
                return
            self.path_input += text

    def handle_button(self, btn):
        if self.picker is not None:
            self._picker_result(self.picker.handle_button(btn))
            return None
        if self.editing and self.kbd is not None:
            return self._kbd_button(btn)       # controller keyboard is open
        if self.editing:
            # Auto-confirm current field before processing button
            if btn == "start":
                self._commit_edit() or self._cancel_edit()
                return "save"
            return None
        if btn == "B":
            return "back"
        if btn == "start":
            return "save"
        if btn in ("LT", "RT"):
            self.switch_page(-1 if btn == "LT" else 1)
            return None
        opts = self._opts()
        if btn == "up":
            self.cursor = (self.cursor - 1) % len(opts)
            self._scroll_to_settings_cursor()
        if btn == "down":
            self.cursor = (self.cursor + 1) % len(opts)
            self._scroll_to_settings_cursor()
        if btn in ("left", "right"):
            self._adjust(-1 if btn == "left" else 1)
        opt = opts[self.cursor]
        if btn == "A" and opt[1] in self.PICKABLE:
            mode, title = self.PICKABLE[opt[1]]
            self.picker     = FilePicker(mode, title, self.fonts, self.width, self.height)
            self.picker_key = opt[1]
        elif btn in ("A", "X") and opt[2] == "path":
            self._begin_edit(opt[1])       # type it (SteamGridDB key, or X = type a path)
            self._swallow_x = btn == "X" and _input_mode == "kbd"
        elif btn == "A" and opt[2] == "bool":
            self._adjust(1)
        return None

    def _adjust(self, direction):
        opt = self._opts()[self.cursor]
        key = opt[1]
        if opt[2] == "bool":
            self.config[key] = not self.config[key]
        elif opt[2] == "choice":
            vals = opt[3]
            cur  = self.config[key]
            idx  = vals.index(cur) if cur in vals else 0
            self.config[key] = vals[(idx + direction) % len(vals)]

    ROW_H    = _s(54)      # row pitch (row height + gap)
    ROW_GAP  = _s(6)
    HEADER_H = _s(64)
    FOOTER_H = _s(52)
    BODY_PAD = _s(14)      # space between divider and first/last row

    def _layout(self):
        """Panel geometry shared by drawing and scrolling."""
        pw         = min(_s(700), self.width - _s(80))
        content_h  = len(self._opts()) * self.ROW_H - self.ROW_GAP
        # panel height from the longer page, so it doesn't jump when switching
        tallest    = max(len(self._page_opts(p)) for p in range(len(self.PAGES)))
        full_h     = tallest * self.ROW_H - self.ROW_GAP
        top_margin = App.TOPBAR_H + App.TABBAR_H + _s(20)
        bot_margin = App.BOTTOMBAR_H + _s(20)
        max_ph     = self.height - top_margin - bot_margin
        chrome     = self.HEADER_H + self.FOOTER_H + self.BODY_PAD * 2
        ph         = min(chrome + full_h, max_ph)
        vis_h      = ph - chrome
        px         = (self.width - pw) // 2
        py         = top_margin + (max_ph - ph) // 2
        return px, py, pw, ph, vis_h, content_h

    def _scroll_to_settings_cursor(self):
        *_, vis_h, _content_h = self._layout()
        item_top = self.cursor * self.ROW_H
        item_bot = item_top + self.ROW_H - self.ROW_GAP
        if item_top < self.target_sy:
            self.target_sy = float(item_top)
        elif item_bot > self.target_sy + vis_h:
            self.target_sy = float(item_bot - vis_h)

    def draw(self, surf):
        px, py, pw, ph, vis_h, content_h = self._layout()
        rect = (px, py, pw, ph)
        self.scroll_y += (self.target_sy - self.scroll_y) * 0.18

        draw_panel(surf, rect, _s(18))
        # header: the two pages as tabs, with LT / RT on either side
        page = getattr(self, "page", 0)
        tw, th = min(_s(230), (pw - _s(150)) // 2), _s(36)
        tx = px + (pw - 2 * tw - _s(10)) // 2
        ty = py + (self.HEADER_H - th) // 2
        for i, label in enumerate(self.PAGES):
            tr = pygame.Rect(tx + i * (tw + _s(10)), ty, tw, th)
            draw_tab(surf, tr, i == page)
            lt = self.fonts["tab"].render(label, True, C_WHITE if i == page else C_TEXT_DIM)
            surf.blit(lt, lt.get_rect(center=tr.center))
        for btn, x in (("LT", tx - _s(12)), ("RT", tx + 2 * tw + _s(10) + _s(12))):
            bw = _btn_size(self.fonts["hint"], btn)[0]
            draw_button(surf, self.fonts["hint"], btn, x - bw if btn == "LT" else x, ty + th // 2)
        pygame.draw.line(surf, PANEL_DIV, (px + _s(20), py + self.HEADER_H),
                         (px + pw - _s(20), py + self.HEADER_H))

        body_top  = py + self.HEADER_H + self.BODY_PAD
        clip_rect = pygame.Rect(px + 2, body_top - _s(4), pw - 4, vis_h + _s(8))
        surf.set_clip(clip_rect)
        row_h = self.ROW_H - self.ROW_GAP
        for i, opt in enumerate(self._opts()):
            oy = body_top + i * self.ROW_H - int(self.scroll_y)
            if oy + row_h < clip_rect.top or oy > clip_rect.bottom:
                continue
            sel = i == self.cursor
            rr  = pygame.Rect(px + _s(16), oy, pw - _s(32), row_h)
            if sel:
                draw_row_highlight(surf, rr, C_ACCENT)
            mid = rr.centery
            lbl = self.fonts["ui"].render(opt[0], True, C_WHITE if sel else C_TEXT)
            surf.blit(lbl, (rr.x + _s(24), mid - lbl.get_height() // 2))
            key   = opt[1]
            val   = self.config[key]
            right = rr.right - _s(20)
            if opt[2] == "bool":
                on   = bool(val)
                vt   = self.fonts["hint"].render("ON" if on else "OFF", True,
                                                 C_GREEN if on else C_RED)
                pill = vt.get_rect(midright=(right, mid)).inflate(_s(18), _s(8))
                pill.right = right
                draw_rounded_rect(surf, C_GREEN if on else C_RED, pill,
                                  radius=pill.height // 2, alpha=40)
                surf.blit(vt, vt.get_rect(center=pill.center))
            elif opt[2] == "path":
                is_api = key == "sgdb_api_key"
                if self.editing and sel:
                    raw     = self.path_input + "|"
                    display = ("*" * max(0, len(raw) - 1) + "|") if is_api else raw
                else:
                    raw     = str(val)
                    display = ("*" * min(len(raw), 8) + "..." if raw else "Not set") if is_api \
                              else (raw or "Not set")
                if len(display) > 44:
                    display = "…" + display[-42:]
                txt_col = C_YELLOW if not str(val) else C_ACCENT2
                vt = self.fonts["path"].render(display, True, txt_col)
                surf.blit(vt, (right - vt.get_width(), mid - vt.get_height() // 2))
            elif opt[2] == "choice":
                vt   = self.fonts["ui"].render(str(val), True, C_YELLOW)
                acol = C_ACCENT2 if sel else C_GRAY
                draw_triangle_right(surf, right - _s(6), mid, _s(14), acol)
                vx = right - _s(22) - vt.get_width()
                surf.blit(vt, (vx, mid - vt.get_height() // 2))
                draw_triangle_left(surf, vx - _s(16), mid, _s(14), acol)
        surf.set_clip(None)

        if content_h > vis_h:
            sbx = px + pw - _s(8)
            pygame.draw.rect(surf, C_GRAY, (sbx, body_top, _s(3), vis_h), border_radius=2)
            th = max(_s(20), int(vis_h * vis_h / content_h))
            ty = body_top + int((self.scroll_y / max(1, content_h - vis_h)) * (vis_h - th))
            pygame.draw.rect(surf, C_ACCENT, (sbx, ty, _s(3), th), border_radius=2)

        if self._opts()[self.cursor][1] in self.PICKABLE and not self.editing:
            foot = [("A", "Browse"), ("X", "Type path"), ("B", "Back"), ("START", "Save & Apply")]
        else:
            foot = [("B", "Back"), ("START", "Save & Apply")]
        draw_panel_footer(surf, self.fonts["hint"], rect, self.FOOTER_H, foot)


class TextPrompt(SettingsScreen):
    """Small "type a name" box that reuses the Settings on-screen keyboard
    (controller) and also takes typing from a real keyboard."""

    def __init__(self, label, fonts, width, height, target=None):
        self.fonts, self.width, self.height = fonts, width, height
        self.config      = {}
        self.label       = label
        self.target      = target          # shortcut the name is for
        self.editing     = True
        self.editing_key = "_prompt"
        self.path_input  = ""
        self.result      = None            # ("ok", text) / ("cancel", None)
        self.kbd         = {"sel": [1, 0], "shift": True, "error": ""}
        self.opened_t    = time.time()
        pygame.event.set_grab(False)
        pygame.key.start_text_input()

    def _edit_label(self):
        return self.label

    def _commit_edit(self):
        name = re.sub(r"\s+", " ", self.path_input).strip()
        if not name:
            return False
        self.result = ("ok", name[:40])
        self._end_edit()
        return True

    def _kbd_done(self):
        if not self._commit_edit():
            self.kbd["error"] = "Type a name first"

    def _kbd_press(self, key):
        was_char = key["kind"] == "char"
        super()._kbd_press(key)
        if was_char and self.kbd and self.kbd["shift"] and len(self.path_input) == 1:
            self.kbd["shift"] = False          # capital first letter, then lower case

    def _cancel_edit(self):
        self.result = ("cancel", None)
        self._end_edit()

    def handle_key(self, event):
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            if not self._commit_edit():
                self.kbd["error"] = "Type a name first"
        elif event.key == pygame.K_ESCAPE:
            self._cancel_edit()
        elif event.key == pygame.K_BACKSPACE:
            self.path_input = self.path_input[:-1]
        elif event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
            self.path_input += clipboard_text()

    def handle_text_input(self, text):
        # The Space that opened the box can arrive as text right after it
        if not self.path_input:
            text = text.lstrip()
        self.path_input += text
        if self.kbd:
            self.kbd["error"] = ""

    @property
    def done(self):
        return self.result is not None


class CoverPicker:
    """Full-screen overlay to browse and pick a SteamGridDB cover for a game.

    Usage: create with the game name + full_path of the entry, call load() to
    kick off the network fetch, then draw()/handle() each frame. When the user
    presses A on a thumbnail, on_pick(cache_path) is invoked by the App.
    """

    def __init__(self, game_name, full_path, api_key, fonts, width, height, icon_size):
        self.game_name = game_name
        self.full_path = full_path
        self.api_key   = api_key
        self.fonts     = fonts
        self.width     = width
        self.height    = height
        self.icon_size = icon_size

        self.items: list       = []      # [{"url","thumb"}]
        self.thumbs: dict      = {}      # index -> pygame.Surface (or False while loading, None on fail)
        self.cursor            = 0
        self.scroll_y          = 0.0
        self.target_sy         = 0.0
        self.state             = "loading"   # loading | ready | empty | error | applying
        self.status            = ""
        self._thumb_pending: set = set()

        # Layout — fit the grid to the screen (works down to 1280x720 and below)
        self.gap    = _s(22)
        avail_w     = width - _s(80)
        avail_h     = height - _s(150) - _s(70) - _s(12)     # between header and footer
        self.cols   = max(2, min(5, (avail_w + self.gap) // (_s(150) + self.gap)))
        tw_fit_w    = (avail_w - (self.cols - 1) * self.gap) // self.cols
        tw_fit_h    = int(avail_h / 1.5)
        self.tw     = max(_s(60), min(_s(150), tw_fit_w, tw_fit_h))   # thumbnail width
        self.th     = int(self.tw * 1.5)                              # portrait height

    # ── networking ────────────────────────────────────────────────────────────
    def load(self):
        self.state = "loading"
        _icon_executor.submit(self._load_bg)

    def _load_bg(self):
        items = _sgdb_fetch_grid_list(self.game_name, self.api_key)
        if not items:
            # Distinguish "no key / net error" from "genuinely no art"
            self.state = "empty" if self.api_key else "error"
            self.status = ("No covers found for this game."
                           if self.api_key else "No SteamGridDB key set.")
            return
        self.items = items
        self.state = "ready"

    def _ensure_thumb(self, idx):
        if idx in self.thumbs or idx in self._thumb_pending:
            return
        if idx >= len(self.items):
            return
        self._thumb_pending.add(idx)
        self.thumbs[idx] = False   # loading sentinel
        _icon_executor.submit(self._thumb_bg, idx)

    def _thumb_bg(self, idx):
        try:
            url  = self.items[idx].get("thumb") or self.items[idx].get("url")
            data = _sgdb_download_url_bytes(url, timeout=12)
            if not data:
                self.thumbs[idx] = None
                return
            tmp = os.path.join(tempfile.gettempdir(), f"games_pick_{abs(hash(url))}.png")
            with open(tmp, "wb") as f:
                f.write(data)
            try:
                from PIL import Image as PilImage  # type: ignore[import]
                img = PilImage.open(tmp).convert("RGBA")
                # scale to fill the portrait thumb, then center-crop
                sw, sh = img.size
                scale  = max(self.tw / sw, self.th / sh)
                nw, nh = int(sw * scale), int(sh * scale)
                img = img.resize((nw, nh), getattr(PilImage, "Resampling", PilImage).LANCZOS)
                left, top = (nw - self.tw) // 2, (nh - self.th) // 2
                img = img.crop((left, top, left + self.tw, top + self.th))
                surf = pygame.image.fromstring(img.tobytes(), img.size, "RGBA")
            except ImportError:
                surf = pygame.image.load(tmp).convert_alpha()
                surf = pygame.transform.smoothscale(surf, (self.tw, self.th))
            self.thumbs[idx] = surf
        except Exception as e:  # noqa: BLE001
            _sgdb_log(f"THUMB {idx} error: {type(e).__name__}: {e}")
            self.thumbs[idx] = None
        finally:
            self._thumb_pending.discard(idx)

    # ── input ─────────────────────────────────────────────────────────────────
    def handle_button(self, btn):
        """Return: 'close' to dismiss, ('pick', cache_path) on success, or None."""
        if self.state in ("loading", "applying"):
            if btn == "B":
                return "close"
            return None
        if self.state in ("empty", "error"):
            if btn in ("A", "B"):
                return "close"
            return None

        # ready
        n = len(self.items)
        if btn == "B":
            return "close"
        elif btn == "left":
            self.cursor = (self.cursor - 1) % n
        elif btn == "right":
            self.cursor = (self.cursor + 1) % n
        elif btn == "up":
            if self.cursor - self.cols >= 0:
                self.cursor -= self.cols
        elif btn == "down":
            if self.cursor + self.cols < n:
                self.cursor += self.cols
        elif btn == "A":
            self.state  = "applying"
            self.status = "Downloading cover…"
            result = {"path": None}
            def _apply():
                result["path"] = _sgdb_set_cover(self.game_name, self.items[self.cursor]["url"])
                self._apply_result = result["path"]
            self._apply_result = "PENDING"
            _icon_executor.submit(_apply)
            return None
        self._scroll_to_cursor()
        return None

    def poll_apply(self):
        """Called each frame; returns ('pick', path) once the apply finishes."""
        if self.state == "applying" and getattr(self, "_apply_result", "PENDING") != "PENDING":
            path = self._apply_result
            if path:
                return ("pick", path)
            # failed — go back to ready so user can try another
            self.state  = "ready"
            self.status = "Download failed — try another."
        return None

    def _scroll_to_cursor(self):
        row     = self.cursor // self.cols
        cell_h  = self.th + self.gap + _s(6)
        top_pad = _s(150)
        vis_h   = self.height - top_pad - _s(90)
        row_top = row * cell_h
        if row_top - self.target_sy < 0:
            self.target_sy = float(row_top)
        elif row_top - self.target_sy + cell_h > vis_h:
            self.target_sy = float(row_top + cell_h - vis_h)

    # ── drawing ───────────────────────────────────────────────────────────────
    def draw(self, surf):
        ov = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 225))
        surf.blit(ov, (0, 0))

        title = self.fonts["title"].render(
            fit_text(self.fonts["title"], f"Choose cover — {self.game_name}", self.width - _s(80)),
            True, C_ACCENT2)
        surf.blit(title, (_s(40), _s(60)))
        sub_y = _s(60) + title.get_height() + _s(8)
        draw_hints(surf, self.fonts["hint"], [("A", "Use this cover"), ("B", "Cancel")],
                   _s(40), sub_y + _s(12))

        if self.state in ("loading", "applying"):
            msg = "Loading covers…" if self.state == "loading" else (self.status or "Working…")
            t = self.fonts["big"].render(msg, True, C_TEXT)
            surf.blit(t, t.get_rect(center=(self.width // 2, self.height // 2)))
            return
        if self.state in ("empty", "error"):
            t = self.fonts["ui"].render(self.status, True, C_YELLOW)
            surf.blit(t, t.get_rect(center=(self.width // 2, self.height // 2)))
            hint = self.fonts["hint"].render(
                f"Press {btn_text('A')} or {btn_text('B')} to close", True, C_TEXT_DIM)
            surf.blit(hint, hint.get_rect(center=(self.width // 2, self.height // 2 + _s(44))))
            return

        # ready — draw the thumbnail grid
        top_pad = _s(150)
        bot     = self.height - _s(70)
        total_w = self.cols * (self.tw + self.gap) - self.gap
        sx      = (self.width - total_w) // 2
        self.scroll_y += (self.target_sy - self.scroll_y) * 0.18
        surf.set_clip(pygame.Rect(0, top_pad, self.width, bot - top_pad))

        cell_h = self.th + self.gap + _s(6)
        for i in range(len(self.items)):
            row = i // self.cols
            col = i % self.cols
            x   = sx + col * (self.tw + self.gap)
            y   = top_pad + row * cell_h - self.scroll_y
            if y + self.th < top_pad or y > bot:
                continue
            self._ensure_thumb(i)
            rect = pygame.Rect(x, y, self.tw, self.th)
            sel  = i == self.cursor
            if sel:
                glow = pygame.Rect(x - _s(6), y - _s(6), self.tw + _s(12), self.th + _s(12))
                pygame.draw.rect(surf, C_ACCENT, glow, border_radius=_s(12))
            thumb = self.thumbs.get(i)
            if isinstance(thumb, pygame.Surface):
                surf.blit(thumb, (x, y))
            else:
                pygame.draw.rect(surf, C_CARD, rect, border_radius=_s(8))
                lbl = "…" if thumb is False else "×"
                lt  = self.fonts["big"].render(lbl, True, C_TEXT_DIM)
                surf.blit(lt, lt.get_rect(center=rect.center))
            pygame.draw.rect(surf, C_ACCENT if sel else C_GRAY, rect,
                             width=_s(3) if sel else 1, border_radius=_s(8))
        surf.set_clip(None)

        if self.status:
            st = self.fonts["hint"].render(self.status, True, C_YELLOW)
            surf.blit(st, (_s(40), bot + _s(20)))
        pos = self.fonts["hint"].render(
            f"{self.cursor + 1} / {len(self.items)}", True, C_TEXT_DIM)
        surf.blit(pos, (self.width - pos.get_width() - _s(40), bot + _s(20)))


class App:
    TAB_APPS     = 0
    TAB_PC       = 1
    TAB_EMU      = 2
    TAB_SETTINGS = 3
    TAB_COUNT    = 4
    TAB_LABELS   = ["APPS", "PC GAMES", "EMULATION", "SETTINGS"]
    TOPBAR_H     = _s(50)
    TABBAR_H     = _s(35)
    BOTTOMBAR_H  = _s(62)

    @property
    def GRID_TOP(self):
        return self.TOPBAR_H + self.TABBAR_H

    def __init__(self):
        # Tell Windows this process is DPI-aware so we get real pixel dimensions
        # and pygame fullscreen covers the entire physical screen at any scaling level
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except Exception:  # noqa: BLE001
            try:
                ctypes.windll.user32.SetProcessDPIAware()   # fallback for older Windows
            except Exception:  # noqa: BLE001
                pass
        # Let SDL keep reading the controller while a game is in front — used only
        # for the "hold VIEW + START to come back" escape (see _poll_escape).
        os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
        pygame.init()
        pygame.joystick.init()

        self.config = self._load_config()
        info        = pygame.display.Info()
        self.width  = info.current_w
        self.height = info.current_h
        # Borderless full-screen window (not exclusive full-screen): games can take
        # over the display instantly, without a mode switch or a focus fight.
        os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.get_rel()

        pygame.display.set_caption(APP_NAME)
        _set_window_icon()
        self.fonts = self._make_fonts()
        self.joy   = None
        self._init_joy()

        last = self.config.get("last_tab", self.TAB_PC)
        if not isinstance(last, int) or not 0 <= last < len(CATEGORIES):
            last = self.TAB_PC
        self.tab           = last
        self.last_cat_tab  = last
        self.tab_cursor    = {i: 0 for i in range(len(CATEGORIES))}
        self.path          = self.config["start_folder"]
        self.all_entries: list = []   # every shortcut found: dicts (see _scan)
        self.entries: list     = []   # shortcuts in the current category tab
        self.cursor        = 0
        self.scroll_y      = 0.0
        self.target_sy     = 0.0
        self.columns       = self.config["columns"]
        self.icon_size     = self.config["icon_size"]
        self.icon_gap      = _s(20)
        self.status_msg    = ""
        self.status_color  = C_GREEN
        self.status_time   = 0.0
        self.confirm_exit  = False
        self.exit_cursor   = 0   # index into POWER_OPTIONS
        self._desktop_mode = False   # "Go to Desktop": don't auto-return until the player comes back
        self.cat_menu      = None   # {"entry": dict, "cursor": int} while "Move to" menu is open
        self.opts_menu     = None   # X menu: Move to tab / Set category / Manage
        self.group_menu    = None   # "Set category" list for one shortcut
        self.prompt        = None   # TextPrompt while typing a new category name
        self.game_menu     = None   # VIEW + START over an emulated game: resume / close
        self.settings_leave = None  # "Unsaved changes" dialog when leaving Settings
        self.pairing       = None   # BluetoothPairing while the pairing screen is up
        self.pair_mode     = None   # "startup" (no controller yet) / "manual" (Power menu)
        self._kbd_used     = False  # a key was pressed → this is a keyboard user
        self._had_joy      = False  # a controller has been connected this session
        self._pair_tried   = False
        self._started_t    = time.time()
        # Categories rail (PC Games / Emulation): always starts hidden on "All"
        self.rail_open     = False
        self.rail_cursor   = 0
        self.rail_revert   = None   # (group, cursor) to restore when the rail is canceled
        self.group_sel     = {self.TAB_PC: GROUP_ALL, self.TAB_EMU: GROUP_ALL}
        self._trig_held    = {"LT": False, "RT": False}
        self.manage        = None   # Manage menu state (uninstall / remove shortcut)
        self._pending_uninstall = None   # shortcut to tidy up once its game is gone
        self._pending_check_t   = 0.0
        self.cover_picker  = None   # active CoverPicker overlay, or None
        self.show_keys     = False  # F1 keyboard-shortcuts panel
        self._last_pad_t   = 0.0
        self.settings      = SettingsScreen(self.config, self.fonts, self.width, self.height)

        spd = self.config.get("scroll_speed", "Normal")
        self.rep_del      = {"Slow": 0.5,  "Normal": 0.32, "Fast": 0.18}[spd]
        self.rep_rate     = {"Slow": 0.20, "Normal": 0.11, "Fast": 0.06}[spd]
        self.dead         = 0.4
        self.held: dict   = {}
        self._joy_retry_t = 0.0
        self._last_press: dict = {}   # button -> time, to drop duplicate presses
        self._launch_block_until = 0.0  # no launching right after a menu closes
        # Restore-after-game watcher state
        self._hwnd        = None
        if sys.platform == "win32":
            try:
                self._hwnd = pygame.display.get_wm_info().get("window")
            except Exception:  # noqa: BLE001
                self._hwnd = None
        self._launched_launcher = False   # the shortcut itself opens a store launcher
        self._game        = None   # windows of the game we launched (see _watch_foreground)
        self.osk          = None   # on-screen keyboard state while it's open
        self._joyxoff     = False  # JoyXoff running → our controller keyboard steps aside
        self._joyxoff_t   = 0.0
        self._keys_page   = 0      # F1 help: 0 = keyboard, 1 = controller
        self._osk_prev_x  = False
        self._escape_t    = None
        self._idle_since  = None   # when the desktop became the foreground window
        self._watch_t     = 0.0

        set_input_mode("pad" if self.joy else "kbd")
        self._dbg_log(f"=== GameClub started, build {APP_BUILD} ===")
        self._drop_old_run_entry()        # tidy the "GamesBrowser" entry from GAMES days
        self._migrate_from_padhub()       # one time only, after the rename
        self.stats = self._load_stats()   # {shortcut key: {"count","last","secs"}}
        self._play = None
        self._scan()
        self.clock = pygame.time.Clock()

    def _load_config(self):
        base = DEFAULT_CONFIG.copy()
        base["categories"] = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, encoding="UTF-8") as fh:
                    saved = json.load(fh)
                for k, v in saved.items():
                    base[k] = v
            except (OSError, json.JSONDecodeError):
                pass
        if not isinstance(base.get("categories"), dict):
            base["categories"] = {}
        global _sgdb_api_key
        _sgdb_api_key = base.get("sgdb_api_key", "")
        set_button_style(base.get("button_style", "Xbox"))
        set_accent(base.get("accent", "Blue"))
        if base.get("background") not in ("Solid", "Wallpaper"):
            base["background"] = "Solid"
        # Clear .miss files on startup so art is re-attempted with current key
        if _sgdb_api_key:
            try:
                for f in os.listdir(SGDB_CACHE_DIR):
                    if f.endswith(".miss"):
                        os.remove(os.path.join(SGDB_CACHE_DIR, f))
            except OSError:
                pass
        return base

    def _save_config(self):
        global _sgdb_api_key
        self.config["last_tab"] = self.last_cat_tab
        old_key = _sgdb_api_key
        _sgdb_api_key = self.config.get("sgdb_api_key", "")
        if _sgdb_api_key != old_key:
            for f in os.listdir(SGDB_CACHE_DIR):
                if f.endswith(".miss"):
                    try:
                        os.remove(os.path.join(SGDB_CACHE_DIR, f))
                    except OSError:
                        pass
        with open(CONFIG_FILE, "w", encoding="UTF-8") as fh:
            json.dump(self.config, fh, indent=2)

    def _migrate_from_padhub(self):
        """Once, after the PadHub → GameClub rename: move Start with Windows and
        Controller on UAC & Sign-in over to the new names (the old PadHub
        uninstaller removes its own tasks). Never runs again after that."""
        if self.config.get("app_name") == APP_NAME:
            return
        self.config["app_name"] = APP_NAME
        try:
            with open(CONFIG_FILE, "w", encoding="UTF-8") as fh:
                json.dump(self.config, fh, indent=2)
        except OSError:
            pass
        if sys.platform != "win32":
            return
        try:                                            # old Run entry, if any
            import winreg
            path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ) as k:
                winreg.QueryValueEx(k, "PadHub")
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, "PadHub")
        except OSError:
            pass
        on_start = bool(self.config.get("startup_with_windows"))
        on_sec   = bool(self.config.get("secure_desktop"))
        if on_start or on_sec:
            self._dbg_log("renamed to GameClub: setting up the startup options under the new name")
            self._apply_startup(on_start, on_sec)

    def _drop_old_run_entry(self):
        """Remove the old "GamesBrowser" Run entry — only if it's actually there."""
        if sys.platform != "win32":
            return
        try:
            import winreg
            path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ) as k:
                winreg.QueryValueEx(k, "GamesBrowser")
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, "GamesBrowser")
        except OSError:
            pass                                       # not there — nothing to do

    def _apply_startup(self, startup_changed=True, secure_changed=True):
        """Start with Windows / Controller on UAC & Sign-in. Called ONLY when you
        switch one of them in Settings and save — never at every start (re-creating
        startup tasks over and over is exactly what malware does, and Defender's
        "Persistence" detection reacts to it).
        • Installed GameClub.exe (runs as administrator): a scheduled task at sign-in.
        • Running the .py file: a "GameClub" entry in the Run key, as before."""
        if sys.platform != "win32" or not (startup_changed or secure_changed):
            return
        want = bool(self.config.get("startup_with_windows"))
        use_task = getattr(sys, "frozen", False) and is_elevated()
        if use_task and secure_changed:
            # Controller on UAC prompts & the sign-in screen: the SYSTEM task
            def sec_job(exe=sys.executable, on=bool(self.config.get("secure_desktop"))):
                ok = set_secure_task(on, exe, os.path.abspath(CONFIG_FILE))
                if on:
                    self._dbg_log(f"UAC & sign-in controller task -> {'ok' if ok else 'failed'}")
            _icon_executor.submit(sec_job)
        if not startup_changed:
            return
        if use_task:
            def job(exe=sys.executable, want=want):
                ok = set_startup_task(want, exe)
                self._dbg_log(f"start with Windows: scheduled task {'created' if want else 'removed'}"
                              f" -> {'ok' if ok else 'failed'}")
            _icon_executor.submit(job)
        elif not want:
            _icon_executor.submit(set_startup_task, False)   # tidy up a task from before
        try:
            import winreg
            reg_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE)
            if want and not use_task:
                if getattr(sys, "frozen", False):          # GameClub.exe without admin rights
                    cmd = f'"{sys.executable}"'
                else:                                      # running the .py file
                    cmd = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
                winreg.SetValueEx(reg_key, "GameClub", 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(reg_key, "GameClub")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(reg_key)
        except Exception:  # noqa: BLE001
            pass

    @staticmethod
    def _make_fonts():
        def sf(name, size, bold=False):
            return pygame.font.SysFont(name, size, bold=bold)
        try:
            return {
                "title": sf("Segoe UI", _s(26), True),
                "tab":   sf("Segoe UI", _s(15), True),
                "ui":    sf("Segoe UI", _s(17)),
                "name":  sf("Segoe UI", _s(13)),
                "hint":  sf("Segoe UI", _s(13), True),
                "path":  sf("Consolas", _s(12)),
                "big":   sf("Segoe UI", _s(46), True),
            }
        except Exception:  # noqa: BLE001
            pairs = [("title", 28, True), ("tab", 17, True), ("ui", 19, False),
                     ("name", _s(15), False), ("hint", _s(15), True), ("path", _s(16), False), ("big", _s(48), True)]
            return {k: pygame.font.SysFont(None, s, bold=b) for k, s, b in pairs}

    def _init_joy(self):
        self._bat_t = 0.0                    # read the battery again soon
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()
        else:
            self.joy = None

    def _check_joyxoff(self):
        """Every few seconds: is JoyXoff running? If so, our keyboard tool is off."""
        now = time.time()
        if now - self._joyxoff_t < 3.0:
            return
        self._joyxoff_t = now
        before = self._joyxoff
        try:
            self._joyxoff = joyxoff_running()
        except Exception:  # noqa: BLE001
            self._joyxoff = False
        if self._joyxoff != before:
            self._dbg_log(f"JoyXoff running: {self._joyxoff}")
        if self._joyxoff and self.osk:
            self.osk_close()

    def _check_joy_lost(self):
        t = getattr(self, "_joy_lost_t", None)
        if t is None or time.time() - t < 1.2:
            return
        self._joy_lost_t = None
        if pygame.joystick.get_count() == 0:
            self.joy = None
            set_input_mode("kbd")
            self.set_status("Controller disconnected", error=True)
        else:
            self._init_joy()

    def _get_events(self):
        """pygame.event.get(), but survive a pygame bug: after the joystick
        subsystem is re-initialized (when coming back from a game), SDL can still
        report "controller removed" for the OLD controller id, which pygame no
        longer knows — it then raises KeyError (as SystemError) instead of returning
        the event. Drop such events and carry on."""
        for _attempt in range(3):
            try:
                return pygame.event.get()
            except (SystemError, KeyError) as exc:
                cause = exc.__cause__ or exc.__context__ or exc
                self._dbg_log(f"pygame event bug ignored ({type(cause).__name__}: {cause}) "
                              "- stale controller event dropped")
                try:
                    pygame.event.clear((pygame.JOYDEVICEREMOVED,))
                except Exception:  # noqa: BLE001
                    pass
        return []

    def _reinit_joy(self):
        """Fully reset joystick subsystem after returning from a game."""
        self.held.clear()
        # quit()/init() makes SDL report a "removed" + "added" pair — ignore those
        self._joy_reset_until = time.time() + 1.5
        try:
            pygame.joystick.quit()
            pygame.joystick.init()
            try:                              # stale add/remove events for the old ids
                pygame.event.clear((pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED))
            except Exception:  # noqa: BLE001
                pass
            self._init_joy()
        except Exception:  # noqa: BLE001
            self.joy = None

    # ── shortcut scanning & categories ────────────────────────────────────────
    def _draw_loading(self, msg):
        self.screen.fill(C_BG)
        t = self.fonts["big"].render(msg, True, C_TEXT_DIM)
        self.screen.blit(t, t.get_rect(center=(self.width // 2, self.height // 2)))
        pygame.display.flip()
        pygame.event.pump()

    def _current_cat(self):
        return CATEGORIES[self.tab] if self.tab < len(CATEGORIES) else None

    def _scan(self):
        """Collect every launchable shortcut under the Shortcuts Folder and
        assign each one a category (manual override or auto-detected)."""
        self.all_entries = []
        # If the configured folder no longer exists, fall back to Desktop/home
        if not os.path.isdir(self.path):
            fallback = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.isdir(fallback):
                fallback = os.path.expanduser("~")
            self.path = fallback
            self.set_status("Folder not found - set Shortcuts Folder in Settings", error=True)

        root     = self.path
        scan_sub = self.config.get("scan_subfolders", True)
        found    = []   # (full_path, relative_dir)
        for dirpath, dirnames, filenames in os.walk(root):
            rel   = os.path.relpath(dirpath, root)
            depth = 0 if rel == "." else rel.count(os.sep) + 1
            if scan_sub and depth < MAX_SCAN_DEPTH:
                dirnames[:] = [d for d in dirnames
                               if not d.startswith(".") and d.lower() not in ALWAYS_HIDE]
            else:
                dirnames[:] = []
            for fn in filenames:
                if fn.startswith(".") or fn.lower() in ALWAYS_HIDE:
                    continue
                if os.path.splitext(fn)[1].lower() not in LAUNCH_EXTS:
                    continue
                found.append((os.path.join(dirpath, fn), "" if rel == "." else rel))

        lnks = [f for f, _ in found if f.lower().endswith(".lnk")]
        if lnks:
            self._draw_loading("Reading shortcuts…")
        targets   = _resolve_lnk_targets(lnks) if lnks else {}
        overrides = self.config.setdefault("categories", {})
        groups    = self.config.setdefault("groups", {})

        for full, rel in found:
            fn  = os.path.basename(full)
            ext = os.path.splitext(fn)[1].lower()
            if ext == ".lnk":
                tgt, args = targets.get(full, ("", ""))
            elif ext == ".url":
                tgt, args = _read_url_target(full), ""
            else:
                tgt, args = full, ""
            auto = detect_category(full, rel, tgt, args)
            cat  = overrides.get(_cat_key(full), auto)
            if cat not in CATEGORIES:
                cat = auto
            entry = {
                "name": os.path.splitext(fn)[0],
                "file": fn,
                "path": full,
                "auto": auto,
                "cat":  cat,
                "target": tgt if ext != ".url" else tgt,
                "args":   args,
                "folder_group": folder_group(rel),
                "system": detect_system(tgt if ext == ".lnk" else full, args)
                          if ext != ".url" else "",
            }
            g = groups.get(_cat_key(full))
            entry["group"] = g if isinstance(g, str) else self._auto_group(entry)
            self.all_entries.append(entry)
        self.all_entries.sort(key=lambda e: e["name"].lower())

        _icon_cache.clear()
        _icon_pending.clear()
        # Clear .miss files so SGDB art is retried (e.g. after key is entered)
        if _sgdb_api_key:
            try:
                for _f in os.listdir(SGDB_CACHE_DIR):
                    if _f.endswith(".miss"):
                        os.remove(os.path.join(SGDB_CACHE_DIR, _f))
            except OSError:
                pass

        self.tab_cursor = {i: 0 for i in range(len(CATEGORIES))}
        self._refresh_view(reset=True)

        # The scan can block for a while (many shortcuts / first run). Throw
        # away any presses that queued up meanwhile — e.g. the duplicate of the
        # Start press that saved Settings, which would otherwise open the
        # Power menu — and ignore buttons for a moment afterward.
        try:
            pygame.event.clear((pygame.KEYDOWN, pygame.KEYUP, pygame.TEXTINPUT,
                                pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP,
                                pygame.JOYHATMOTION, pygame.JOYAXISMOTION))
        except pygame.error:
            pass
        if hasattr(self, "held"):
            self.held.clear()
        self._input_block_until = time.time() + 0.4

    def _sort_entries(self, entries, cat):
        mode  = self.config.get(SORT_KEYS.get(cat, ""), SORT_MODES[0])
        stats = self.stats
        def st(e):
            return stats.get(_cat_key(e["path"]), {})
        by_name = lambda e: e["name"].lower()
        if mode == "Recently played":
            return sorted(entries, key=lambda e: (-st(e).get("last", 0), by_name(e)))
        if mode == "Most played":
            return sorted(entries, key=lambda e: (-st(e).get("secs", 0),
                                                  -st(e).get("count", 0), by_name(e)))
        return sorted(entries, key=by_name)

    def _refresh_view(self, reset=False, keep_path=None):
        """Rebuild self.entries for the active category tab (sorted).
        keep_path: keep this shortcut selected even if it moved in the order."""
        cat = self._current_cat()
        entries = [e for e in self.all_entries if e["cat"] == cat] if cat else []
        if self._has_rail():
            names = {n for n, _c in self._group_list()}
            sel   = self.group_sel.get(self.tab, GROUP_ALL)
            if sel not in names:                 # that category is gone (rescan, moved…)
                sel = self.group_sel[self.tab] = GROUP_ALL
            if sel != GROUP_ALL:
                entries = [e for e in entries if e.get("group", "") == sel]
        self.entries = self._sort_entries(entries, cat) if cat else []
        if reset:
            self.cursor = self.tab_cursor.get(self.tab, 0)
        if keep_path:
            for i, e in enumerate(self.entries):
                if e["path"] == keep_path:
                    self.cursor = i
                    break
        self.cursor = max(0, min(self.cursor, len(self.entries) - 1))
        self.scroll_y  = 0.0
        self.target_sy = 0.0
        if self.entries:
            self._scroll_to_cursor()
            self.scroll_y = self.target_sy   # jump straight there, no slide

    # ── categories rail (sub-categories inside PC Games / Emulation) ──────────
    def _auto_group(self, entry):
        """Category a shortcut gets without a manual choice: its subfolder, or
        (in Emulation) the system worked out from the emulator / ROM."""
        if entry.get("folder_group"):
            return entry["folder_group"]
        if entry.get("cat") == "emulation":
            return entry.get("system", "")
        return GROUP_NONE

    def _has_rail(self, tab=None):
        return (self.tab if tab is None else tab) in (self.TAB_PC, self.TAB_EMU)

    def _group_list(self, tab=None):
        """[(group, count)] for the rail: All, the categories A–Z, Uncategorized."""
        tab = self.tab if tab is None else tab
        cat = CATEGORIES[tab]
        counts, none = {}, 0
        for e in self.all_entries:
            if e["cat"] != cat:
                continue
            g = e.get("group", "")
            if g:
                counts[g] = counts.get(g, 0) + 1
            else:
                none += 1
        out = [(GROUP_ALL, sum(counts.values()) + none)]
        out += sorted(counts.items(), key=lambda kv: kv[0].lower())
        if none and counts:
            out.append((GROUP_NONE, none))
        return out

    @staticmethod
    def _group_label(g):
        return "All" if g == GROUP_ALL else (g or "Uncategorized")

    def _rail_noun(self):
        return "Systems" if self.tab == self.TAB_EMU else "Categories"

    def _select_group(self, group):
        if self.group_sel.get(self.tab) == group:
            return
        self.group_sel[self.tab] = group
        self.cursor = 0
        self._refresh_view()

    def _step_group(self, step):
        groups = [g for g, _c in self._group_list()]
        if len(groups) < 2:
            return
        cur = self.group_sel.get(self.tab, GROUP_ALL)
        i   = groups.index(cur) if cur in groups else 0
        self._select_group(groups[(i + step) % len(groups)])
        if self.rail_open:
            self.rail_cursor = groups.index(self.group_sel[self.tab])

    def open_rail(self):
        groups = [g for g, _c in self._group_list()]
        cur    = self.group_sel.get(self.tab, GROUP_ALL)
        self.rail_open   = True
        self.rail_cursor = groups.index(cur) if cur in groups else 0
        self.rail_revert = (cur, self.cursor)
        self._clamp_cursor()

    def close_rail(self, keep=True):
        if not self.rail_open:
            return
        self.rail_open = False
        if not keep and self.rail_revert:
            g, c = self.rail_revert
            self.group_sel[self.tab] = g
            self.cursor = c
            self._refresh_view()
        self.rail_revert = None
        self._clamp_cursor()

    def _clamp_cursor(self):
        """Columns change when the rail opens/closes — keep the selection visible."""
        self.cursor = max(0, min(self.cursor, len(self.entries) - 1))
        if self.entries:
            self._scroll_to_cursor()

    def _rail_action(self, btn):
        """Input while the rail is open. Returns True if the press was used."""
        groups = [g for g, _c in self._group_list()]
        if btn in ("up", "down", "LT", "RT"):
            step = -1 if btn in ("up", "LT") else 1
            self.rail_cursor = (self.rail_cursor + step) % len(groups)
            self._select_group(groups[self.rail_cursor])   # grid follows (preview)
            return True
        if btn in ("A", "right"):
            self.close_rail(keep=True)
            self._block_launch()
            return True
        if btn in ("B", "back"):
            self.close_rail(keep=False)
            self._block_launch()
            return True
        if btn in ("LB", "RB"):
            self.close_rail(keep=True)
            return False                                   # still switch tab
        return btn not in ("start",)                       # Power menu still works

    # ── X menu: Options (Move to tab / Set category / Manage) ──────────────────
    def open_options(self):
        if not self.entries:
            return
        self.opts_menu = {"entry": self.entries[self.cursor], "cursor": 0}

    def _opts_options(self):
        opts = [("Move to tab…", C_ACCENT2, "move")]
        if self._has_rail():
            noun = "system" if self.tab == self.TAB_EMU else "category"
            opts.append((f"Set {noun}…", (120, 200, 140), "group"))
        opts += [("Manage…", (220, 170, 40), "manage"),
                 ("Cancel", (150, 160, 178), "cancel")]
        return opts

    def _opts_action(self, btn):
        m, opts = self.opts_menu, self._opts_options()
        if btn == "up":
            m["cursor"] = (m["cursor"] - 1) % len(opts)
        elif btn == "down":
            m["cursor"] = (m["cursor"] + 1) % len(opts)
        elif btn in ("B", "X"):
            self.opts_menu = None
        elif btn == "A":
            act, entry = opts[m["cursor"]][2], m["entry"]
            self.opts_menu = None
            if act == "move":
                self.cat_menu = {"entry": entry, "cursor": CATEGORIES.index(entry["cat"])}
            elif act == "group":
                self.open_group_menu(entry)
            elif act == "manage":
                self.open_manage(entry)

    def _draw_opts_menu(self):
        m = self.opts_menu
        self._draw_menu_panel("Options", m["entry"]["name"],
                              [(lbl, col) for lbl, col, _a in self._opts_options()], m["cursor"])

    # ── "Set category" for one shortcut ────────────────────────────────────────
    def open_group_menu(self, entry):
        self.group_menu = {"entry": entry, "cursor": 0}
        opts = self._group_menu_options()
        cur  = self._group_menu_current(opts)
        self.group_menu["cursor"] = cur if cur is not None else 0

    def _group_menu_options(self):
        entry = self.group_menu["entry"]
        names = sorted({e.get("group", "") for e in self.all_entries
                        if e["cat"] == entry["cat"] and e.get("group")} |
                       ({entry["group"]} if entry.get("group") else set()),
                       key=str.lower)
        auto  = self._auto_group(entry)
        opts  = [(n, C_ACCENT2, ("set", n)) for n in names]
        opts += [("+ New…", (120, 200, 140), ("new", None)),
                 ("Uncategorized", (150, 160, 178), ("set", GROUP_NONE)),
                 (f"Auto ({auto or 'Uncategorized'})", C_YELLOW, ("auto", None))]
        return opts

    def _group_menu_current(self, opts):
        entry = self.group_menu["entry"]
        has_override = isinstance(self.config.get("groups", {}).get(_cat_key(entry["path"])), str)
        for i, (_l, _c, (act, val)) in enumerate(opts):
            if has_override and act == "set" and val == entry.get("group", ""):
                return i
            if not has_override and act == "auto":
                return i
        return None

    def _group_menu_action(self, btn):
        m, opts = self.group_menu, self._group_menu_options()
        if btn in ("up", "down"):
            m["cursor"] = (m["cursor"] + (-1 if btn == "up" else 1)) % len(opts)
        elif btn in ("LT", "RT"):                      # page through long lists
            m["cursor"] = max(0, min(len(opts) - 1, m["cursor"] + (-8 if btn == "LT" else 8)))
        elif btn == "B":
            self.group_menu = None
        elif btn == "A":
            act, val = opts[m["cursor"]][2]
            entry = m["entry"]
            if act == "new":
                noun = "system" if entry["cat"] == "emulation" else "category"
                self.prompt = TextPrompt(f"New {noun}", self.fonts, self.width, self.height,
                                         target=entry)
                return
            self.group_menu = None
            self.set_group(entry, None if act == "auto" else val)

    def set_group(self, entry, group):
        """Give a shortcut a category (None = back to automatic)."""
        groups = self.config.setdefault("groups", {})
        key    = _cat_key(entry["path"])
        if group is None:
            groups.pop(key, None)
            entry["group"] = self._auto_group(entry)
        else:
            groups[key] = group
            entry["group"] = group
        self._save_config()
        self._refresh_view(keep_path=entry["path"])
        self.set_status(f"{entry['name']} → {self._group_label(entry['group'])}")

    def _draw_group_menu(self):
        m     = self.group_menu
        opts  = self._group_menu_options()
        cur   = self._group_menu_current(opts)
        # Long lists: show a window of rows around the cursor
        row   = _s(56)
        fit   = max(4, (self.height - _s(64) - _s(24) - _s(52) - _s(28) - _s(40)) // row)
        start = 0
        if len(opts) > fit:
            start = max(0, min(m["cursor"] - fit // 2, len(opts) - fit))
        vis   = opts[start:start + fit]
        noun  = "System" if m["entry"]["cat"] == "emulation" else "Category"
        self._draw_menu_panel(f"Set {noun}", m["entry"]["name"],
                              [(lbl, col) for lbl, col, _a in vis], m["cursor"] - start,
                              current=None if cur is None else cur - start)

    def _finish_prompt(self):
        """New category typed (or canceled) in the TextPrompt."""
        p, self.prompt = self.prompt, None
        if p.result and p.result[0] == "ok" and p.target is not None:
            self.group_menu = None
            self.set_group(p.target, p.result[1])
        self._block_launch()

    def switch_tab(self, direction):
        self.close_rail(keep=True)
        if self.tab < len(CATEGORIES):
            self.tab_cursor[self.tab] = self.cursor
        self.tab = (self.tab + direction) % self.TAB_COUNT
        if self.tab < len(CATEGORIES):
            self.last_cat_tab = self.tab
            self._refresh_view(reset=True)

    def open_cat_menu(self):
        if not self.entries:
            return
        entry = self.entries[self.cursor]
        self.cat_menu = {"entry": entry, "cursor": CATEGORIES.index(entry["cat"])}

    def _cat_menu_options(self):
        auto = self.cat_menu["entry"]["auto"]
        return ([(CATEGORY_NAMES[c], c) for c in CATEGORIES]
                + [(f"Auto-detect ({CATEGORY_NAMES[auto]})", "auto")])

    def _cat_menu_action(self, btn):
        opts = self._cat_menu_options()
        if btn == "up":
            self.cat_menu["cursor"] = (self.cat_menu["cursor"] - 1) % len(opts)
        elif btn == "down":
            self.cat_menu["cursor"] = (self.cat_menu["cursor"] + 1) % len(opts)
        elif btn in ("B", "X"):
            self.cat_menu = None
        elif btn == "A":
            entry  = self.cat_menu["entry"]
            choice = opts[self.cat_menu["cursor"]][1]
            self.cat_menu = None
            self.set_category(entry, choice)

    def set_category(self, entry, choice):
        """Move a shortcut to another category ('auto' clears the override)."""
        cats = self.config.setdefault("categories", {})
        key  = _cat_key(entry["path"])
        new  = entry["auto"] if choice == "auto" else choice
        if new == entry["auto"]:
            cats.pop(key, None)       # matches auto-detect → no override needed
        else:
            cats[key] = new
        old = entry["cat"]
        entry["cat"] = new
        if not isinstance(self.config.get("groups", {}).get(key), str):
            entry["group"] = self._auto_group(entry)   # e.g. system only applies in Emulation
        # Apps and games render differently (icon vs. SGDB art) — re-render.
        _icon_cache.pop(entry["path"], None)
        _icon_pending.discard(entry["path"])
        self._save_config()
        if new == old:
            self.set_status(f"{entry['name']} stays in {CATEGORY_NAMES[new]}")
            return
        self._refresh_view()
        self.set_status(f"Moved {entry['name']} to {CATEGORY_NAMES[new]}")

    # ── leaving Settings with unsaved changes ─────────────────────────────────
    LEAVE_OPTIONS = [("save", "Save & Apply", (77, 181, 108)),
                     ("discard", "Discard changes", (222, 72, 72)),
                     ("keep", "Keep editing", (150, 160, 178))]

    def _settings_dirty(self):
        return any(self.settings.config.get(o[1]) != self.config.get(o[1])
                   for o in SettingsScreen.OPTIONS)

    def _settings_leave_action(self, btn):
        """Returns "save" / "back" when the dialog decides, else None."""
        m, n = self.settings_leave, len(self.LEAVE_OPTIONS)
        if btn in ("up", "down"):
            m["cursor"] = (m["cursor"] + (-1 if btn == "up" else 1)) % n
            return None
        if btn == "B":
            self.settings_leave = None                   # = Keep editing
            return None
        if btn != "A":
            return None
        act = self.LEAVE_OPTIONS[m["cursor"]][0]
        self.settings_leave = None
        if act == "save":
            return "save"
        if act == "discard":
            keep = (self.settings.page if hasattr(self.settings, "page") else 0)
            self.settings.config = self.config.copy()    # throw the edits away
            self.settings.page = keep
            self.set_status("Changes discarded")
            return "back"
        return None

    def _draw_settings_leave(self):
        self._draw_menu_panel("Unsaved changes", "Save them before leaving?",
                              [(lbl, col) for _a, lbl, col in self.LEAVE_OPTIONS],
                              self.settings_leave["cursor"])

    def _settings_change_summary(self, before):
        """Pop-up text describing which settings were actually changed."""
        changes = []
        for opt in SettingsScreen.OPTIONS:
            label, key = opt[0], opt[1]
            old, new = before.get(key), self.config.get(key)
            if old == new:
                continue
            if key == "sgdb_api_key":
                if not new:
                    changes.append("SteamGridDB key removed")
                elif not old:
                    changes.append("SteamGridDB key added")
                else:
                    changes.append("SteamGridDB key changed")
            elif opt[2] == "bool":
                changes.append(f"{label} {'ON' if new else 'OFF'}")
            elif opt[2] == "choice":
                changes.append(f"{label}: {new}")
            else:
                changes.append(f"{label} changed")
        if not changes:
            return "Settings saved \u2014 no changes"
        if len(changes) > 3:
            changes = changes[:3] + [f"+{len(changes) - 3} more"]
        return "Saved: " + ", ".join(changes)

    # ── Manage menu: uninstall / remove shortcut ──────────────────────────────
    def open_manage(self, entry=None):
        if entry is None:
            if not self.entries:
                return
            entry = self.entries[self.cursor]
        if entry["cat"] == "emulation" or entry["auto"] == "emulation":
            # The target is the emulator — never offer to uninstall it from a game tile
            uninst, reason = None, "Not available for emulated games"
        else:
            try:
                uninst = find_uninstall_route(entry)
            except Exception:  # noqa: BLE001
                uninst = None
            reason = None if uninst else "No uninstaller found for this shortcut"
        self.manage = {"entry": entry, "stage": "menu", "cursor": 0,
                       "uninst": uninst, "reason": reason}

    def _manage_options(self):
        m = self.manage
        if m["stage"] == "menu":
            noun = "app" if m["entry"]["cat"] == "apps" else "game"
            u = m["uninst"]
            if not u:
                un_label, un_col = f"Uninstall {noun} (unavailable)", C_TEXT_DIM
            elif u["kind"] in ("launcher", "settings"):
                un_label, un_col = f"Uninstall in {u['name']}", (222, 72, 72)
            else:
                un_label, un_col = f"Uninstall {noun}", (222, 72, 72)
            return [(un_label, un_col, "uninstall"),
                    ("Remove shortcut", (220, 170, 40), "remove"),
                    ("Cancel", (150, 160, 178), "cancel")]
        if m["stage"] == "confirm_uninstall":
            return [("Cancel", (150, 160, 178), "cancel"),
                    ("Yes, uninstall", (222, 72, 72), "do_uninstall")]
        return [("Cancel", (150, 160, 178), "cancel"),
                ("Move to Recycle Bin", (220, 170, 40), "do_remove")]

    def _manage_action(self, btn):
        m    = self.manage
        opts = self._manage_options()
        if btn == "up":
            m["cursor"] = (m["cursor"] - 1) % len(opts)
        elif btn == "down":
            m["cursor"] = (m["cursor"] + 1) % len(opts)
        elif btn in ("B", "back"):
            self.manage = None
        elif btn == "A":
            act = opts[m["cursor"]][2]
            if act == "cancel":
                self.manage = None
            elif act == "uninstall":
                if not m["uninst"]:
                    self.set_status(m["reason"], error=True)
                    return
                if m["uninst"]["kind"] in ("launcher", "settings"):
                    # Only opens a page — the launcher/Windows asks before removing anything
                    entry, uninst = m["entry"], m["uninst"]
                    self.manage = None
                    self._start_uninstall(entry, uninst)
                    return
                m["stage"], m["cursor"] = "confirm_uninstall", 0   # default = Cancel
            elif act == "remove":
                m["stage"], m["cursor"] = "confirm_remove", 0      # default = Cancel
            elif act == "do_uninstall":
                entry, uninst = m["entry"], m["uninst"]
                self.manage = None
                self._start_uninstall(entry, uninst)
            elif act == "do_remove":
                entry = m["entry"]
                self.manage = None
                self._remove_shortcut(entry)

    def _start_uninstall(self, entry, uninst):
        try:
            pygame.event.set_grab(False)
            ok = run_uninstaller(uninst["cmd"])
        except OSError:
            ok = False
        if not ok:
            pygame.event.set_grab(True)
            self.set_status(f"Couldn't open {uninst['name']}", error=True)
            return
        # Bring the app back when the uninstaller window closes (same as after a game)
        self._begin_tracking(self._snapshot_windows(), launched_launcher=False)
        # If the game's exe disappears, tidy up its shortcut automatically
        tgt = entry.get("target", "")
        if uninst["kind"] == "program" and tgt and os.path.isfile(tgt):
            self._pending_uninstall = {"entry": entry, "exe": tgt, "t": time.time()}
        if uninst["kind"] == "settings":
            self.set_status(f"Find \u201c{entry['name']}\u201d in Installed apps and choose Uninstall")
        elif uninst["kind"] == "launcher":
            self.set_status(f"Opened {uninst['name']} \u2014 uninstall {entry['name']} there")
        else:
            self.set_status(f"Uninstaller started: {uninst['name']}")

    def _check_pending_uninstall(self):
        p = self._pending_uninstall
        if not p:
            return
        now = time.time()
        if now - self._pending_check_t < 2.0:
            return
        self._pending_check_t = now
        if now - p["t"] > 30 * 60:              # give up after 30 minutes
            self._pending_uninstall = None
            return
        if not os.path.exists(p["exe"]):
            self._pending_uninstall = None
            if os.path.exists(p["entry"]["path"]):
                self._remove_shortcut(p["entry"], after_uninstall=True)

    def _remove_shortcut(self, entry, after_uninstall=False):
        if not move_to_recycle_bin(entry["path"]):
            self.set_status(f"Couldn't remove the shortcut for {entry['name']}", error=True)
            return
        self.all_entries = [e for e in self.all_entries if e["path"] != entry["path"]]
        cats = self.config.setdefault("categories", {})
        if cats.pop(_cat_key(entry["path"]), None) is not None:
            self._save_config()
        _icon_cache.pop(entry["path"], None)
        _icon_pending.discard(entry["path"])
        self._refresh_view()
        if after_uninstall:
            self.set_status(f"{entry['name']} uninstalled \u2014 shortcut moved to Recycle Bin")
        else:
            self.set_status(f"Shortcut moved to Recycle Bin: {entry['name']}")

    def _draw_manage(self):
        m     = self.manage
        opts  = self._manage_options()
        title = {"menu": "Manage", "confirm_uninstall": "Uninstall?",
                 "confirm_remove": "Remove shortcut?"}[m["stage"]]
        sub   = m["uninst"]["name"] if m["stage"] == "confirm_uninstall" else m["entry"]["name"]
        self._draw_menu_panel(title, sub, [(lbl, col) for lbl, col, _ in opts], m["cursor"])

    def _note_input(self, src, now):
        """Switch the on-screen hints between controller and keyboard.
        Keyboard events that arrive right after controller input are ignored,
        because Steam Input & co. often send a key alongside the button."""
        if src in ("joy", "hat", "axis"):
            self._last_pad_t = now
            set_input_mode("pad")
        elif now - self._last_pad_t > 0.5:
            set_input_mode("kbd")

    # ── play stats & sort order ───────────────────────────────────────────────
    def _load_stats(self):
        try:
            with open(STATS_FILE, encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_stats(self):
        try:
            with open(STATS_FILE, "w", encoding="utf-8") as fh:
                json.dump(self.stats, fh, indent=1)
        except OSError:
            pass

    def cycle_sort(self):
        cat = self._current_cat()
        if not cat:
            return
        key  = SORT_KEYS[cat]
        cur  = self.config.get(key, SORT_MODES[0])
        new  = SORT_MODES[(SORT_MODES.index(cur) + 1) % len(SORT_MODES)] if cur in SORT_MODES \
               else SORT_MODES[0]
        self.config[key] = new
        self.settings.config[key] = new          # keep the Settings copy in sync
        keep = self.entries[self.cursor]["path"] if self.entries else None
        self._save_config()
        self._refresh_view(keep_path=keep)
        self.set_status(f"{CATEGORY_NAMES[cat]} sorted by {new}")

    def _start_play(self, entry):
        k = _cat_key(entry["path"])
        rec = self.stats.setdefault(k, {})
        rec["count"] = rec.get("count", 0) + 1
        rec["last"]  = time.time()
        self._save_stats()
        self._play = {"key": k, "path": entry["path"], "start": time.time()}

    def _end_play(self):
        """Add the finished session's time (rough: launch → back in the app)."""
        p = getattr(self, "_play", None)
        if not p:
            return
        secs = time.time() - p["start"]
        if secs < 15:
            return      # probably a launcher hand-off, not the game closing — keep counting
        self._play = None
        if secs <= 24 * 3600:
            rec = self.stats.setdefault(p["key"], {})
            rec["secs"] = rec.get("secs", 0) + int(secs)
            self._save_stats()
        # Re-sort (Recently/Most played may have changed) and stay on the game
        self._refresh_view(keep_path=p["path"])

    def set_status(self, msg, error=False):
        self.status_msg   = msg
        self.status_color = C_RED if error else C_GREEN
        self.status_time  = time.time()

    def open_cover_picker(self):
        """Open the SGDB cover picker for the currently selected shortcut."""
        if not self.entries:
            return
        entry = self.entries[self.cursor]
        ext   = os.path.splitext(entry["file"])[1].lower()
        if ext not in SGDB_EXTS:
            self.set_status("Covers apply to .lnk/.exe/.url only", error=True)
            return
        if not _sgdb_api_key:
            self.set_status("Set a SteamGridDB key in Settings first", error=True)
            return
        self.cover_picker = CoverPicker(
            entry["name"], entry["path"], _sgdb_api_key, self.fonts,
            self.width, self.height, self.icon_size)
        self.cover_picker.load()

    def _apply_picked_cover(self, cache_path):
        """After the picker downloads a chosen cover, refresh that entry's icon."""
        picker = self.cover_picker
        if picker:
            # Drop cached surface so the grid re-renders from the new PNG.
            _icon_cache.pop(picker.full_path, None)
            _icon_pending.discard(picker.full_path)
        self.cover_picker = None
        pygame.event.set_grab(True)
        self._block_launch()
        self.set_status("Cover updated")

    def _block_launch(self, seconds=0.4):
        self._launch_block_until = max(self._launch_block_until, time.time() + seconds)

    LAUNCH_TIMEOUT = 60    # seconds to keep watching for the game's window
    LAUNCH_CARD    = 8     # seconds the "Launching…" card stays on screen at most

    def open_selected(self):
        if not self.entries or time.time() < self._launch_block_until:
            return
        since = time.time() - getattr(self, "_last_front_t", 0)
        self._dbg_log(f"LAUNCH '{self.entries[self.cursor]['name']}' "
                      f"{since:.2f} s after GAMES came back to the front")
        self._flush_log(force=True)
        if getattr(self, "_launching", None):
            return                               # one launch at a time
        entry = self.entries[self.cursor]
        pygame.event.set_grab(False)
        before = set()
        if sys.platform == "win32":
            try:
                before = set(_win_big_windows())
            except Exception:  # noqa: BLE001
                pass
        job = {"entry": entry, "t": time.time(), "before": before,
               "error": None, "started": False, "check_t": 0.0}
        self._launching = job

        def work(job=job):
            # Starting a shortcut can take a second or two (shell, SmartScreen…);
            # do it off the UI thread so the screen never freezes.
            try:
                if sys.platform == "win32":
                    import ctypes
                    ctypes.windll.ole32.CoInitializeEx(None, 2)       # shell needs COM
                    ctypes.windll.user32.AllowSetForegroundWindow(-1) # let the game take focus
                open_as_user(job["entry"]["path"])   # never as admin, even if GameClub is
                job["started"] = True
            except OSError as exc:
                job["error"] = str(exc)
        _icon_executor.submit(work)

        self._start_play(entry)
        self._game_entry = entry          # for the in-game menu (VIEW + START)
        tgt = os.path.basename(entry.get("target", "") or "").lower()
        self._begin_tracking(self._snapshot_windows() | before, launched_launcher=(
            tgt in LAUNCHER_EXES and "-applaunch" not in entry.get("args", "")))

    def _check_launch(self):
        """Watch for the launched game's window; put it in front and step aside."""
        job = getattr(self, "_launching", None)
        if not job:
            return
        now = time.time()
        if job["error"]:
            self._launching = None
            self._play = None
            rec = self.stats.get(_cat_key(job["entry"]["path"]))
            if rec and rec.get("count", 0) > 0:          # a failed launch isn't a play
                rec["count"] -= 1
                self._save_stats()
            pygame.event.set_grab(True)
            self.set_status(job["error"], error=True)
            return
        if job["started"] and not self._in_front():
            self._launching = None               # something else already took the screen
            return
        if now - job["t"] > self.LAUNCH_TIMEOUT:
            self._launching = None               # game never showed a window we could see
            return
        if sys.platform != "win32" or not job["started"] or now - job["check_t"] < 0.25:
            return
        job["check_t"] = now
        try:
            new = [h for h in _win_big_windows() if h not in job["before"]]
        except Exception:  # noqa: BLE001
            new = []
        if new:
            self._launching = None
            try:
                pygame.display.iconify()         # get out of the game's way
                _win_bring_to_front(new[0])
            except Exception:  # noqa: BLE001
                pass

    def _launch_card_visible(self):
        job = getattr(self, "_launching", None)
        return bool(job) and time.time() - job["t"] < self.LAUNCH_CARD

    def _draw_launching(self):
        if not self._launch_card_visible():
            return
        job = self._launching
        ov = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ov.fill((8, 10, 14, 170))
        self.screen.blit(ov, (0, 0))
        name  = fit_text(self.fonts["title"], job["entry"]["name"], _s(420))
        dots  = "." * (1 + int((time.time() - job["t"]) * 3) % 3)
        t1 = self.fonts["hint"].render("LAUNCHING" + dots, True, C_ACCENT2)
        t2 = self.fonts["title"].render(name, True, C_WHITE)
        back_txt = ("for the game menu (resume / close)" if job["entry"].get("cat") == "emulation"
                    else "to come back here")
        t3 = self.fonts["hint"].render(
            f"Hold {pad_btn_text('VIEW')} + {pad_btn_text('START')} {back_txt}"
            + ("" if self._joyxoff else
               f"  \u00b7  {pad_btn_text('VIEW')} + {pad_btn_text('X')} for a keyboard on login screens"),
            True, C_TEXT_DIM) if self.joy else None
        pw = max(_s(320), t2.get_width() + _s(80), (t3.get_width() + _s(60)) if t3 else 0)
        ph = t1.get_height() + t2.get_height() + _s(60) + (t3.get_height() + _s(12) if t3 else 0)
        rect = ((self.width - pw) // 2, (self.height - ph) // 2, pw, ph)
        draw_panel(self.screen, rect, _s(18))
        pygame.draw.rect(self.screen, C_ACCENT, pygame.Rect(rect), width=2, border_radius=_s(18))
        cx = self.width // 2
        self.screen.blit(t1, t1.get_rect(centerx=cx, y=rect[1] + _s(22)))
        if t3:
            self.screen.blit(t3, t3.get_rect(centerx=cx, bottom=rect[1] + rect[3] - _s(18)))
        self.screen.blit(t2, t2.get_rect(centerx=cx, y=rect[1] + _s(28) + t1.get_height()))

    # ── grid geometry (the rail and the category pill take some room) ──────────
    RAIL_W = _s(185)

    def _rail_w(self):
        return self.RAIL_W if self.rail_open and self._has_rail() else 0

    def _pill_h(self):
        return _s(40) if self._has_rail() and len(self._group_list()) > 1 else 0

    def _grid_top(self):
        return self.GRID_TOP + self._pill_h()

    def _grid_cols(self):
        cell_w = self.icon_size + self.icon_gap
        avail  = self.width - self._rail_w() - _s(24)
        return max(1, min(self.columns, (avail + self.icon_gap) // cell_w))

    def move_cursor(self, dx, dy):
        if not self.entries:
            return
        total = len(self.entries)
        cols  = self._grid_cols()
        if dx:
            self.cursor = (self.cursor + dx) % total
        if dy:
            nxt = self.cursor + dy * cols
            if 0 <= nxt < total:
                self.cursor = nxt
            elif dy > 0 and self.cursor // cols < (total - 1) // cols:
                self.cursor = total - 1   # last row is partial — land on its last item
        self._scroll_to_cursor()

    def _cell_h(self):
        return int(self.icon_size * 1.5) + self.icon_gap + 22

    def _scroll_to_cursor(self):
        cell_h  = self._cell_h()
        vis_h   = self.height - self._grid_top() - self.BOTTOMBAR_H - self.icon_gap * 2
        row_top = (self.cursor // self._grid_cols()) * cell_h
        if row_top - self.target_sy < 0:
            self.target_sy = float(row_top)
        elif row_top - self.target_sy + cell_h > vis_h:
            self.target_sy = float(row_top + cell_h - vis_h)

    def _action(self, btn, src="key"):
        # Some controller drivers (e.g. Steam Input) report one physical press
        # twice: as a keyboard key AND as a controller input (and some pads
        # report the D-pad as both a hat and an axis). Drop the duplicate.
        now = time.time()
        self._note_input(src, now)
        if now < getattr(self, "_input_block_until", 0.0):
            if btn == "A":
                self._dbg_log(f"A from {src} ignored (cooldown)")
            return
        if btn == "A" and getattr(self, "_a_gate", False):
            self._dbg_log(f"A from {src} ignored (waiting for release)")
            return
        last_t, last_src = self._last_press.get(btn, (0.0, None))
        self._last_press[btn] = (now, src)
        if btn in ("up", "down", "left", "right"):
            # Directions: only drop the same direction from ANOTHER source,
            # so holding the D-pad still auto-repeats normally.
            if src != last_src and now - last_t < 0.15:
                return
        elif now - last_t < 0.25:
            return

        # F1 keyboard-shortcuts panel: any back/confirm button closes it
        if self.show_keys:
            if btn in ("A", "B", "start", "back"):
                self.show_keys = False
                self._block_launch()
            elif btn in ("left", "right", "LB", "RB"):
                step = -1 if btn in ("left", "LB") else 1
                self._keys_page = (self._keys_page + step) % len(self.HELP_PAGES)
            return

        # Cover picker overlay takes priority over everything else.
        if self.cover_picker is not None:
            result = self.cover_picker.handle_button(btn)
            if result == "close":
                self.cover_picker = None
                pygame.event.set_grab(True)
                self._block_launch()
            elif isinstance(result, tuple) and result[0] == "pick":
                self._apply_picked_cover(result[1])
            return

        if self.game_menu is not None:
            self._game_menu_action(btn)
            return

        if self.pair_mode is not None:
            if self.pair_mode == "manual" and btn in ("B", "back", "start"):
                self.close_pairing()
                self._block_launch()
            return                                   # nothing else while pairing

        if self.confirm_exit:
            if btn in ("up", "down", "left", "right"):
                self._power_nav(btn)
            elif btn == "A":
                act = self.POWER_OPTIONS[self.exit_cursor][0]
                if act == "desktop":
                    self.confirm_exit = False
                    self.exit_cursor  = 0
                    self.go_to_desktop()
                    return
                if act in ("pair", "audio"):
                    self.confirm_exit = False
                    self.exit_cursor  = 0
                    self.open_pairing("manual", "audio" if act == "audio" else "controller")
                    return
                self._save_config()
                pygame.quit()
                import subprocess
                if act == "exit":
                    sys.exit()
                elif act == "sleep":
                    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=False)
                    sys.exit()
                elif act == "restart":
                    subprocess.run(["shutdown", "/r", "/t", "0"], check=False)
                    sys.exit()
                elif act == "shutdown":
                    subprocess.run(["shutdown", "/s", "/t", "0"], check=False)
                    sys.exit()
            elif btn == "B":
                self.confirm_exit = False
                self.exit_cursor  = 0
                self._block_launch()
            return

        if self.prompt is not None:
            self.prompt._kbd_button(btn)
            if self.prompt.done:
                self._finish_prompt()
            return

        if self.opts_menu is not None:
            self._opts_action(btn)
            if self.opts_menu is None and self.cat_menu is None and self.group_menu is None \
                    and self.manage is None:
                self._block_launch()
            return

        if self.group_menu is not None:
            self._group_menu_action(btn)
            if self.group_menu is None:
                self._block_launch()
            return

        if self.cat_menu is not None:
            self._cat_menu_action(btn)
            if self.cat_menu is None:      # menu just closed
                self._block_launch()
            return

        if self.manage is not None:
            self._manage_action(btn)
            if self.manage is None:
                self._block_launch()
            return

        if self.rail_open:
            if not self._has_rail():
                self.rail_open = False
            elif self._rail_action(btn):
                return

        typing = self.tab == self.TAB_SETTINGS and (self.settings.busy()
                                                    or self.settings_leave is not None)
        if btn == "LB" and not typing:
            self.switch_tab(-1)
            return
        if btn == "RB" and not typing:
            self.switch_tab(1)
            return

        if self.tab == self.TAB_SETTINGS and self.settings_leave is not None:
            result = self._settings_leave_action(btn)
        elif self.tab == self.TAB_SETTINGS:
            result = self.settings.handle_button(btn)
            if result == "back" and self._settings_dirty():
                self.settings_leave = {"cursor": 0}      # Save / Discard / Keep editing
                return
        if self.tab == self.TAB_SETTINGS:
            if result == "back":
                self.tab = self.last_cat_tab
                self._refresh_view(reset=True)
            elif result == "save":
                # Remember the old values so the pop-up can say what changed
                before = {opt[1]: self.config.get(opt[1]) for opt in SettingsScreen.OPTIONS}
                # Settings works on a copy — never let it overwrite category data
                self.config.update({k: v for k, v in self.settings.config.items()
                                    if k not in ("categories", "groups", "last_tab")})
                self.columns   = self.config["columns"]
                self.icon_size = self.config["icon_size"]
                set_button_style(self.config.get("button_style", "Xbox"))
                set_accent(self.config.get("accent", "Blue"))
                spd = self.config["scroll_speed"]
                self.rep_del  = {"Slow": 0.5,  "Normal": 0.32, "Fast": 0.18}[spd]
                self.rep_rate = {"Slow": 0.20, "Normal": 0.11, "Fast": 0.06}[spd]
                self.path = self.config["start_folder"]
                self._save_config()
                self._apply_startup(
                    before.get("startup_with_windows") != self.config.get("startup_with_windows"),
                    before.get("secure_desktop") != self.config.get("secure_desktop"))
                self.tab = self.last_cat_tab
                t0 = time.time()
                self._scan()
                if self.status_color == C_RED and self.status_time >= t0:
                    return   # keep the scan's error (e.g. folder not found) visible
                if self.config.get("secure_desktop") and not (
                        getattr(sys, "frozen", False) and is_elevated()):
                    self.set_status("Controller on UAC & Sign-in works only in the "
                                    "installed GameClub (it runs as administrator)", error=True)
                    return
                self.set_status(self._settings_change_summary(before))
            return

        if btn == "A":
            self.open_selected()
        elif btn == "X":
            self.open_options()
        elif btn == "Y":
            self.open_cover_picker()
        elif btn == "back":
            if self._has_rail():
                self.open_rail()            # VIEW / F2: categories rail
            else:
                self.open_manage()          # Apps tab: VIEW still opens Manage
        elif btn == "manage":
            self.open_manage()              # Delete key
        elif btn in ("LT", "RT"):
            if self._has_rail():
                self._step_group(-1 if btn == "LT" else 1)
        elif btn == "RS":
            self.cycle_sort()
        elif btn == "start":
            self.confirm_exit = True
        elif btn == "up":
            self.move_cursor(0, -1)
        elif btn == "down":
            self.move_cursor(0, 1)
        elif btn == "left":
            self.move_cursor(-1, 0)
        elif btn == "right":
            self.move_cursor(1, 0)

    # ── Game tracking: come back when the game closes ─────────────────────────
    GAME_GONE_SECS  = 3.0    # game windows must stay gone this long (splash → game gaps)
    GRACE_SECS      = 30     # after that, a new game window still hands the screen back
    DESKTOP_SECS    = 3.0    # desktop / nothing in front this long → come back anyway
    GIVE_UP_SECS    = 600    # stop waiting for a game that never showed up
    IDLE_SECS       = 1.5    # desktop-only in front this long → come back

    def _snapshot_windows(self):
        """Windows that already existed — these never count as the game."""
        if sys.platform != "win32":
            return set()
        try:
            return _win_all_visible()
        except Exception:  # noqa: BLE001
            return set()

    def _begin_tracking(self, before, launched_launcher):
        self._grace = None
        self._launched_launcher = launched_launcher
        self._game = {"t": time.time(), "before": set(before), "hwnds": set(),
                      "kind": {}, "gone_since": None}
        self._idle_since = None

    def _is_launcher_window(self, g, hwnd):
        """True for windows that are NOT the game: store launchers / their helper
        programs (unless the launcher itself is what was opened) and overlays."""
        k = g["kind"].get(hwnd)
        if k is None:
            exe = _win_process_exe(hwnd)
            if exe in OVERLAY_EXES or "joyxoff" in exe:
                k = "overlay"
            elif exe in LAUNCHER_EXES and not self._launched_launcher:
                k = "launcher"
            else:
                k = "game"
            g["kind"][hwnd] = k
            self._dbg_log(f"window {hwnd} '{exe}' -> {k}")
        return k != "game"

    def _come_back(self, fg):
        """Bring the app to the front; minimize a store launcher that's in the way."""
        self._dbg_log(f"come back (front was '{_win_process_exe(fg) if fg else 'none'}')")
        import ctypes
        if fg and fg != self._hwnd and _win_process_exe(fg) in LAUNCHER_EXES:
            ctypes.windll.user32.ShowWindow(fg, 6)              # SW_MINIMIZE
        _win_restore_and_focus(self._hwnd)

    def _watch_foreground(self):
        """After a launch, follow the game's own windows.

        • While the game is starting, anything may be in front (login, update,
          launcher pop-ups) — the app stays out of the way.
        • Every new window that isn't a store launcher counts as the game.
        • When all the game's windows are gone (for a couple of seconds),
          the app comes to the front — whatever window is there.
        • With no game being tracked, the app comes back when only the desktop
          is left in front.
        """
        if not self._hwnd or sys.platform != "win32":
            return
        now = time.time()
        if now - self._watch_t < 0.5:
            return
        self._watch_t = now
        try:
            import ctypes
            u32 = ctypes.windll.user32
            fg, cls = _win_foreground()
            ours_active = fg == self._hwnd and not u32.IsIconic(self._hwnd)
            # "Nothing in front": desktop, no window, or a window that is hidden or
            # minimized (Windows can leave focus on a closing launcher's hidden window)
            desktop_fg  = fg != self._hwnd and (
                cls in _IDLE_WINDOW_CLASSES or not u32.IsWindowVisible(fg) or u32.IsIconic(fg))
            # If GAMES is visible on screen meanwhile, the player is looking at it:
            # take focus back quickly so it never sits there looking frozen.
            ours_visible = not u32.IsIconic(self._hwnd)
            idle_wait    = 0.5 if ours_visible else self.IDLE_SECS
            if fg != getattr(self, "_last_fg", None):
                self._last_fg = fg
                who = "GAMES" if fg == self._hwnd else (
                    "desktop/none" if desktop_fg else (_win_process_exe(fg) or "?"))
                self._dbg_log(f"foreground -> {who}")

            if self._desktop_mode:
                return                        # player chose the desktop — leave it alone

            g = self._game
            if g:
                # Collect the game's windows: new big windows + whatever is in front
                cands = [h for h in _win_big_windows() if h not in g["before"]]
                if fg and fg != self._hwnd and not desktop_fg and fg not in g["before"]:
                    cands.append(fg)
                for h in cands:
                    if h not in g["hwnds"] and not self._is_launcher_window(g, h):
                        g["hwnds"].add(h)

                if g["hwnds"]:
                    alive = any(u32.IsWindow(h) and u32.IsWindowVisible(h) for h in g["hwnds"])
                    # Only the desktop (or nothing) in front for a few seconds: the
                    # game is closed or minimized away — come back regardless, so the
                    # app is never left visible-but-unfocused (looks frozen).
                    desktop_long = False
                    if desktop_fg:
                        self._idle_since = self._idle_since or now
                        desktop_long = now - self._idle_since >= (
                            idle_wait if ours_visible else self.DESKTOP_SECS)
                    else:
                        self._idle_since = None
                    if alive and not desktop_long:
                        g["gone_since"] = None
                        return
                    if g["gone_since"] is None:
                        g["gone_since"] = now
                    if desktop_long or now - g["gone_since"] >= self.GAME_GONE_SECS:
                        self._dbg_log("game closed -> coming back" if not desktop_long
                                      else "nothing in front -> coming back")
                        self._idle_since = None
                        self._game = None             # the game has closed (probably)
                        play = dict(self._play) if self._play else None
                        if not ours_active:
                            self._come_back(fg)
                        self._end_play()
                        # …unless a new window shows up soon: e.g. a "Play / Settings"
                        # dialog closed and the real game is still loading.
                        self._grace = {"until": now + self.GRACE_SECS, "play": play,
                                       "before": _win_all_visible(),
                                       "launcher": self._launched_launcher}
                    return

                # Game not seen yet — still starting (login / update / launcher)
                if ours_active and now - g["t"] > 90:
                    self._game = None                 # nothing started; we're in front anyway
                elif desktop_fg:
                    self._idle_since = self._idle_since or now
                    if now - self._idle_since >= self.IDLE_SECS * 2:
                        self._game = None             # launch abandoned, launcher closed
                        self._idle_since = None
                        self._come_back(fg)
                else:
                    self._idle_since = None
                    if now - g["t"] > self.GIVE_UP_SECS:
                        self._game = None
                return

            # Just came back from a game: if its real window appears now, hand over again
            gr = getattr(self, "_grace", None)
            if gr:
                if now > gr["until"]:
                    self._grace = None
                else:
                    self._launched_launcher = gr["launcher"]
                    probe = {"kind": {}}
                    new = [h for h in _win_big_windows() if h not in gr["before"]
                           and not self._is_launcher_window(probe, h)]
                    if new:
                        self._grace = None
                        self._begin_tracking(gr["before"], gr["launcher"])
                        self._game["hwnds"].add(new[0])
                        if gr["play"]:                # keep counting the same session
                            self._play = {**gr["play"], "start": now}
                        pygame.display.iconify()
                        _win_bring_to_front(new[0])
                        return

            # No game being tracked: come back when only the desktop is in front
            if desktop_fg:
                self._idle_since = self._idle_since or now
                if now - self._idle_since >= idle_wait:
                    self._idle_since = None
                    self._dbg_log("nothing in front -> coming back")
                    _win_restore_and_focus(self._hwnd)
            else:
                self._idle_since = None
        except Exception:  # noqa: BLE001
            pass

    def _poll_joy(self):
        now = time.time()
        if not self.joy:
            if now - self._joy_retry_t > 2.0:
                self._joy_retry_t = now
                pygame.joystick.quit()
                pygame.joystick.init()
                self._init_joy()
            return

        if self.joy.get_numhats() > 0:
            hat     = self.joy.get_hat(0)
            hat_map = {(0, 1): "up", (0, -1): "down", (-1, 0): "left", (1, 0): "right"}
            for hv, hn in hat_map.items():
                key = "hat_" + hn
                if hat == hv:
                    if key not in self.held:
                        self.held[key] = now
                        self._action(hn, "hat")
                    elif now - self.held[key] > self.rep_del:
                        if now - self.held.get(key + "_t", 0) > self.rep_rate:
                            self.held[key + "_t"] = now
                            self._action(hn, "hat")
                else:
                    self.held.pop(key, None)
                    self.held.pop(key + "_t", None)

        if self.joy.get_numaxes() >= 2:
            ax = self.joy.get_axis(0)
            ay = self.joy.get_axis(1)
            for key, active, act in [("sl", ax < -self.dead, "left"), ("sr", ax > self.dead, "right"),
                                      ("su", ay < -self.dead, "up"),   ("sd", ay > self.dead, "down")]:
                if active:
                    if key not in self.held:
                        self.held[key] = now
                        self._action(act, "axis")
                    elif now - self.held[key] > self.rep_del:
                        if now - self.held.get(key + "_t", 0) > self.rep_rate:
                            self.held[key + "_t"] = now
                            self._action(act, "axis")
                else:
                    self.held.pop(key, None)
                    self.held.pop(key + "_t", None)

        # Triggers (LT / RT): one press each time they're pulled past halfway.
        # They rest at -1 (XInput) or 0 depending on the driver — 0.5 works for both.
        n = self.joy.get_numaxes()
        for name, axis in (("LT", 4), ("RT", 5)):
            pulled = n > axis and self.joy.get_axis(axis) > 0.5
            if pulled and not self._trig_held[name]:
                self._action(name, "joy")
            self._trig_held[name] = pulled

    # ── Background: wallpaper / solid ─────────────────────────────────────────
    BG_FADE = 0.35   # seconds for the cross-fade when the selection changes

    def _ui_cfg(self, key, default=None):
        """Config value, using the not-yet-saved one while on the Settings tab."""
        src = self.settings.config if self.tab == self.TAB_SETTINGS else self.config
        return src.get(key, self.config.get(key, default))

    def _cover_fill(self, surf, dim_alpha):
        """Scale a surface to cover the screen (center-crop) and darken it."""
        sw, sh = surf.get_size()
        k  = max(self.width / sw, self.height / sh)
        sc = pygame.transform.smoothscale(surf, (max(1, int(sw * k)), max(1, int(sh * k))))
        out = pygame.Surface((self.width, self.height))
        out.blit(sc, ((self.width - sc.get_width()) // 2, (self.height - sc.get_height()) // 2))
        shade = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        shade.fill((*C_BG, dim_alpha))
        out.blit(shade, (0, 0))
        return out

    def _bg_target(self):
        """(key, builder) for the background that should be showing now."""
        mode = self._ui_cfg("background", "Solid")
        if mode == "Wallpaper":
            path = self._ui_cfg("wallpaper", "")
            if path and os.path.isfile(path):
                blur = self._ui_cfg("wallpaper_blur", "Off")
                return (("wall", path, blur, self.width, self.height),
                        lambda: self._build_wallpaper(path, blur))
            return None, None
        return None, None

    # Wallpaper Blur → width the image is shrunk to before scaling back up
    # (smaller = blurrier). None = no blur.
    WALL_BLUR = {"Off": None, "Light": 320, "Medium": 140, "Strong": 60}

    def _blur_surface(self, surf, detail):
        """Blur a screen-sized surface by shrinking it and scaling it back up."""
        w, h = surf.get_size()
        small = pygame.transform.smoothscale(surf, (detail, max(1, int(detail * h / w))))
        mid   = pygame.transform.smoothscale(small, (detail * 3, max(1, int(detail * 3 * h / w))))
        return pygame.transform.smoothscale(mid, (w, h))

    def _build_wallpaper(self, path, blur="Off"):
        try:
            try:
                from PIL import Image as PilImage  # type: ignore[import]
                img = PilImage.open(path).convert("RGB")
                img.thumbnail((self.width * 2, self.height * 2))
                surf = pygame.image.fromstring(img.tobytes(), img.size, "RGB")
            except ImportError:
                surf = pygame.image.load(path)
            detail = self.WALL_BLUR.get(blur)
            if detail:
                # cover-crop first so the blur is even across the screen
                surf = self._blur_surface(self._cover_fill(surf, 0), detail)
            return self._cover_fill(surf, 120)
        except Exception:  # noqa: BLE001
            return None

    def _draw_bg(self):
        if not hasattr(self, "_bg_cache"):
            self._bg_cache, self._bg_key, self._bg_cur = {}, None, None
            self._bg_prev, self._bg_t = None, 0.0
        key, build = self._bg_target()
        # Wait until the selection rests for a moment before building a new
        # background, so holding the D-pad to scroll stays smooth.
        now = time.time()
        if key != getattr(self, "_bg_want", (None, 0))[0]:
            self._bg_want = (key, now)
        settled = key is None or key in self._bg_cache or now - self._bg_want[1] >= 0.12
        if key != self._bg_key and settled:
            surf = None
            if key is not None:
                surf = self._bg_cache.get(key)
                if surf is None and build is not None:
                    surf = build()
                    if surf is not None:
                        if len(self._bg_cache) > 24:          # keep memory in check
                            self._bg_cache.pop(next(iter(self._bg_cache)))
                        self._bg_cache[key] = surf
            if surf is not None or key is None:
                self._bg_prev, self._bg_cur = self._bg_cur, surf
                self._bg_key, self._bg_t = key, time.time()

        self.screen.fill(C_BG)
        k = min(1.0, (time.time() - self._bg_t) / self.BG_FADE)
        if self._bg_prev is not None and k < 1.0:
            self._bg_prev.set_alpha(255)
            self.screen.blit(self._bg_prev, (0, 0))
        if self._bg_cur is not None:
            self._bg_cur.set_alpha(int(255 * k))
            self.screen.blit(self._bg_cur, (0, 0))
        elif self._bg_prev is not None and k < 1.0:     # fading out to solid
            shade = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            shade.fill((*C_BG, int(255 * k)))
            self.screen.blit(shade, (0, 0))

    def _fill_bar(self, rect):
        """Top / tab / bottom bars: slightly see-through over a picture background."""
        if getattr(self, "_bg_cur", None) is None:
            pygame.draw.rect(self.screen, C_PANEL, rect)
            return
        bar = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        bar.fill((*C_PANEL, 215))
        self.screen.blit(bar, (rect[0], rect[1]))

    def _draw_topbar(self):
        self._fill_bar((0, 0, self.width, self.TOPBAR_H))
        pygame.draw.line(self.screen, C_GRAY, (0, self.TOPBAR_H), (self.width, self.TOPBAR_H), 1)
        mid_y = self.TOPBAR_H // 2
        # 24-hour clock in place of the old "GAMES" title (same font, size and color)
        t = self.fonts["title"].render(time.strftime("%H:%M"), True, C_ACCENT2)
        self.screen.blit(t, t.get_rect(midleft=(20, mid_y)))
        right = self.width - _s(20)
        if self.joy:
            self._poll_battery()
            bw = draw_battery(self.screen, self.fonts["hint"], right, mid_y,
                              getattr(self, "_battery", None), C_GREEN)
            if bw:
                right -= bw + _s(14)
            ci = self.fonts["hint"].render("Controller: " + self.joy.get_name()[:50], True, C_GREEN)
        else:
            ci = self.fonts["hint"].render("No Controller  -  Use Arrow Keys", True, C_YELLOW)
        self.screen.blit(ci, ci.get_rect(midright=(right, mid_y)))

    BATTERY_SECS = 30     # how often the controller battery is read

    def _poll_battery(self):
        """Refresh the battery reading in the background every BATTERY_SECS."""
        now = time.time()
        job = getattr(self, "_bat_job", None)
        if job is not None and job.done():
            self._bat_job = None
            try:
                res = job.result()
            except Exception:  # noqa: BLE001
                res = None
            if res is None and self.joy is not None:
                try:                                   # SDL's own (coarse) reading
                    lvl = _SDL_POWER.get(self.joy.get_power_level())
                except (AttributeError, pygame.error):
                    lvl = None
                if lvl == "wired":
                    res = {"pct": None, "level": None, "wired": True, "charging": False}
                elif lvl:
                    res = {"pct": None, "level": lvl, "wired": False, "charging": False}
            if res != getattr(self, "_battery", None):
                self._dbg_log(f"controller battery: {res}")
            self._battery = res
        if job is None and now - getattr(self, "_bat_t", 0.0) >= self.BATTERY_SECS:
            self._bat_t = now
            self._bat_job = _icon_executor.submit(read_battery)

    def _draw_tabbar(self):
        """Tabs centred. With a controller, LB / RB sit right next to the first
        and last tab; with only a keyboard the "Tab · Switch Tab" hint stays on
        the right."""
        y  = self.TOPBAR_H
        h  = self.TABBAR_H
        tw = 190
        self._fill_bar((0, y, self.width, h))
        n     = len(self.TAB_LABELS)
        total = n * tw + (n - 1) * 8
        x0    = (self.width - total) // 2
        for i, label in enumerate(self.TAB_LABELS):
            tr     = pygame.Rect(x0 + i * (tw + 8), y + 5, tw, h - 9)
            active = self.tab == i
            draw_tab(self.screen, tr, active)
            col = C_WHITE if active else C_TEXT_DIM
            lt  = self.fonts["tab"].render(label, True, col)
            self.screen.blit(lt, lt.get_rect(center=tr.center))
        cy, font = y + h // 2, self.fonts["hint"]
        if _input_mode == "kbd":
            tab_hints = [("RB", "Switch Tab")]
            hw = hints_width(font, tab_hints)
            draw_hints(self.screen, font, tab_hints, self.width - hw - _s(20), cy)
        else:
            lbw = _btn_size(font, "LB")[0]
            draw_button(self.screen, font, "LB", x0 - _s(12) - lbw, cy)
            draw_button(self.screen, font, "RB", x0 + total + _s(12), cy)
        pygame.draw.line(self.screen, C_ACCENT, (0, y + h - 1), (self.width, y + h - 1), 2)

    def _draw_grid(self):
        cols     = self._grid_cols()
        isz      = self.icon_size
        gap      = self.icon_gap
        card_h   = int(isz * 1.5)          # portrait card height
        cell_w   = isz + gap
        cell_h   = self._cell_h()
        left     = self._rail_w()
        area_w   = self.width - left
        top      = self._grid_top()
        bot      = self.height - self.BOTTOMBAR_H
        cat      = self._current_cat()
        if self._has_rail():
            self._draw_group_pill(left)

        if not self.entries:
            cx = left + area_w // 2
            msg = self.fonts["big"].render(f"No {CATEGORY_NAMES[cat]} yet", True, C_TEXT_DIM)
            self.screen.blit(msg, msg.get_rect(center=(cx, (top + bot) // 2)))
            sub = self.fonts["hint"].render(
                f"Press {btn_text('X')} on a shortcut in another tab \u2192 Move to tab \u2192 {CATEGORY_NAMES[cat]}",
                True, C_TEXT_DIM)
            self.screen.blit(sub, sub.get_rect(center=(cx, (top + bot) // 2 + _s(50))))
            if self.rail_open:
                self._draw_rail()
            return

        total_rows      = math.ceil(len(self.entries) / cols)
        total_content_h = total_rows * cell_h + gap
        total_w = cols * cell_w - gap
        sx      = left + (area_w - total_w) // 2
        self.scroll_y += (self.target_sy - self.scroll_y) * 0.15
        self.screen.set_clip(pygame.Rect(left, top, area_w, bot - top))

        allow_search = cat != "apps"
        pending_labels = []   # draw labels after clip is cleared
        for i, entry in enumerate(self.entries):
            row   = i // cols
            col   = i % cols
            x     = sx + col * cell_w
            y     = top + gap + row * cell_h - self.scroll_y
            if y + cell_h < top or y > bot:
                continue
            sel   = i == self.cursor
            name  = entry["file"]
            color = file_color(name, False)
            badge = file_badge(name, False)
            ico   = get_file_icon(entry["path"], name, isz, allow_search)
            draw_icon(self.screen, x, y, isz, card_h, color, badge, selected=sel, icon_surf=ico)
            dn = fit_text(self.fonts["name"], entry["name"], cell_w - _s(6))
            nt = self.fonts["name"].render(dn, True, C_WHITE if sel else C_TEXT)
            pending_labels.append((nt, x + isz // 2 - nt.get_width() // 2, y + card_h + 4))

        self.screen.set_clip(None)
        # Draw labels unclipped — bottombar drawn on top will mask any overlap
        # (but never under the pill row / rail)
        self.screen.set_clip(pygame.Rect(left, top, area_w, self.height - top))
        for nt, lx, ly in pending_labels:
            self.screen.blit(nt, (lx, ly))
        self.screen.set_clip(None)

        vis_h = bot - top
        if total_content_h > vis_h:
            sbx = self.width - 10
            pygame.draw.rect(self.screen, C_GRAY, (sbx, top, 5, vis_h), border_radius=3)
            th  = max(36, int(vis_h * vis_h / total_content_h))
            ty  = top + int((self.scroll_y / total_content_h) * vis_h)
            pygame.draw.rect(self.screen, C_ACCENT, (sbx, ty, 5, th), border_radius=3)

        if self.rail_open:
            # The rail has the focus: dim the games a little
            shade = pygame.Surface((area_w, bot - self.GRID_TOP), pygame.SRCALPHA)
            shade.fill((*C_BG, 110))
            self.screen.blit(shade, (left, self.GRID_TOP))
            self._draw_rail()

    def _draw_group_pill(self, left):
        """Current category, top-left above the grid (+ how to open the rail)."""
        if not self._pill_h():
            return
        sel   = self.group_sel.get(self.tab, GROUP_ALL)
        count = dict(self._group_list()).get(sel, 0)
        font  = self.fonts["tab"]
        txt   = f"{self._group_label(sel)}   {count}"
        dot   = SYSTEM_COLOURS.get(sel) if self.tab == self.TAB_EMU and sel != GROUP_ALL else None
        if self.tab == self.TAB_EMU and sel not in (GROUP_ALL, GROUP_NONE) and dot is None:
            dot = (150, 160, 178)
        pad   = _s(12) + (_s(14) if dot else 0)
        h     = _s(26)
        r     = pygame.Rect(left + _s(16), self.GRID_TOP + (self._pill_h() - h) // 2,
                            font.size(txt)[0] + pad + _s(12), h)
        draw_rounded_rect(self.screen, C_ACCENT, r, radius=h // 2, alpha=60)
        pygame.draw.rect(self.screen, C_ACCENT, r, 2, border_radius=h // 2)
        if dot:
            pygame.draw.circle(self.screen, dot, (r.x + _s(14), r.centery), _s(4))
        t = font.render(txt, True, C_WHITE)
        self.screen.blit(t, (r.x + pad, r.centery - t.get_height() // 2))
        if not self.rail_open:
            draw_hints(self.screen, self.fonts["hint"], [("VIEW", self._rail_noun())],
                       r.right + _s(12), r.centery)

    def _draw_rail(self):
        """Categories rail on the left (the grid has already moved aside)."""
        top, bot = self.GRID_TOP, self.height - self.BOTTOMBAR_H
        w   = self.RAIL_W
        panel = pygame.Surface((w, bot - top), pygame.SRCALPHA)
        panel.fill((*PANEL_BOT, 245))
        self.screen.blit(panel, (0, top))
        pygame.draw.line(self.screen, C_ACCENT, (w, top), (w, bot), 2)
        head = self.fonts["hint"].render(self._rail_noun().upper(), True, C_TEXT_DIM)
        self.screen.blit(head, (_s(14), top + _s(10)))
        groups = self._group_list()
        row_h, pitch = _s(28), _s(32)
        y0   = top + _s(10) + head.get_height() + _s(8)
        fit  = max(1, (bot - y0 - _s(8)) // pitch)
        start = 0
        if len(groups) > fit:
            start = max(0, min(self.rail_cursor - fit // 2, len(groups) - fit))
        emu  = self.tab == self.TAB_EMU
        for i, (g, cnt) in enumerate(groups[start:start + fit], start):
            rr  = pygame.Rect(_s(8), y0 + (i - start) * pitch, w - _s(16), row_h)
            sel = i == self.rail_cursor
            if sel:
                draw_rounded_rect(self.screen, C_ACCENT, rr, radius=_s(7), alpha=70)
                pygame.draw.rect(self.screen, C_ACCENT, rr, 2, border_radius=_s(7))
            tx = rr.x + _s(10)
            if emu:
                col = SYSTEM_COLOURS.get(g, (150, 160, 178))
                pygame.draw.circle(self.screen, col, (rr.x + _s(12), rr.centery), _s(4))
                tx = rr.x + _s(24)
            ct = self.fonts["hint"].render(str(cnt), True, C_ACCENT2 if sel else C_TEXT_DIM)
            name = fit_text(self.fonts["ui"], self._group_label(g), rr.right - tx - ct.get_width() - _s(14))
            nt = self.fonts["ui"].render(name, True, C_WHITE if sel else C_TEXT)
            self.screen.blit(nt, (tx, rr.centery - nt.get_height() // 2))
            self.screen.blit(ct, (rr.right - ct.get_width() - _s(8), rr.centery - ct.get_height() // 2))
        if start > 0:
            draw_triangle_up = [(w // 2, y0 - _s(6)), (w // 2 - _s(6), y0 - _s(1)), (w // 2 + _s(6), y0 - _s(1))]
            pygame.draw.polygon(self.screen, C_TEXT_DIM, draw_triangle_up)
        if start + fit < len(groups):
            by = y0 + fit * pitch
            pygame.draw.polygon(self.screen, C_TEXT_DIM,
                                [(w // 2, by + _s(5)), (w // 2 - _s(6), by), (w // 2 + _s(6), by)])
        if len(groups) <= 1:
            tip = ["Put shortcuts in", "subfolders, or use", f"{btn_text('X')} → Set " +
                   ("system" if emu else "category")]
            ty = y0 + pitch + _s(6)
            for line in tip:
                lt = self.fonts["hint"].render(line, True, C_TEXT_DIM)
                self.screen.blit(lt, (_s(14), ty))
                ty += lt.get_height() + _s(2)

    TOAST_SECS = 3.0    # how long a pop-up stays fully visible
    TOAST_ANIM = 0.25   # slide/fade in and out duration

    def _draw_toast(self):
        """Pop-up notification card above the bottom bar (auto-hides)."""
        if not self.status_msg:
            return
        age   = time.time() - self.status_time
        total = self.TOAST_SECS + 2 * self.TOAST_ANIM
        if age >= total:
            self.status_msg = ""
            return
        # 0 → 1 while appearing, 1 while shown, 1 → 0 while disappearing
        if age < self.TOAST_ANIM:
            k = age / self.TOAST_ANIM
        elif age > total - self.TOAST_ANIM:
            k = (total - age) / self.TOAST_ANIM
        else:
            k = 1.0
        k = k * k * (3 - 2 * k)          # smoothstep easing

        is_err = self.status_color == C_RED
        accent = C_RED if is_err else C_GREEN
        title  = "Error" if is_err else "Notification"
        tt = self.fonts["hint"].render(title.upper(), True, accent)
        mt = self.fonts["ui"].render(self.status_msg, True, C_WHITE)

        pad_x  = _s(26)
        head_h = tt.get_height() + _s(18)       # title area above the divider
        w = min(self.width - _s(80),
                max(tt.get_width(), mt.get_width(), _s(220)) + pad_x * 2)
        h = head_h + mt.get_height() + _s(26)
        rad = _s(16)

        # Draw onto an off-screen layer (with room for the shadow) so the whole
        # card can fade in/out together.
        m     = _s(24)
        layer = pygame.Surface((w + m * 2, h + m * 2), pygame.SRCALPHA)
        rect  = (m, m, w, h)
        draw_panel(layer, rect, rad)
        pygame.draw.rect(layer, accent, pygame.Rect(rect), width=2, border_radius=rad)
        layer.blit(tt, tt.get_rect(centerx=m + w // 2, y=m + _s(10)))
        pygame.draw.line(layer, PANEL_DIV, (m + _s(16), m + head_h), (m + w - _s(16), m + head_h))
        msg_y = m + head_h + (h - head_h - mt.get_height()) // 2
        if mt.get_width() <= w - pad_x * 2:
            layer.blit(mt, mt.get_rect(centerx=m + w // 2, y=msg_y))
        else:   # very long message — left-align and clip to the card
            layer.blit(mt, (m + pad_x, msg_y),
                       area=pygame.Rect(0, 0, w - pad_x * 2, mt.get_height()))
        layer.set_alpha(int(255 * k))

        rest_y = self.height - self.BOTTOMBAR_H - h - _s(18)
        y = int(rest_y + (1 - k) * _s(30))   # slides up into place
        self.screen.blit(layer, ((self.width - w) // 2 - m, y - m))

    def _draw_bottombar(self):
        y = self.height - self.BOTTOMBAR_H
        self._fill_bar((0, y, self.width, self.BOTTOMBAR_H))
        pygame.draw.line(self.screen, C_GRAY, (0, y), (self.width, y), 1)
        mid = y + self.BOTTOMBAR_H // 2
        font  = self.fonts["hint"]
        if self.rail_open and self._has_rail():
            hints = [("A", "Choose"), ("B", ""), ("VIEW", "Cancel")]
        elif self._has_rail():
            hints = [("A", "Launch"), ("X", "Options"), ("Y", "Cover"),
                     ("VIEW", self._rail_noun()), ("START", "Power")]
            trig  = [("LT", ""), ("RT", "Previous / next")]
            room  = self.width - _s(40) - draw_keycap(pygame.Surface((1, 1)), font, "F1", 0, 0)
            if len(self._group_list()) > 1 and \
                    hints_width(font, hints[:4] + trig + hints[4:]) + _s(140) < room:
                hints = hints[:4] + trig + hints[4:]
        else:
            hints = [("A", "Launch"), ("X", "Options"), ("Y", "Cover"),
                     ("VIEW", "Manage"), ("START", "Power")]
        draw_hints(self.screen, font, hints, _s(20), mid)
        hints_end = _s(20) + hints_width(font, hints)
        # F1 opens the full keyboard-shortcuts list (shown only if it fits)
        for label in ("Keyboard shortcuts", "Keys"):
            kw = draw_keycap(pygame.Surface((1, 1)), font, "F1", 0, 0) + _s(_HINT_GAP_IN) + font.size(label)[0]
            x  = self.width - kw - _s(20)
            if x > hints_end + _s(20):
                x += draw_keycap(self.screen, font, "F1", x, mid) + _s(_HINT_GAP_IN)
                lt = font.render(label, True, C_TEXT_DIM)
                self.screen.blit(lt, (x, mid - lt.get_height() // 2))
                break

    KEY_HELP = [
        ("arrows",            "Move"),
        ("Enter",             "Launch / select"),
        ("Backspace",         "Back / cancel"),
        ("Tab",               "Next tab"),
        ("Shift+Tab",         "Previous tab"),
        ("X",                 "Options menu"),
        ("Y",                 "Choose cover"),
        ("F2",                "Categories rail"),
        ("PgUp",              "Previous category"),
        ("PgDn",              "Next category"),
        ("Del",               "Manage (uninstall / remove)"),
        ("Esc",               "Power menu"),
        ("S",                 "Change sort order"),
        ("F1",                "Show / hide this list"),
    ]

    HELP_PAGES = ("Keyboard", "Controller", "Desktop")

    def _controller_help(self, page=1):
        """(section title, [(glyphs, description)], columns) for help pages 2 and 3."""
        if page == 2:
            back = ("Back to GameClub", [(["VIEW", "+", "START"], "Hold 1 s \u2014 come back to GameClub")], 1)
            if self._joyxoff:
                return [("Outside GameClub (desktop & windowed apps)",
                         [([], "JoyXoff is running \u2014 GameClub\u2019s desktop mouse is turned off")], 1),
                        back]
            ptr = "RS" if getattr(self, "config", {}).get("mouse_stick", "Right stick") == "Right stick" else "LS"
            scl = "LS" if ptr == "RS" else "RS"
            rows = [([ptr], "Move mouse pointer"), ([scl], "Tilt: scroll"),
                    ([self._click_triggers()[0]], "Left click (hold to drag)"),
                    ([self._click_triggers()[1]], "Right click"),
                    (["RS"], "Press in: middle click"), (["D-pad"], "Arrow keys"),
                    (["VIEW", "+", "X"], "On-screen keyboard")]
            return [("Outside GameClub (desktop & windowed apps)", rows, 2), back,
                    ("Note", [([], "Turns off by itself while a full-screen game is in front")], 1)]
        outside = [(["VIEW", "+", "START"], "Hold 1 s \u2014 come back to GameClub from any window"),
                   (["VIEW", "+", "START"], "In an emulated game: menu to resume or close it")]
        if self._joyxoff:
            return [("Outside GameClub (launchers, games, pop-ups)", outside, 1),
                    ("JoyXoff is running", [([], "GameClub\u2019s controller keyboard is turned off "
                                                 "\u2014 use JoyXoff\u2019s instead")], 1)]
        outside.append((["VIEW", "+", "X"], "Keyboard & mouse for logins and Play / Settings windows"))
        inside = [(["D-pad"], "Pick a key"), (["A"], "Type"), (["B"], "Delete"),
                  (["X"], "Space"), (["Y"], "Shift"), (["LB", "/", "RB"], "Previous / next field"),
                  (["START"], "Enter"), (["RS"], "Move mouse"),
                  ([self._click_triggers()[0]], "Click"), ([self._click_triggers()[1]], "Right click"),
                  (["LS"], "Move keyboard up / down"), (["VIEW"], "Close keyboard")]
        return [("Outside GameClub (launchers, games, pop-ups)", outside, 1),
                ("While the controller keyboard is open", inside, 2)]

    def _glyphs_width(self, font, spec):
        w = 0
        for t in spec:
            if t in ("+", "/"):
                w += font.size(t)[0] + _s(10)
            elif t == "D-pad":
                w += draw_keycap(pygame.Surface((1, 1)), font, "D-pad", 0, 0) + _s(4)
            else:
                w += _btn_size(font, t)[0] + _s(4)
        return w

    def _draw_glyphs(self, font, spec, x, cy):
        for t in spec:
            if t in ("+", "/"):
                tt = font.render(t, True, C_TEXT_DIM)
                self.screen.blit(tt, (x + _s(5), cy - tt.get_height() // 2))
                x += tt.get_width() + _s(10)
            elif t == "D-pad":
                x += draw_keycap(self.screen, font, "D-pad", x, cy) + _s(4)
            else:
                x += draw_button(self.screen, font, t, x, cy) + _s(4)

    def _help_height(self, font, ui, row_h, sec_h, header_h, footer_h, pad):
        items = self.KEY_HELP
        avail = self.height - _s(24)
        cols0 = 1 if header_h + footer_h + pad * 2 + len(items) * row_h <= avail else 2
        h0 = math.ceil(len(items) / cols0) * row_h
        h1 = max(sum(sec_h + math.ceil(len(rows) / ncol) * row_h + _s(6)
                     for _t, rows, ncol in self._controller_help(p)) for p in (1, 2))
        return header_h + pad * 2 + max(h0, h1) + footer_h

    def _draw_keys_panel(self):
        """F1 help: page 1 keyboard shortcuts, page 2 controller shortcuts."""
        ov = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ov.fill((8, 10, 14, 200))
        self.screen.blit(ov, (0, 0))
        mode_before = _input_mode
        set_input_mode("pad")                       # controller page always shows pad glyphs
        font, ui = self.fonts["hint"], self.fonts["ui"]
        avail_h  = self.height - _s(24)
        # normal spacing, or a compact one when the screen is short (e.g. 720p)
        for row_h, sec_h, header_h, footer_h, pad in ((_s(32), _s(34), _s(64), _s(52), _s(14)),
                                                      (_s(26), _s(28), _s(52), _s(40), _s(8))):
            if self._help_height(font, ui, row_h, sec_h, header_h, footer_h, pad) <= avail_h:
                break

        # ── page 1 metrics (keyboard)
        items   = self.KEY_HELP
        cols0   = 1 if header_h + footer_h + pad * 2 + len(items) * row_h <= avail_h else 2
        per0    = math.ceil(len(items) / cols0)
        key_w   = max(_s(24) * 4 + _s(9), max(draw_keycap(pygame.Surface((1, 1)), font, k, 0, 0)
                                               for k, _ in items if k != "arrows"))
        colw0   = key_w + _s(18) + max(ui.size(d)[0] for _, d in items) + _s(24)
        w0, h0  = cols0 * colw0, per0 * row_h

        # ── page 2 metrics (controller)
        w1 = h1 = 0
        for p in (1, 2):                  # size for the bigger page so it doesn't jump
            sp = self._controller_help(p)
            gw = max(self._glyphs_width(font, g) for _, rows, _c in sp for g, _ in rows)
            hp = 0
            for _t, rows, ncol in sp:
                colw = gw + _s(16) + max(ui.size(d)[0] for _, d in rows) + _s(24)
                w1   = max(w1, ncol * colw)
                hp  += sec_h + math.ceil(len(rows) / ncol) * row_h + _s(6)
            h1 = max(h1, hp)
        secs    = self._controller_help(max(1, self._keys_page))
        glyph_w = max(self._glyphs_width(font, g) for _, rows, _c in secs for g, _ in rows)

        pw = min(self.width - _s(40), max(w0, w1) + _s(48))
        ph = header_h + pad * 2 + max(h0, h1) + footer_h
        px, py = (self.width - pw) // 2, (self.height - ph) // 2
        rect = (px, py, pw, ph)
        draw_panel(self.screen, rect, _s(18))

        # header: two-page tabs instead of a title
        tw, th = _s(170), min(_s(34), header_h - _s(14))
        npg = len(self.HELP_PAGES)
        tx = px + (pw - (tw * npg + _s(8) * (npg - 1))) // 2
        for i, label in enumerate(self.HELP_PAGES):
            tr = pygame.Rect(tx + i * (tw + _s(8)), py + (header_h - th) // 2, tw, th)
            draw_tab(self.screen, tr, i == self._keys_page)
            lt = self.fonts["tab"].render(label, True, C_WHITE if i == self._keys_page else C_TEXT_DIM)
            self.screen.blit(lt, lt.get_rect(center=tr.center))
        pygame.draw.line(self.screen, PANEL_DIV, (px + _s(20), py + header_h),
                         (px + pw - _s(20), py + header_h))

        top = py + header_h + pad
        if self._keys_page == 0:
            for i, (key, desc) in enumerate(items):
                c, r = divmod(i, per0)
                x  = px + _s(24) + c * ((pw - _s(40)) // cols0)
                cy = top + r * row_h + row_h // 2
                if key == "arrows":
                    kx = x
                    for d in ("left", "up", "down", "right"):
                        kx += draw_keycap(self.screen, font, "", kx, cy, arrow=d) + _s(3)
                else:
                    draw_keycap(self.screen, font, key, x, cy)
                dt = ui.render(desc, True, C_TEXT)
                self.screen.blit(dt, (x + key_w + _s(18), cy - dt.get_height() // 2))
        else:
            y = top
            for title, rows, ncol in secs:
                tt = font.render(title.upper(), True, C_ACCENT2)
                self.screen.blit(tt, (px + _s(24), y + (sec_h - tt.get_height()) // 2))
                y += sec_h
                per = math.ceil(len(rows) / ncol)
                for i, (spec, desc) in enumerate(rows):
                    c, r = divmod(i, per)
                    x  = px + _s(24) + c * ((pw - _s(40)) // ncol)
                    cy = y + r * row_h + row_h // 2
                    self._draw_glyphs(font, spec, x, cy)
                    col = C_YELLOW if not spec else C_TEXT
                    dt  = ui.render(desc, True, col)
                    self.screen.blit(dt, (x + (glyph_w + _s(16) if spec else 0), cy - dt.get_height() // 2))
                y += per * row_h + _s(6)

        fy = py + ph - footer_h
        pygame.draw.line(self.screen, PANEL_DIV, (px + _s(20), fy), (px + pw - _s(20), fy))
        lt = font.render("\u2190 \u2192  switch page    \u00b7    F1, Esc or Backspace  close",
                         True, C_TEXT_DIM)
        self.screen.blit(lt, lt.get_rect(center=(px + pw // 2, fy + footer_h // 2)))
        set_input_mode(mode_before)

    def _draw_menu_panel(self, title, subtitle, options, cursor, current=None):
        """Shared modal used by the Power and Move-to menus.
        options: list of (label, color); current: index to tag as 'current'."""
        ov = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ov.fill((8, 10, 14, 200))
        self.screen.blit(ov, (0, 0))

        row_h    = _s(50)
        row_gap  = _s(6)
        header_h = _s(64) + (_s(24) if subtitle else 0)
        footer_h = _s(52)
        body_pad = _s(14)
        pw       = _s(380)
        body_h   = len(options) * (row_h + row_gap) - row_gap
        ph       = header_h + body_pad * 2 + body_h + footer_h
        px       = (self.width  - pw) // 2
        py       = (self.height - ph) // 2
        rect     = (px, py, pw, ph)

        draw_panel(self.screen, rect, _s(18))
        draw_panel_header(self.screen, self.fonts, rect, header_h, title, subtitle)

        ry0 = py + header_h + body_pad
        for i, (label, col) in enumerate(options):
            oy  = ry0 + i * (row_h + row_gap)
            sel = i == cursor
            rr  = pygame.Rect(px + _s(16), oy, pw - _s(32), row_h)
            if sel:
                draw_row_highlight(self.screen, rr, col)
            dot_x = rr.x + _s(28)
            pygame.draw.circle(self.screen, col, (dot_x, rr.centery), _s(6) if sel else _s(5))
            if not sel:
                pygame.draw.circle(self.screen, C_PANEL, (dot_x, rr.centery), _s(3))
            txt = self.fonts["ui"].render(label, True, C_WHITE if sel else C_TEXT)
            self.screen.blit(txt, txt.get_rect(centery=rr.centery, x=dot_x + _s(18)))
            if current is not None and i == current:
                tag  = self.fonts["hint"].render("CURRENT", True, C_GREEN)
                tr   = tag.get_rect(centery=rr.centery, right=rr.right - _s(16))
                pill = tr.inflate(_s(14), _s(6))
                draw_rounded_rect(self.screen, C_GREEN, pill, radius=pill.height // 2, alpha=40)
                self.screen.blit(tag, tr)

        draw_panel_footer(self.screen, self.fonts["hint"], rect, footer_h,
                          [("A", "Select"), ("B", "Cancel")])

    # (action, label, colour) — colour None = current accent colour
    POWER_OPTIONS = [
        ("desktop",  "Desktop",       (120, 200, 140)),
        ("pair",     "Pair a controller", (90, 170, 220)),
        ("audio",    "Pair headphones",   (170, 120, 220)),
        ("exit",     "Exit App",      (150, 160, 178)),
        ("sleep",    "Sleep",         None),
        ("restart",  "Restart",       (220, 170, 40)),
        ("shutdown", "Shutdown",      (222, 72, 72)),
    ]

    # ── Desktop mouse (controller as mouse after "Go to Desktop") ─────────────
    def _fg_fullscreen(self, fg):
        """True if a window covers the whole screen (a full-screen game).
        A normal app that is only MAXIMISED (NVIDIA App, a browser…) doesn't count,
        even if its frame hangs a few pixels past the screen edges."""
        try:
            import ctypes
            from ctypes import wintypes
            u32 = ctypes.windll.user32
            r = wintypes.RECT()
            u32.GetWindowRect(fg, ctypes.byref(r))
            covers = r.left <= 0 and r.top <= 0 and r.right >= self.width and r.bottom >= self.height
            if not covers:
                return False
            u32.GetWindowLongW.restype = ctypes.c_long
            style = u32.GetWindowLongW(fg, -16) & 0xFFFFFFFF          # GWL_STYLE
            resizable = bool(style & (0x00C00000 | 0x00040000))       # WS_CAPTION / WS_THICKFRAME
            if u32.IsZoomed(fg) and resizable:
                result = False                                         # maximized app window
            else:
                result = True
            key = (fg, result)
            if key != getattr(self, "_fs_logged", None):
                self._fs_logged = key
                self._dbg_log(f"full-screen check: {_win_process_exe(fg) or '?'} "
                              f"rect=({r.left},{r.top},{r.right},{r.bottom}) style=0x{style:08X} "
                              f"maximised={bool(u32.IsZoomed(fg))} -> "
                              f"{'full-screen (mouse off)' if result else 'maximised window (mouse on)'}")
            return result
        except Exception:  # noqa: BLE001
            return False

    def _pointer_px_per_frame(self, mag, dz):
        """Stick deflection → pointer pixels per frame, from Mouse Pointer Speed."""
        speed = max(1, min(10, int(self.config.get("mouse_speed", 3) or 3)))
        top_px_s = (200 + 230 * (speed - 1)) * (self.width / 1920)
        return ((mag - dz) / (1 - dz)) ** 1.8 * (top_px_s / 60)

    def _clicks_swapped(self):
        return getattr(self, "config", {}).get("mouse_clicks", "").startswith("LT left")

    def _click_triggers(self):
        """('RT', 'LT') = (left-click trigger, right-click trigger) per Mouse Clicks."""
        return ("LT", "RT") if self._clicks_swapped() else ("RT", "LT")

    def _desktop_mouse_ready(self):
        """Mouse mode: whenever GAMES is in the background (Go to Desktop, Alt+Tab to
        a browser…) — but never over a full-screen app, and never over a game that
        was launched from GAMES (even a windowed one).
        Exception: something started from the APPS tab (a browser, Kodi, a media
        player…) always gets mouse mode, even when it runs full screen."""
        if not (self.joy and not self._joyxoff and sys.platform == "win32"):
            return False
        if not self.config.get("desktop_mouse", True):
            return False                            # switched off in Settings
        try:
            fg, cls = _win_foreground()
        except Exception:  # noqa: BLE001
            return False
        if fg and fg == getattr(self, "_hwnd", None):
            return False                            # GAMES itself is in front
        if not fg or cls in _IDLE_WINDOW_CLASSES:
            return True
        g = getattr(self, "_game", None)
        entry = getattr(self, "_game_entry", None)
        from_apps = bool(g) and bool(entry) and entry.get("cat") == "apps"
        if g and fg in g.get("hwnds", ()):
            return from_apps                        # launched app: yes / game: no
        if from_apps:
            # a window the launched app opened later (e.g. its full-screen player)
            tgt = os.path.basename((entry.get("target") or "").replace("\\", "/")).lower()
            if tgt.endswith(".exe") and _win_process_exe(fg) == tgt:
                return True
        return not self._fg_fullscreen(fg)          # never over a full-screen app

    def _release_desktop_mouse(self):
        dm = getattr(self, "_dm", None)
        if not dm:
            return
        try:
            if dm["rt"]:
                mouse_button(False)
            if dm["lt"]:
                mouse_button(False, right=True)
            if dm["r3"]:
                mouse_middle(False)
        except Exception:  # noqa: BLE001
            pass
        self._dm = None

    def _dm_telemetry(self, dm, mx, my, pos, now):
        """Once a second while moving: log intended vs actual pointer travel and
        what is in front — to diagnose 'doubled' movement in menus."""
        t = dm.setdefault("tel", {"t": now, "want": 0, "start": pos})
        t["want"] += abs(mx) + abs(my)
        if now - t["t"] >= 1.0:
            x, y = cursor_pos()
            got = abs(x - t["start"][0]) + abs(y - t["start"][1])
            try:
                fg, cls = _win_foreground()
                who = f"{_win_process_exe(fg) or '?'} [{cls}]"
            except Exception:  # noqa: BLE001
                who = "?"
            self._dbg_log(f"desktop mouse: wanted {t['want']} px, pointer moved {got} px, "
                          f"front: {who}")
            dm["tel"] = {"t": now, "want": 0, "start": (x, y)}

    def _dm_check_other_mover(self, dm, stick_moving, now):
        """Returns True while another program is driving the pointer from the
        controller (we then pause pointer, clicks and scrolling)."""
        hist = dm.setdefault("hist", deque(maxlen=10))
        if dm.get("paused"):
            # resume once the stick moves but the pointer doesn't (the other mapper stopped)
            pos = cursor_pos()
            if stick_moving:
                if pos == dm.get("pause_pos"):
                    dm["still_t"] = dm.get("still_t") or now
                    if now - dm["still_t"] > 0.3:
                        dm["paused"] = False
                        hist.clear()
                        self._dbg_log("desktop mouse: other mouse program stopped -> resuming")
                else:
                    dm["still_t"] = None
            dm["pause_pos"] = pos
            return dm.get("paused", False)
        exp, last = dm.get("expect"), dm.get("last")
        if stick_moving and exp and last:
            x, y = cursor_pos()
            ex, ey = x - exp[0], y - exp[1]          # movement we did NOT make
            l2 = last[0] ** 2 + last[1] ** 2
            hist.append(l2 >= 4 and (ex * last[0] + ey * last[1]) > 0.5 * l2)
            if sum(hist) >= 6:
                dm["paused"], dm["pause_pos"], dm["still_t"] = True, (x, y), None
                for name, right in (("rt", False), ("lt", True)):
                    if dm[name]:
                        mouse_button(False, right=right)
                        dm[name] = False
                self._dbg_log("desktop mouse: another program is also moving the pointer "
                              "-> pausing (no double movement / double clicks)")
                return True
        return False

    def _poll_game_cursor(self):
        """Hide the pointer while a full-screen game from PC Games / Emulation is in
        front and the controller is in use. The real mouse brings it back at once;
        using the pad again hides it again. Restored when the game isn't in front."""
        if sys.platform != "win32":
            return
        cg = getattr(self, "_cg", None)
        if cg is None:
            cg = self._cg = {"hidden": False, "mouse": False, "tick": 0, "pos": (0, 0), "t": 0.0}
        now = time.time()
        if now - cg["t"] < 0.1:                       # 10 checks a second is plenty
            return
        cg["t"] = now
        want = False
        try:
            g, entry = getattr(self, "_game", None), getattr(self, "_game_entry", None)
            if g and entry and entry.get("cat") in ("pc_games", "emulation"):
                fg, _cls = _win_foreground()
                want = fg in g.get("hwnds", ()) and self._fg_fullscreen(fg)
        except Exception:  # noqa: BLE001
            want = False
        if not want:
            if cg["hidden"]:
                restore_system_cursor()
                cg["hidden"] = False
                self._dbg_log("game pointer: shown again (game not in front)")
            cg["mouse"] = False
            return
        tick, pos = _last_input_tick(), cursor_pos()
        mouse_moved = tick != cg["tick"] and (abs(pos[0] - cg["pos"][0]) > 2
                                              or abs(pos[1] - cg["pos"][1]) > 2)
        cg["tick"], cg["pos"] = tick, pos
        if mouse_moved and cg["hidden"]:
            restore_system_cursor()                   # you grabbed the real mouse
            cg["hidden"], cg["mouse"] = False, True
            self._dbg_log("game pointer: real mouse moved -> shown")
            return
        if cg["mouse"] and self._pad_in_use():
            cg["mouse"] = False                       # back on the controller
        if not cg["hidden"] and not cg["mouse"]:
            if hide_system_cursor():
                cg["hidden"] = True
                self._dbg_log("game pointer: hidden (full-screen game, using the pad)")

    def _pad_in_use(self) -> bool:
        j = self.joy
        if j is None:
            return False
        try:
            if any(j.get_button(i) for i in range(j.get_numbuttons())):
                return True
            n = j.get_numaxes()
            if any(abs(j.get_axis(i)) > 0.5 for i in range(min(n, 4))):
                return True
            if any(j.get_hat(i) != (0, 0) for i in range(j.get_numhats())):
                return True
        except pygame.error:
            return False
        return False

    def _poll_desktop_mouse(self):
        """Left stick = pointer, right stick = scroll, RT = left click, LT = right
        click, R3 = middle click, D-pad = arrow keys."""
        if not self._desktop_mouse_ready():
            if getattr(self, "_dm", None):
                self._release_desktop_mouse()
            if getattr(self, "_dm_active", False):
                self._dbg_log("desktop mouse OFF (full-screen window / JoyXoff / back in GAMES)")
            self._dm_active = False
            return
        if not getattr(self, "_dm_active", False):
            self._dbg_log("desktop mouse ON")
        self._dm_active = True
        dm = getattr(self, "_dm", None)
        if dm is None:
            dm = self._dm = {"lt": False, "rt": False, "r3": False, "mx": 0.0, "my": 0.0,
                             "sx": 0.0, "sy": 0.0, "held": {}, "push_t": 0.0}
        j = self.joy
        try:
            n  = j.get_numaxes()
            ax = lambda i, d=0.0: j.get_axis(i) if n > i else d
            lx, ly, rx, ry = ax(0), ax(1), ax(2), ax(3)
            if self.config.get("mouse_stick", "Right stick") == "Right stick":
                # pointer on the right stick, scrolling on the left — Windows menus
                # navigate with the left stick, so they stay still while you point
                lx, ly, rx, ry = rx, ry, lx, ly
            lt, rt = ax(4, -1.0), ax(5, -1.0)
            r3  = bool(j.get_numbuttons() > 9 and j.get_button(9))
            hat = j.get_hat(0) if j.get_numhats() else (0, 0)
        except pygame.error:
            return
        now = time.time()
        # left stick → pointer (curved: slow and precise near the center)
        # Settings (1 = slow … 10 = fast), like JoyXoff's three sliders
        lvl = lambda key, d: max(1, min(10, int(self.config.get(key, d) or d)))
        speed, accel, scroll = lvl("mouse_speed", 3), lvl("mouse_accel", 2), lvl("mouse_scroll", 4)
        # Pointer speed: top speed at full tilt, 200 … 2270 px/s (scaled to screen width)
        top_px_s = (200 + 230 * (speed - 1)) * (self.width / 1920)
        # Acceleration: holding the stick pushed far speeds the pointer up over ~1 s
        # (level 1 = none, level 10 = up to 3.25x)
        dz, mag = 0.12, math.hypot(lx, ly)
        if mag > 0.85:
            dm["push_t"] = dm["push_t"] or now
        else:
            dm["push_t"] = 0.0
        boost = 1 + (accel - 1) * 0.25 * min(1.0, (now - dm["push_t"]) if dm["push_t"] else 0.0)
        # Another program also moving the pointer from the controller (JoyXoff
        # profile, Steam desktop layout, DS4Windows…)? Then step aside.
        if self._dm_check_other_mover(dm, mag > dz, now):
            return
        # Pointer hidden (e.g. after boot nobody has touched the real mouse yet)?
        # Wake it up as soon as the controller wants to use it.
        using = mag > dz or rt > 0.0 or lt > 0.0
        if using and now - dm.get("wake_t", 0.0) > 0.5:
            dm["wake_t"] = now
            try:
                if cursor_hidden():
                    wake_cursor()
                    self._dbg_log("desktop mouse: Windows was hiding the pointer -> woke it up")
            except Exception:  # noqa: BLE001
                pass
        if mag > dz:
            k = ((mag - dz) / (1 - dz)) ** 1.8 * (top_px_s / 60) * boost / mag
            dm["mx"] += lx * k
            dm["my"] += ly * k
            mx, my = int(dm["mx"]), int(dm["my"])
            if mx or my:
                # exact placement: unaffected by Windows pointer speed / precision,
                # and lets us see if someone else moves the pointer too
                cx, cy = cursor_pos()
                set_cursor_pos(cx + mx, cy + my)
                dm["expect"], dm["last"] = (cx + mx, cy + my), (mx, my)
                self._dm_telemetry(dm, mx, my, (cx, cy), now)
                dm["mx"] -= mx
                dm["my"] -= my
        else:
            dm["expect"] = None
            dm.pop("tel", None)
        # right stick → scroll (vertical and horizontal)
        for key, val, horiz, sign in (("sy", ry, False, -1), ("sx", rx, True, 1)):
            if abs(val) > 0.2:
                # Scroll speed: level 4 ≈ 8 notches/s at full tilt (level 1 = 2, level 10 = 20)
                dm[key] += sign * (1 if val > 0 else -1) * ((abs(val) - 0.2) / 0.8) ** 1.5 * scroll * 4
                step = int(dm[key])
                if step:
                    mouse_wheel(step, horizontal=horiz)
                    dm[key] -= step
            else:
                dm[key] = 0.0
        # triggers → left / right mouse button (hold to drag); "rt" / "lt" here mean
        # the left-click / right-click trigger, swapped by the Mouse Clicks setting
        left_val, right_val = (lt, rt) if self._clicks_swapped() else (rt, lt)
        for name, val, right in (("rt", left_val, False), ("lt", right_val, True)):
            down = val > -0.4 if dm[name] else val > 0.0       # a little hysteresis
            if down != dm[name]:
                mouse_button(down, right=right)
                dm[name] = down
        # R3 → middle button
        if r3 != dm["r3"]:
            mouse_middle(r3)
            dm["r3"] = r3
        # D-pad → arrow keys (repeat while held)
        for vk, on in ((VK_LEFT, hat[0] < 0), (VK_RIGHT, hat[0] > 0),
                       (VK_UP, hat[1] > 0), (VK_DOWN, hat[1] < 0)):
            t0 = dm["held"].get(vk)
            if not on:
                dm["held"].pop(vk, None)
                continue
            if t0 is None:
                dm["held"][vk] = now
                dm["held"][-vk] = now
                send_arrow(vk)
            elif now - t0 > 0.40 and now - dm["held"].get(-vk, 0) > 0.07:
                dm["held"][-vk] = now
                send_arrow(vk)

    def go_to_desktop(self):
        """Minimize GAMES and stay out of the way until the player comes back
        (VIEW + START, taskbar, Alt+Tab…)."""
        self._desktop_mode = True
        self._game  = None
        self._grace = None
        self._dbg_log("Go to Desktop")
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        pygame.display.iconify()
        if sys.platform == "win32":
            try:
                if cursor_hidden():
                    wake_cursor()        # after boot Windows hides it until a mouse moves
                    self._dbg_log("Go to Desktop: pointer was hidden -> woke it up")
            except Exception:  # noqa: BLE001
                pass

    POWER_TILES = ("sleep", "restart", "shutdown")   # the big tiles along the bottom

    def _power_nav(self, btn):
        """List on top (up / down), Sleep · Restart · Shutdown tiles below (left / right)."""
        acts  = [a for a, _l, _c in self.POWER_OPTIONS]
        tiles = [i for i, a in enumerate(acts) if a in self.POWER_TILES]
        items = [i for i, a in enumerate(acts) if a not in self.POWER_TILES]
        cur   = self.exit_cursor
        if cur in tiles:
            k = tiles.index(cur)
            if btn == "left":
                cur = tiles[(k - 1) % len(tiles)]
            elif btn == "right":
                cur = tiles[(k + 1) % len(tiles)]
            elif btn == "up":
                cur = items[-1]
            elif btn == "down":
                cur = items[0]
        else:
            k = items.index(cur)
            if btn == "up":
                cur = items[k - 1] if k > 0 else tiles[0]
            elif btn == "down":
                cur = items[k + 1] if k + 1 < len(items) else tiles[0]
        self.exit_cursor = cur

    @staticmethod
    def _power_icon(surf, kind, cx, cy, col, s):
        if kind == "desktop":
            pygame.draw.rect(surf, col, (cx - s, cy - s + 2, 2 * s, int(1.3 * s)), 2, border_radius=3)
            pygame.draw.line(surf, col, (cx, cy + s // 2), (cx, cy + s), 2)
            pygame.draw.line(surf, col, (cx - s // 2, cy + s), (cx + s // 2, cy + s), 2)
        elif kind == "pair":
            r = pygame.Rect(cx - s, cy - s // 2, 2 * s, s + 2)
            pygame.draw.rect(surf, col, r, border_radius=s // 2)
            pygame.draw.circle(surf, C_PANEL, (cx - s // 2, cy), max(2, s // 4))
            pygame.draw.circle(surf, C_PANEL, (cx + s // 2, cy), max(2, s // 4))
        elif kind == "audio":
            pygame.draw.arc(surf, col, (cx - s, cy - s, 2 * s, 2 * s), 0.1, 3.04, 3)
            pygame.draw.rect(surf, col, (cx - s - 1, cy - 2, s // 2 + 2, s), border_radius=3)
            pygame.draw.rect(surf, col, (cx + s // 2 - 1, cy - 2, s // 2 + 2, s), border_radius=3)
        elif kind == "exit":
            pygame.draw.rect(surf, col, (cx - s, cy - s, int(1.2 * s), 2 * s), 2, border_radius=2)
            pygame.draw.line(surf, col, (cx - 2, cy), (cx + s, cy), 2)
            pygame.draw.polygon(surf, col, [(cx + s + 3, cy), (cx + s - 4, cy - 5), (cx + s - 4, cy + 5)])
        elif kind == "sleep":                       # crescent moon (cut out, any background)
            moon = pygame.Surface((2 * s + 2, 2 * s + 2), pygame.SRCALPHA)
            pygame.draw.circle(moon, col, (s + 1, s + 1), s)
            pygame.draw.circle(moon, (0, 0, 0, 0), (s + 1 + s // 2, s + 1 - s // 3), s)
            surf.blit(moon, (cx - s - 1, cy - s - 1))
        elif kind == "restart":
            pygame.draw.arc(surf, col, (cx - s, cy - s, 2 * s, 2 * s), 0.6, 5.6, 3)
            pygame.draw.polygon(surf, col, [(cx + s + 3, cy - s // 2 - 3), (cx + s - 6, cy - s // 2 - 2),
                                            (cx + s - 1, cy - s // 2 + 7)])
        elif kind == "shutdown":
            pygame.draw.arc(surf, col, (cx - s, cy - s, 2 * s, 2 * s), -1.0, 4.15, 3)
            pygame.draw.line(surf, col, (cx, cy - s - 2), (cx, cy), 3)

    def _draw_exit_confirm(self):
        """Power menu: a list (Desktop, pairing, Exit) and three big tiles."""
        scr = self.screen
        ov = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ov.fill((8, 10, 14, 200))
        scr.blit(ov, (0, 0))
        opts  = [(a, l, c or C_ACCENT) for a, l, c in self.POWER_OPTIONS]
        items = [(i, o) for i, o in enumerate(opts) if o[0] not in self.POWER_TILES]
        tiles = [(i, o) for i, o in enumerate(opts) if o[0] in self.POWER_TILES]
        row_h, gap = _s(46), _s(6)
        tile_h     = _s(92)
        header_h, footer_h, pad = _s(64), _s(52), _s(14)
        pw = min(self.width - _s(40), _s(520))
        ph = header_h + pad + len(items) * (row_h + gap) + _s(14) + tile_h + pad + footer_h
        px, py = (self.width - pw) // 2, (self.height - ph) // 2
        rect = (px, py, pw, ph)
        draw_panel(scr, rect, _s(18))
        draw_panel_header(scr, self.fonts, rect, header_h, "Power")
        y = py + header_h + pad
        for i, (act, label, col) in items:
            rr  = pygame.Rect(px + _s(16), y, pw - _s(32), row_h)
            sel = i == self.exit_cursor
            if sel:
                draw_row_highlight(scr, rr, col)
            self._power_icon(scr, act, rr.x + _s(30), rr.centery, col, _s(11))
            t = self.fonts["ui"].render(label, True, C_WHITE if sel else C_TEXT)
            scr.blit(t, (rr.x + _s(58), rr.centery - t.get_height() // 2))
            y += row_h + gap
        pygame.draw.line(scr, PANEL_DIV, (px + _s(20), y + _s(4)), (px + pw - _s(20), y + _s(4)))
        y += _s(14)
        tw = (pw - _s(32) - _s(20)) // max(1, len(tiles))
        for k, (i, (act, label, col)) in enumerate(tiles):
            r   = pygame.Rect(px + _s(16) + k * (tw + _s(10)), y, tw, tile_h)
            sel = i == self.exit_cursor
            if sel:
                draw_row_highlight(scr, r, col)
            else:
                pygame.draw.rect(scr, PANEL_TOP, r, border_radius=_s(10))
                pygame.draw.rect(scr, PANEL_BORDER, r, 1, border_radius=_s(10))
            self._power_icon(scr, act, r.centerx, r.y + _s(32), col, _s(14))
            t = self.fonts["hint"].render(label, True, C_WHITE if sel else C_TEXT)
            scr.blit(t, t.get_rect(center=(r.centerx, r.bottom - _s(20))))
        draw_panel_footer(scr, self.fonts["hint"], rect, footer_h,
                          [("A", "Select"), ("B", "Cancel")])

    def _draw_cat_menu(self):
        entry   = self.cat_menu["entry"]
        opts    = self._cat_menu_options()
        colours = [C_ACCENT2] * len(CATEGORIES) + [C_YELLOW]
        options = [(label, colours[i]) for i, (label, _) in enumerate(opts)]
        current = CATEGORIES.index(entry["cat"])
        self._draw_menu_panel("Move to", entry["name"], options,
                              self.cat_menu["cursor"], current=current)

    # ── On-screen keyboard (VIEW + X while a launcher / game start is in front) ─
    def _osk_allowed(self):
        """Launcher screens, while a game is starting, non-full-screen windows, and
        anywhere on the desktop after "Go to Desktop" — never in a full-screen game."""
        if self._desktop_mouse_ready():
            return True                     # wherever mouse mode works, the keyboard does too
        try:
            fg, cls = _win_foreground()
        except Exception:  # noqa: BLE001
            return False
        if not fg or fg == self._hwnd or cls in _IDLE_WINDOW_CLASSES:
            return False
        if _win_process_exe(fg) in LAUNCHER_EXES:
            return True
        g = self._game
        if g and not g["hwnds"]:
            return True
        # A window that doesn't cover the screen: settings / "Play" dialogs that
        # some games show before starting (Tomb Raider, Guardians of the Galaxy…).
        # Full-screen gameplay never matches, so the combo can't disturb a game.
        try:
            import ctypes
            from ctypes import wintypes
            r = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(fg, ctypes.byref(r))
            return (r.right - r.left) < self.width * 0.9 or (r.bottom - r.top) < self.height * 0.9
        except Exception:  # noqa: BLE001
            return False

    def _poll_osk_toggle(self):
        """In the background: VIEW + X opens the keyboard."""
        if not self.joy or sys.platform != "win32":
            return
        try:
            view = self.joy.get_numbuttons() > 6 and self.joy.get_button(6)
            x    = self.joy.get_button(2)
        except pygame.error:
            return
        pressed, self._osk_prev_x = (x and not self._osk_prev_x), x
        if view and pressed and not self._joyxoff and self._osk_allowed():
            self.osk_open()

    def _osk_size(self):
        ow   = min(self.width - _s(40), _s(900))
        unit = (ow - _s(32)) / OSK_UNITS
        kh   = int(min(unit * 0.86, _s(40), self.height * 0.052))   # smaller on small screens
        gap  = _s(5)
        hints_h = _s(66)            # two lines of button hints
        oh   = _s(14) + len(OSK_ROWS) * (kh + gap) + hints_h + _s(8)
        return ow, oh, unit, kh, gap

    def _osk_layout(self):
        """[[(rect, key), …], …] in window coordinates."""
        ow, oh, unit, kh, gap = self._osk_size()
        rows, y = [], _s(14)
        for row in OSK_ROWS:
            row_w = sum(k["w"] for k in row) * unit
            x = (ow - row_w) / 2
            out = []
            for k in row:
                w = k["w"] * unit
                out.append((pygame.Rect(int(x + gap / 2), y, int(w - gap), kh), k))
                x += w
            rows.append(out)
            y += kh + gap
        return rows

    def osk_open(self):
        self._release_desktop_mouse()      # let go of any click held with the desktop mouse
        self._dm_active = False
        import ctypes
        u32 = ctypes.windll.user32
        fg, _cls = _win_foreground()
        ow, oh, *_ = self._osk_size()
        top  = self.config.get("osk_pos", "Bottom") == "Top"
        x, y = self._osk_pos(ow, oh, top=top)
        pygame.event.set_grab(False)
        u32.ShowWindow(self._hwnd, 4)                         # SW_SHOWNOACTIVATE
        self.screen = pygame.display.set_mode((ow, oh), pygame.NOFRAME)
        self._hwnd  = pygame.display.get_wm_info().get("window", self._hwnd)
        ex = u32.GetWindowLongW(self._hwnd, -20)
        u32.SetWindowLongW(self._hwnd, -20, ex | 0x08000000 | 0x8)   # NOACTIVATE | TOPMOST
        win_set_pos(self._hwnd, HWND_TOPMOST, x, y, ow, oh, 0x0010 | 0x0040 | 0x0020)
        if fg:
            _win_bring_to_front(fg)                           # typing goes to the launcher
        set_input_mode("pad")
        self._dbg_log(f"keyboard opened over '{_win_process_exe(fg) if fg else 'desktop'}' "
                      f"at {x},{y} size {ow}x{oh} (topmost)")
        self.osk = {"target": fg, "sel": [2, 0], "shift": False, "held": {},
                    "mx": 0.0, "my": 0.0, "rt": False, "lt": False, "top": top, "t": time.time(),
                    "known": set(self._game["hwnds"]) if self._game else set()}

    def _osk_pos(self, ow, oh, top):
        return (self.width - ow) // 2, (_s(24) if top else self.height - oh - _s(24))

    def _osk_flip_position(self):
        """L3: move the keyboard between the bottom and the top of the screen."""
        import ctypes
        self.osk["top"] = not self.osk.get("top")
        ow, oh = self.screen.get_size()
        x, y = self._osk_pos(ow, oh, self.osk["top"])
        win_set_pos(self._hwnd, HWND_TOPMOST, x, y, ow, oh, 0x0010)

    def osk_close(self):
        import ctypes
        u32 = ctypes.windll.user32
        target = self.osk.get("target") if self.osk else None
        for key, right in (("rt", False), ("lt", True)):        # let go of a held click
            if self.osk and self.osk.get(key):
                try:
                    mouse_button(False, right=right)
                except Exception:  # noqa: BLE001
                    pass
        self.osk = None
        self._dbg_log("keyboard closed")
        ex = u32.GetWindowLongW(self._hwnd, -20)
        u32.SetWindowLongW(self._hwnd, -20, ex & ~0x08000000 & ~0x8)
        win_set_pos(self._hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
        self._hwnd  = pygame.display.get_wm_info().get("window", self._hwnd)
        win_set_pos(self._hwnd, 0, 0, 0, self.width, self.height, 0x0004 | 0x0010 | 0x0020)
        pygame.display.iconify()                              # back out of the way
        fg, _cls = _win_foreground()
        if target and u32.IsWindow(target) and fg in (0, self._hwnd):
            _win_bring_to_front(target)

    def _osk_type(self, key):
        sh = self.osk["shift"]
        k  = key["kind"]
        if k == "char":
            send_text(key["s"] if sh else key["n"])
        elif k == "text":
            send_text(key["text"])
        elif k == "space":
            send_text(" ")
        elif k == "bksp":
            send_vk(VK_BACK)
        elif k == "tab":
            send_vk(VK_TAB)
        elif k == "enter":
            send_vk(VK_RETURN)
        elif k == "shift":
            self.osk["shift"] = not sh

    def _osk_button(self, b):
        o = self.osk
        if b == 0:                                 # A — type the selected key
            r, c = o["sel"]
            self._osk_type(OSK_ROWS[r][c])
        elif b == 1:
            send_vk(VK_BACK)                       # B — backspace
        elif b == 2:
            send_text(" ")                         # X — space
        elif b == 3:
            o["shift"] = not o["shift"]            # Y — shift
        elif b == 4:
            send_vk(VK_TAB, shift=True)            # LB — previous field
        elif b == 5:
            send_vk(VK_TAB)                        # RB — next field
        elif b == 7:
            send_vk(VK_RETURN)                     # START — Enter
        elif b == 8:
            self._osk_flip_position()              # L3 — move keyboard top / bottom
        elif b == 9:
            mouse_button(True)                     # R3 — click
            mouse_button(False)
        elif b == 6:
            self.osk_close()                       # VIEW — close keyboard

    def _osk_move(self, dx, dy):
        r, c = self.osk["sel"]
        if dx:
            c = (c + dx) % len(OSK_ROWS[r])
        if dy:
            rows = self._osk_layout()
            cx   = rows[r][c][0].centerx
            r    = (r + dy) % len(OSK_ROWS)
            c    = min(range(len(rows[r])), key=lambda i: abs(rows[r][i][0].centerx - cx))
        self.osk["sel"] = [r, c]

    def _osk_poll(self):
        """D-pad / left stick navigation (with repeat), right stick = mouse, RT = click."""
        o, joy, now = self.osk, self.joy, time.time()
        if not joy:
            return
        try:
            hat  = joy.get_hat(0) if joy.get_numhats() else (0, 0)
            ax   = joy.get_axis(0) if joy.get_numaxes() > 1 else 0
            ay   = joy.get_axis(1) if joy.get_numaxes() > 1 else 0
            rx   = joy.get_axis(2) if joy.get_numaxes() > 3 else 0
            ry   = joy.get_axis(3) if joy.get_numaxes() > 3 else 0
            rt   = joy.get_axis(5) if joy.get_numaxes() > 5 else -1
            lt   = joy.get_axis(4) if joy.get_numaxes() > 4 else -1
        except pygame.error:
            return
        dirs = {"left":  hat[0] < 0 or ax < -self.dead, "right": hat[0] > 0 or ax > self.dead,
                "up":    hat[1] > 0 or ay < -self.dead, "down":  hat[1] < 0 or ay > self.dead}
        for d, on in dirs.items():
            if not on:
                o["held"].pop(d, None)
                continue
            t0 = o["held"].get(d)
            if t0 is None or (now - t0 > self.rep_del and now - o["held"].get(d + "_t", 0) > self.rep_rate):
                if t0 is None:
                    o["held"][d] = now
                o["held"][d + "_t"] = now
                self._osk_move(*{"left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1)}[d])
        # right stick → mouse pointer (curved for precision)
        dz  = 0.15
        mag = math.hypot(rx, ry)
        if mag > dz:
            k = self._pointer_px_per_frame(mag, dz) / mag      # same speed as desktop mouse
            o["mx"] += rx * k
            o["my"] += ry * k
            mx, my = int(o["mx"]), int(o["my"])
            if mx or my:
                mouse_move(mx, my)
                o["mx"] -= mx
                o["my"] -= my
        # triggers → left / right mouse button (hold to drag), per Mouse Clicks
        left_val, right_val = (lt, rt) if self._clicks_swapped() else (rt, lt)
        for key, val, right in (("rt", left_val, False), ("lt", right_val, True)):
            down = val > 0.5
            if down != o.get(key, False):
                mouse_button(down, right=right)
                o[key] = down

    def _osk_frame(self):
        """One frame of the keyboard overlay (runs while another window has focus)."""
        g = self._game
        try:
            import ctypes
            gone = self.osk["target"] and not ctypes.windll.user32.IsWindow(self.osk["target"])
        except Exception:  # noqa: BLE001
            gone = False
        started = bool(g and (g["hwnds"] - self.osk["known"] - {self.osk["target"]}))
        if started or gone:
            self.osk_close()                       # the game started / dialog closed
            return
        self._osk_poll()
        if self.osk:
            now = time.time()
            if now - self.osk.get("top_t", 0) > 1.0:          # stay above the browser etc.
                self.osk["top_t"] = now
                try:
                    win_set_pos(self._hwnd, HWND_TOPMOST, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)
                except Exception:  # noqa: BLE001
                    pass
            self._osk_draw()
            pygame.display.flip()

    def _osk_draw(self):
        surf = self.screen
        ow, oh = surf.get_size()
        surf.fill(PANEL_BOT)
        draw_panel(surf, (0, 0, ow, oh), 0)        # square: the window itself is a rectangle
        pygame.draw.rect(surf, C_ACCENT, (0, 0, ow, oh), width=2)
        font = self.fonts["hint"]
        sh   = self.osk["shift"]
        for r, row in enumerate(self._osk_layout()):
            for c, (rect, k) in enumerate(row):
                sel = [r, c] == self.osk["sel"]
                on  = k["kind"] == "shift" and sh
                pygame.draw.rect(surf, BTN_KEYCAP_BG, rect, border_radius=_s(7))
                if sel or on:
                    draw_rounded_rect(surf, C_ACCENT, rect, radius=_s(7), alpha=90 if sel else 45)
                pygame.draw.rect(surf, C_ACCENT if sel else BTN_KEYCAP_BORDER, rect,
                                 width=2 if sel else 1, border_radius=_s(7))
                label = (k["s"] if sh else k["n"]) if k["kind"] == "char" else k["label"]
                t = (self.fonts["ui"] if k["kind"] == "char" else font).render(
                    label, True, C_WHITE if sel else C_TEXT)
                surf.blit(t, t.get_rect(center=rect.center))
        lines = [[("A", "Type"), ("B", "Delete"), ("X", "Space"), ("Y", "Shift"),
                  ("LB", ""), ("RB", "Prev / next field"), ("START", "Enter")],
                 [("RS", "Mouse"), (self._click_triggers()[0], "Click"),
                  ("LS", "Move keyboard"), ("VIEW", "Close")]]
        for i, hints in enumerate(lines):
            hw = hints_width(font, hints)
            draw_hints(surf, font, hints, (ow - hw) // 2, oh - _s(52) + i * _s(30))

    ESCAPE_HOLD = 1.0   # seconds to hold VIEW + START to come back

    def _poll_escape(self):
        """Hold VIEW + START (Back + Start) for a second anywhere → back to the app.
        Works over launcher pop-ups, error dialogs, etc. — controller only."""
        if not self.joy or sys.platform != "win32" or not self._hwnd:
            return
        try:
            held = self.joy.get_numbuttons() > 7 and self.joy.get_button(6) and self.joy.get_button(7)
        except pygame.error:
            return
        now = time.time()
        if not held:
            self._escape_t = None
            return
        if getattr(self, "_escape_t", None) is None:
            self._escape_t = now
        elif now - self._escape_t >= self.ESCAPE_HOLD:
            self._escape_t = None
            try:
                fg, _cls = _win_foreground()
                if fg and fg != self._hwnd and _win_process_exe(fg) in LAUNCHER_EXES:
                    import ctypes
                    ctypes.windll.user32.ShowWindow(fg, 6)    # minimize a launcher pop-up
                game = self._running_emulation()
                _win_restore_and_focus(self._hwnd)
                if game:
                    # Emulated game: GameClub comes to the front with a small menu. The
                    # emulator loses focus, so it stops reading the controller meanwhile.
                    self.game_menu = {"entry": game[0], "pids": game[1], "stage": "menu",
                                      "cursor": 0, "t": now}
                    self._dbg_log(f"game menu opened over '{game[0]['name']}' (pids {sorted(game[1])})")
            except Exception:  # noqa: BLE001
                pass
            self._launch_block_until = now + 0.8              # don't act on the held buttons

    # ── Pairing a Bluetooth controller (no keyboard needed) ───────────────────
    PAIR_AFTER = 4.0     # seconds after start with no controller before the screen shows

    def open_pairing(self, mode, kind="controller"):
        if self.pairing is not None:
            self.pairing.stop()
        self.pair_mode = mode
        self.pair_kind = kind
        self.pairing   = BluetoothPairing(self._dbg_log, kind) if sys.platform == "win32" else None
        self._pair_joys = pygame.joystick.get_count()
        self._dbg_log(f"pairing screen opened ({mode})")

    def close_pairing(self):
        if self.pairing is not None:
            self.pairing.stop()
        self.pairing, self.pair_mode = None, None

    def _poll_pairing(self):
        if self.joy is not None:
            self._had_joy = True
        # Started with Windows and no controller (and nobody typing): offer pairing
        if (self.pair_mode is None and not self._pair_tried and not self._had_joy
                and not self._kbd_used and sys.platform == "win32"
                and time.time() - self._started_t > self.PAIR_AFTER):
            self._pair_tried = True
            self.open_pairing("startup")
        if self.pair_mode is None:
            return
        st = self.pairing.state if self.pairing else "unavailable"
        if self.pair_mode == "startup" and self.joy is not None:
            name = self.joy.get_name()
            self.close_pairing()
            self.set_status(f"{name} connected")
            self._block_launch(1.0)
            return
        if st == "paired":
            # manual: a new pad shows up next to the current one — or give it a moment
            if getattr(self, "pair_kind", "controller") == "audio":
                if time.time() - self.pairing.paired_at > 2.5:
                    dev, msg = self.pairing.device, self.pairing.message
                    self.close_pairing()
                    self.set_status(f"{dev} paired \u2014 {msg[:1].lower() + msg[1:]}"
                                    if msg else f"{dev} paired")
                    self._block_launch(1.0)
                return
            more = pygame.joystick.get_count() > getattr(self, "_pair_joys", 0)
            if self.pair_mode == "manual" and (more or time.time() - self.pairing.paired_at > 4):
                dev = self.pairing.device
                self.close_pairing()
                self._init_joy()
                self.set_status(f"{dev} paired")
                self._block_launch(1.0)

    def _draw_pairing(self):
        p    = self.pairing
        st   = p.state if p else "unavailable"
        scr  = self.screen
        W, H = self.width, self.height
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((8, 10, 14, 205))
        scr.blit(ov, (0, 0))
        found = st in ("pairing", "paired")
        audio = getattr(self, "pair_kind", "controller") == "audio"
        thing = "Headphones" if audio else "Controller"
        title = {"pairing": f"{thing} found", "paired": f"{thing} paired",
                 "failed": "Couldn\u2019t pair", "no_bt": "No Bluetooth",
                 "bt_off": "Bluetooth is off"}.get(
                     st, "No controller connected" if self.pair_mode == "startup"
                   else ("Pair headphones" if audio else "Pair a controller"))
        sub = {"pairing": "Pairing\u2026", "paired": "Connecting\u2026",
               "starting": "Getting Bluetooth ready\u2026", "bt_off": "Switching it on\u2026"}.get(
                   st, "GameClub is looking for one" if self.pair_mode == "startup" else "Searching\u2026")
        pw, ph = min(W - _s(40), _s(760)), min(H - _s(40), _s(480))
        P = pygame.Rect((W - pw) // 2, (H - ph) // 2, pw, ph)
        draw_panel(scr, P, _s(16))
        draw_panel_header(scr, self.fonts, P, _s(64), title, sub)
        # pulsing rings + controller
        cx, cy = P.centerx, P.y + _s(150)
        t = time.time()
        for k in range(3):
            ph_ = (t * 0.6 + k / 3) % 1.0
            rr  = int(_s(30) + _s(55) * ph_)
            ring = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*C_ACCENT, int(170 * (1 - ph_))), (rr + 2, rr + 2), rr, 2)
            if st in ("searching", "pairing", "starting", "bt_off"):
                scr.blit(ring, (cx - rr - 2, cy - rr - 2))
        col = C_GREEN if st == "paired" else (C_ACCENT2 if found else (150, 160, 178))
        if audio:
            self._power_icon(scr, "audio", cx, cy, (170, 120, 220) if not found else col, _s(26))
            bw = bh = 0
        else:
            bw, bh = _s(70), _s(44)
        if bw:
            self._draw_pad_icon(scr, cx, cy, col, bw, bh)
        y = P.y + _s(240)
        self._draw_pairing_text(P, pw, st, p, found, audio, y)

    @staticmethod
    def _draw_pad_icon(scr, cx, cy, col, bw, bh):
        body = pygame.Rect(0, 0, bw, bh)
        body.center = (cx, cy)
        pygame.draw.rect(scr, col, body, border_radius=bh // 2)
        pygame.draw.circle(scr, col, (body.x + bh // 3, body.bottom - bh // 6), bh // 3)
        pygame.draw.circle(scr, col, (body.right - bh // 3, body.bottom - bh // 6), bh // 3)
        pygame.draw.circle(scr, C_BG, (body.x + bw // 3, cy - 2), max(3, bh // 7))
        pygame.draw.circle(scr, C_BG, (body.right - bw // 3, cy + 2), max(3, bh // 7))

    def _draw_pairing_text(self, P, pw, st, p, found, audio, y):
        scr = self.screen
        if found:
            n = self.fonts["title"].render(fit_text(self.fonts["title"], p.device, pw - _s(80)),
                                           True, C_WHITE)
            scr.blit(n, n.get_rect(center=(P.centerx, y + _s(20))))
            if audio:
                hint = (p.message or "Keep them close to the PC") if st == "pairing" else \
                       (p.message or "Connecting\u2026")
            else:
                hint = ("Keep the controller close to the PC" if st == "pairing"
                        else "Press any button on it if it doesn\u2019t connect in a few seconds")
            ht = self.fonts["hint"].render(hint, True, C_TEXT_DIM)
            scr.blit(ht, ht.get_rect(center=(P.centerx, y + _s(70))))
        else:
            if st == "unavailable":
                lines = [("Automatic pairing isn\u2019t available in this build.", C_YELLOW),
                         ("Pair the controller in Windows: Settings \u2192 Bluetooth & devices.", C_TEXT_DIM),
                         ("(Needs the winrt-Windows.Devices.Enumeration package.)", C_TEXT_DIM)]
            elif st == "no_bt":
                lines = [("This PC has no Bluetooth.", C_YELLOW),
                         ("Use the controller\u2019s USB receiver or a cable instead.", C_TEXT_DIM)]
            elif audio:
                lines = [("Put your headphones in pairing mode:", C_WHITE),
                         ("Usually: hold the power or Bluetooth button until the light flashes", C_TEXT_DIM),
                         ("AirPods / earbuds: open the case and hold its button", C_TEXT_DIM),
                         ("Sound switches to them automatically once they\u2019re paired", C_ACCENT2)]
                if st == "failed" and p.message:
                    lines.append((p.message, C_RED))
            else:
                lines = [("Put your controller in pairing mode:", C_WHITE),
                         ("Xbox: hold the small pair button on top until the logo flashes fast", C_TEXT_DIM),
                         ("PlayStation: hold PS + Create (Share) until the light bar blinks", C_TEXT_DIM),
                         ("Switch Pro / 8BitDo / GameSir: hold the sync or pairing button", C_TEXT_DIM)]
                if st == "failed" and p.message:
                    lines.append((p.message, C_RED))
                elif p and p.message:
                    lines.append((p.message, C_YELLOW))
            for txt, c in lines:
                f  = self.fonts["ui"] if c == C_WHITE else self.fonts["hint"]
                tt = f.render(fit_text(f, txt, pw - _s(80)), True, c)
                scr.blit(tt, (P.x + _s(40), y))
                y += tt.get_height() + _s(10)
        if self.pair_mode == "manual":
            draw_panel_footer(scr, self.fonts["hint"], P, _s(52), [("B", "Cancel")])
        else:
            ft2 = self.fonts["hint"].render(
                "Using a keyboard instead? Press any key to skip pairing", True, C_TEXT_DIM)
            r2 = ft2.get_rect(midbottom=(P.centerx, P.bottom - _s(20)))
            ft = self.fonts["hint"].render(
                "Pairs by itself \u2014 no keyboard needed  \u00b7  Already paired? Just switch it on",
                True, C_ACCENT2)
            scr.blit(ft, ft.get_rect(midbottom=(P.centerx, r2.top - _s(8))))
            scr.blit(ft2, r2)

    # ── In-game menu for emulated games (hold VIEW + START) ───────────────────
    CLOSE_WAIT = 5.0       # seconds to wait for the emulator to close by itself

    def _running_emulation(self):
        """(entry, pids) if a game from the Emulation tab is running, else None."""
        g, entry = getattr(self, "_game", None), getattr(self, "_game_entry", None)
        if not g or not entry or entry.get("cat") != "emulation" or sys.platform != "win32":
            return None
        import ctypes
        u32   = ctypes.windll.user32
        never = OVERLAY_EXES | LAUNCHER_EXES | {"explorer.exe", "joyxoff.exe"}
        wins  = [(h, _win_process_exe(h)) for h in g["hwnds"] if u32.IsWindow(h)]
        wins  = [(h, exe) for h, exe in wins if exe and exe not in never]
        # Prefer the emulator the shortcut points at — never close an unrelated
        # program that just happened to open a window while the game was running
        tgt  = os.path.basename((entry.get("target") or "").replace("\\", "/")).lower()
        mine = [w for w in wins if w[1] == tgt] if tgt.endswith(".exe") else []
        pids = {_win_pid(h) for h, _e in (mine or wins[:1])}
        pids = {p for p in pids if p and p != os.getpid() and _pid_alive(p)}
        return (entry, pids) if pids else None

    def _game_menu_options(self):
        st = self.game_menu["stage"]
        if st == "menu":
            return [("Resume game", C_ACCENT, "resume"),
                    ("Close game", (222, 72, 72), "close"),
                    ("Back to GameClub", (150, 160, 178), "stay")]
        if st == "closing":
            return [("Cancel", (150, 160, 178), "stay")]
        return [("Force close", (222, 72, 72), "force"),          # stage "stuck"
                ("Show the emulator", C_ACCENT, "resume"),
                ("Wait a bit longer", (220, 170, 40), "wait"),
                ("Back to GameClub", (150, 160, 178), "stay")]

    def _game_menu_action(self, btn):
        m, opts = self.game_menu, self._game_menu_options()
        if btn in ("up", "down"):
            m["cursor"] = (m["cursor"] + (-1 if btn == "up" else 1)) % len(opts)
            return
        if btn == "B":
            act = "resume" if m["stage"] == "menu" else "stay"
        elif btn == "A":
            act = opts[m["cursor"]][2]
        else:
            return
        name = m["entry"]["name"]
        if act == "resume":
            self.game_menu = None
            self._resume_game()
        elif act == "stay":
            self.game_menu = None
            self._block_launch()
        elif act in ("close", "wait"):
            if act == "close":
                n = _close_pid_windows(m["pids"])
                self._dbg_log(f"game menu: asked '{name}' to close ({n} windows)")
            m.update(stage="closing", cursor=0, t=time.time())
        elif act == "force":
            for pid in m["pids"]:
                _kill_pid(pid)
            self._dbg_log(f"game menu: force-closed '{name}'")
            m.update(stage="closing", cursor=0, t=time.time() - self.CLOSE_WAIT + 1.5)

    def _resume_game(self):
        g = getattr(self, "_game", None)
        if not g:
            return
        import ctypes
        u32 = ctypes.windll.user32
        for h in g["hwnds"]:
            if u32.IsWindow(h) and u32.IsWindowVisible(h):
                pygame.display.iconify()
                _win_bring_to_front(h)
                return

    def _poll_game_menu(self):
        """While closing: done when the emulator's process is gone; after
        CLOSE_WAIT seconds offer Force close (it may be asking to confirm)."""
        m = self.game_menu
        if not m or sys.platform != "win32":
            return
        alive = {p for p in m["pids"] if _pid_alive(p)}
        if not alive:
            name = m["entry"]["name"]
            self.game_menu = None
            self._game, self._grace = None, None
            self._end_play()
            self._block_launch(0.8)
            if m["stage"] != "menu":
                self.set_status(f"Closed {name}")
            return
        if m["stage"] == "closing" and time.time() - m["t"] > self.CLOSE_WAIT:
            m.update(stage="stuck", cursor=0)
            self._dbg_log(f"game menu: '{m['entry']['name']}' still running after {self.CLOSE_WAIT:.0f} s")

    def _draw_game_menu(self):
        m  = self.game_menu
        st = m["stage"]
        title = {"menu": "Game", "closing": "Closing\u2026", "stuck": "Still running"}[st]
        sub = m["entry"]["name"]
        if st == "stuck":
            sub = "It may be asking you to confirm"
        elif st == "closing":
            sub = m["entry"]["name"] + " " + "." * (1 + int(time.time() * 3) % 3)
        self._draw_menu_panel(title, sub, [(l, c) for l, c, _a in self._game_menu_options()],
                              m["cursor"])

    FOCUS_COOLDOWN = 1.0   # seconds of ignored input after the app comes back to the front
    INPUT_LOG = os.path.join(os.path.expanduser("~"), "games_browser_input_log.txt")

    def _dbg_log(self, msg):
        """Tiny in-memory log of focus / input events (written to disk only if a
        launch happens right after coming back — to diagnose stray launches)."""
        if not hasattr(self, "_dbg"):
            self._dbg = deque(maxlen=250)
        self._dbg.append(f"{time.time():.3f}  {msg}")

    def _flush_log(self, force=False):
        """Append new log lines to the file every few seconds (file kept < ~400 KB)."""
        now = time.time()
        if not force and now - getattr(self, "_log_flush_t", 0) < 5:
            return
        self._log_flush_t = now
        lines = getattr(self, "_dbg", None)
        if not lines:
            return
        try:
            if os.path.exists(self.INPUT_LOG) and os.path.getsize(self.INPUT_LOG) > 400_000:
                os.replace(self.INPUT_LOG, self.INPUT_LOG + ".old")
            with open(self.INPUT_LOG, "a", encoding="utf-8") as fh:
                fh.write("\n".join(lines) + "\n")
            lines.clear()
        except OSError:
            pass

    def _arm_focus_guard(self, why):
        """The app just came to the front: drop the presses that did the switching
        and lock A / Enter until they've been released (see _update_a_gate)."""
        try:
            pygame.event.clear((pygame.KEYDOWN, pygame.KEYUP, pygame.TEXTINPUT,
                                pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP,
                                pygame.JOYHATMOTION, pygame.JOYAXISMOTION))
        except pygame.error:
            pass
        self.held.clear()
        now = time.time()
        # Everything else works again almost immediately; only A / Enter (the
        # buttons that launch) stay locked until released + FOCUS_COOLDOWN.
        self._input_block_until  = max(getattr(self, "_input_block_until", 0), now + 0.25)
        self._launch_block_until = max(self._launch_block_until, now + self.FOCUS_COOLDOWN)
        self._a_gate       = True        # A / Enter locked until seen released
        self._a_gate_clear = None
        self._a_gate_min   = now + self.FOCUS_COOLDOWN
        self._last_front_t = now
        self._dbg_log(f"FOCUS GUARD armed ({why})")

    def _update_a_gate(self):
        """Unlock A / Enter once controller A and Enter/Space have been released
        for a moment AND the cooldown is over — a press that was part of the
        window switch can then never count as a new press."""
        if not getattr(self, "_a_gate", False):
            return
        now = time.time()
        try:
            a_down = bool(self.joy and self.joy.get_numbuttons() > 0 and self.joy.get_button(0))
        except pygame.error:
            a_down = False
        keys   = pygame.key.get_pressed()
        k_down = keys[pygame.K_RETURN] or keys[pygame.K_SPACE] or keys[pygame.K_KP_ENTER]
        if a_down or k_down:
            self._a_gate_clear = None
            return
        if self._a_gate_clear is None:
            self._a_gate_clear = now
        if now - self._a_gate_clear >= 0.15 and now >= getattr(self, "_a_gate_min", 0):
            self._a_gate = False
            self._dbg_log("A / Enter unlocked")

    def _on_front_change(self, front):
        """When the app comes back to the front (task switcher, Alt+Tab, VIEW+START,
        after a game…), arm the focus guard."""
        was = getattr(self, "_was_front", True)
        self._was_front = front
        if front != was:
            self._dbg_log(f"in front: {front}")
        if front and not was and not self.osk:
            self._arm_focus_guard("foreground check")
            if self._desktop_mode:
                self._desktop_mode = False
                self._dbg_log("back from desktop")
            if getattr(self, "_dm_active", False) or getattr(self, "_dm", None):
                self._release_desktop_mouse()
                self._dm_active = False
                self._dbg_log("desktop mouse OFF (back in GAMES)")
        if front:
            self._update_a_gate()

    def _in_front(self):
        """True while our window is the one the player is looking at."""
        if sys.platform == "win32" and getattr(self, "_hwnd", None):
            try:
                import ctypes
                u = ctypes.windll.user32
                return u.GetForegroundWindow() == self._hwnd and not u.IsIconic(self._hwnd)
            except Exception:  # noqa: BLE001
                pass
        return bool(pygame.display.get_active())

    def run(self):
        while True:
            # While a game is in front: tick slowly, ignore the controller and skip
            # drawing, so the launcher doesn't steal CPU/GPU or react to game input.
            # Wait for the next frame FIRST, then check who's in front. (Checking
            # before the wait missed presses that switched windows during it —
            # e.g. A in the task switcher — and they then launched a game.)
            self.clock.tick(60 if (getattr(self, "_active", True)
                                   or getattr(self, "_dm_active", False)) else 8)
            front  = self._in_front()
            self._on_front_change(front)
            active = front or self._launch_card_visible() or bool(self.osk)
            self._active = active
            if active:
                pygame.mouse.set_visible(False)

            for ev in self._get_events():
                if ev.type == pygame.QUIT:
                    self._save_config()
                    pygame.quit()
                    sys.exit()

                elif ev.type == pygame.TEXTINPUT:
                    if self.prompt is not None:
                        self.prompt.handle_text_input(ev.text)
                    elif self.tab == self.TAB_SETTINGS:
                        self.settings.handle_text_input(ev.text)

                elif ev.type == pygame.KEYDOWN:
                    self._dbg_log(f"KEYDOWN {pygame.key.name(ev.key)}")
                    self._kbd_used = True
                    if self.pair_mode == "startup":   # a keyboard user — no pairing screen
                        self.close_pairing()
                        continue
                    if not front and not (self.tab == self.TAB_SETTINGS and self.settings.editing):
                        self._dbg_log("KEYDOWN ignored (not in front at frame start)")
                        continue      # e.g. Enter from a switcher that just picked GAMES
                    if self.prompt is not None:          # typing a new category name
                        self._note_input("key", time.time())
                        self.prompt.handle_key(ev)
                        if self.prompt.done:
                            self._finish_prompt()
                        continue
                    if ev.key == pygame.K_F1 and not (self.tab == self.TAB_SETTINGS
                                                      and self.settings.editing):
                        self._note_input("key", time.time())
                        self.show_keys = not self.show_keys
                        continue
                    if self.tab == self.TAB_SETTINGS and self.settings.editing:
                        self.settings.handle_key(ev)
                        continue  # swallow — never pass to key_map while editing
                    if self.tab == self.TAB_SETTINGS:
                        self.settings.handle_key(ev)
                        if self.settings.editing:
                            continue  # editing just started (e.g. A pressed) — swallow
                    if ev.key == pygame.K_TAB and (ev.mod & pygame.KMOD_SHIFT):
                        self._action("LB")
                        continue
                    key_map = {
                        pygame.K_UP:        "up",
                        pygame.K_DOWN:      "down",
                        pygame.K_LEFT:      "left",
                        pygame.K_RIGHT:     "right",
                        pygame.K_RETURN:    "A",
                        pygame.K_SPACE:     "A",
                        pygame.K_BACKSPACE: "B",
                        pygame.K_ESCAPE:    "start",
                        pygame.K_TAB:       "RB",
                        pygame.K_x:         "X",
                        pygame.K_y:         "Y",
                        pygame.K_DELETE:    "manage",
                        pygame.K_F2:        "back",
                        pygame.K_PAGEUP:    "LT",
                        pygame.K_PAGEDOWN:  "RT",
                        pygame.K_s:         "RS",
                    }
                    if ev.key in key_map:
                        self._action(key_map[ev.key])

                elif ev.type == pygame.JOYBUTTONDOWN:
                    self._dbg_log(f"JOYBUTTONDOWN {ev.button}")
                    if self.osk:
                        self._osk_button(ev.button)
                        continue
                    # Use the in-front state from the START of this frame, not "now":
                    # JoyXoff switches to GAMES the instant A is pressed, so by the
                    # time this event is handled we're already in front — but the
                    # press belonged to the switcher, not to us.
                    if not front or not self._in_front():
                        self._dbg_log(f"JOYBUTTONDOWN {ev.button} ignored (not in front at frame start)")
                        continue
                    btn_map = {0: "A", 1: "B", 2: "X", 3: "Y", 4: "LB", 5: "RB", 6: "back", 7: "start",
                               9: "RS"}
                    if ev.button in btn_map:
                        self._action(btn_map[ev.button], "joy")

                elif ev.type == pygame.JOYDEVICEADDED:
                    self._init_joy()

                elif ev.type == pygame.JOYDEVICEREMOVED:
                    self.held.clear()
                    if time.time() < getattr(self, "_joy_reset_until", 0):
                        self._init_joy()          # our own reset — not a real unplug
                        continue
                    # Real unplug? Check again in a moment (Bluetooth blips, driver
                    # re-enumeration and pads switching modes come straight back).
                    self._joy_lost_t = time.time()
                    self._init_joy()

                elif ev.type == pygame.ACTIVEEVENT:
                    if self.osk:
                        continue
                    if getattr(ev, "gain", 0) and getattr(ev, "state", 0) in (1, 2, 6):
                        self._arm_focus_guard("activate event")
                        self._reinit_joy()
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)

                elif ev.type == pygame.WINDOWFOCUSGAINED:
                    if self.osk:
                        continue
                    self._arm_focus_guard("window focus event")
                    self._reinit_joy()
                    pygame.event.set_grab(True)
                    pygame.mouse.set_visible(False)

            self._check_joy_lost()
            self._check_joyxoff()
            self._flush_log()
            self._watch_foreground()
            self._check_launch()
            self._check_pending_uninstall()
            self._poll_game_menu()
            self._poll_pairing()
            self._poll_game_cursor()
            if self.osk:
                self._osk_frame()
                continue          # the keyboard overlay is all we draw
            if not (active and self._in_front()):
                self.held.clear()
                if not active:
                    self._poll_escape()
                    self._poll_osk_toggle()
                    self._poll_desktop_mouse()
                    continue      # nothing to draw while the game is in front
            else:
                self._poll_joy()
            # On the Settings tab, preview the Button Style being chosen (not saved yet)
            saved_style  = _button_style
            saved_accent = _accent_name
            if self.tab == self.TAB_SETTINGS:
                set_button_style(self.settings.config.get("button_style", saved_style))
                set_accent(self.settings.config.get("accent", saved_accent))
            self._draw_bg()

            if self.tab == self.TAB_SETTINGS:
                self.settings.draw(self.screen)
            else:
                self._draw_grid()

            # Draw bars AFTER content so they cleanly mask any grid overflow
            self._draw_topbar()
            self._draw_tabbar()
            self._draw_bottombar()
            # Settings text field being typed with the controller: keyboard on top
            if self.tab == self.TAB_SETTINGS and self.settings.editing and self.settings.kbd:
                self.settings._kbd_draw(self.screen)
            if self.tab == self.TAB_SETTINGS and self.settings.picker is not None:
                self.settings.picker.draw(self.screen)
            if self.tab == self.TAB_SETTINGS and self.settings_leave is not None:
                self._draw_settings_leave()

            if self.cat_menu is not None:
                self._draw_cat_menu()

            if self.opts_menu is not None:
                self._draw_opts_menu()

            if self.group_menu is not None:
                self._draw_group_menu()

            if self.prompt is not None:
                self.prompt._kbd_draw(self.screen)

            if self.manage is not None:
                self._draw_manage()

            if self.cover_picker is not None:
                # Check if an in-progress cover download has finished.
                done = self.cover_picker.poll_apply()
                if isinstance(done, tuple) and done[0] == "pick":
                    self._apply_picked_cover(done[1])
                if self.cover_picker is not None:
                    self.cover_picker.draw(self.screen)

            if self.confirm_exit:
                self._draw_exit_confirm()

            if self.game_menu is not None:
                self._draw_game_menu()

            if self.pair_mode is not None:
                self._draw_pairing()

            if self.show_keys:
                self._draw_keys_panel()

            self._draw_launching()

            self._draw_toast()
            set_button_style(saved_style)
            set_accent(saved_accent)
            pygame.display.flip()


# ── Controller on UAC prompts & the sign-in screen (like JoyXoff) ─────────────
# UAC prompts and the sign-in screen live on Windows' locked "Winlogon" desktop,
# where only LocalSystem programs may move the pointer or press keys. So, when the
# option is on, GameClub registers a scheduled task that runs GameClub.exe as SYSTEM
# from boot ("--secure-service"). That copy starts a tiny helper in the signed-in
# session, ON the Winlogon desktop ("--secure-helper"), which reads the controller
# through XInput and works as a mouse — but only while that desktop is showing.
SECURE_TASK = "GameClub Secure Desktop"
SECURE_DIR  = os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"), "GameClub")
SECURE_LOG  = os.path.join(SECURE_DIR, "secure_desktop_log.txt")

_SECURE_TASK_XML = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>GameClub: controller on UAC prompts and the sign-in screen</Description></RegistrationInfo>
  <Triggers><BootTrigger><Enabled>true</Enabled></BootTrigger></Triggers>
  <Principals>
    <Principal id="Author"><UserId>S-1-5-18</UserId><RunLevel>HighestAvailable</RunLevel></Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>4</Priority>
    <RestartOnFailure><Interval>PT1M</Interval><Count>5</Count></RestartOnFailure>
    <IdleSettings><StopOnIdleEnd>false</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings>
  </Settings>
  <Actions Context="Author">
    <Exec><Command>"{exe}"</Command><Arguments>--secure-service --config "{cfg}"</Arguments></Exec>
  </Actions>
</Task>
"""


def _slog(msg):
    try:
        os.makedirs(SECURE_DIR, exist_ok=True)
        if os.path.exists(SECURE_LOG) and os.path.getsize(SECURE_LOG) > 200_000:
            os.replace(SECURE_LOG, SECURE_LOG + ".old")
        with open(SECURE_LOG, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")
    except OSError:
        pass


def set_secure_task(enable: bool, exe: str = "", cfg: str = "") -> bool:
    """Create + start (or stop + remove) the SYSTEM task. Needs administrator."""
    from xml.sax.saxutils import escape
    run = lambda *a: subprocess.run(["schtasks", *a], capture_output=True,
                                    creationflags=CREATE_NO_WINDOW)
    try:
        if not enable:
            run("/End", "/TN", SECURE_TASK)
            return run("/Delete", "/TN", SECURE_TASK, "/F").returncode == 0
        xml  = _SECURE_TASK_XML.format(exe=escape(exe), cfg=escape(cfg))
        path = os.path.join(tempfile.gettempdir(), "padhub_secure_task.xml")
        with open(path, "w", encoding="utf-16") as fh:
            fh.write(xml)
        ok = run("/Create", "/TN", SECURE_TASK, "/XML", path, "/F").returncode == 0
        try:
            os.remove(path)
        except OSError:
            pass
        if ok:
            run("/Run", "/TN", SECURE_TASK)          # start now, not only after a reboot
        return ok
    except Exception:  # noqa: BLE001
        return False


def _input_desktop_name() -> str:
    """Name of the desktop that gets input now: "Default", or "Winlogon" while a
    UAC prompt / the sign-in or lock screen is showing."""
    import ctypes
    from ctypes import wintypes
    u32 = ctypes.windll.user32
    u32.OpenInputDesktop.restype = wintypes.HANDLE
    h = u32.OpenInputDesktop(0, False, 0x0001)          # DESKTOP_READOBJECTS
    if not h:
        return ""
    try:
        buf, need = ctypes.create_unicode_buffer(256), wintypes.DWORD()
        if u32.GetUserObjectInformationW(wintypes.HANDLE(h), 2, buf, ctypes.sizeof(buf),
                                         ctypes.byref(need)):
            return buf.value
        return ""
    finally:
        u32.CloseDesktop(wintypes.HANDLE(h))


def _xinput_pad():
    """(buttons, lt, rt, lx, ly, rx, ry) of the first connected XInput pad, or None.
    Sticks −1…1 (y up = negative, like SDL), triggers 0…1."""
    import ctypes

    class GP(ctypes.Structure):
        _fields_ = [("wButtons", ctypes.c_ushort), ("bLeftTrigger", ctypes.c_ubyte),
                    ("bRightTrigger", ctypes.c_ubyte), ("sThumbLX", ctypes.c_short),
                    ("sThumbLY", ctypes.c_short), ("sThumbRX", ctypes.c_short),
                    ("sThumbRY", ctypes.c_short)]

    class ST(ctypes.Structure):
        _fields_ = [("dwPacketNumber", ctypes.c_uint32), ("Gamepad", GP)]
    dll = None
    for name in ("xinput1_4", "xinput1_3", "xinput9_1_0"):
        try:
            dll = getattr(ctypes.windll, name)
            break
        except OSError:
            continue
    if dll is None:
        return None
    for i in range(4):
        st = ST()
        if dll.XInputGetState(i, ctypes.byref(st)) == 0:
            g = st.Gamepad
            n = lambda v: max(-1.0, min(1.0, v / 32767.0))
            return (g.wButtons, g.bLeftTrigger / 255.0, g.bRightTrigger / 255.0,
                    n(g.sThumbLX), -n(g.sThumbLY), n(g.sThumbRX), -n(g.sThumbRY))
    return None


def run_secure_helper(cfg_path, parent_pid):
    """Runs as SYSTEM on the Winlogon desktop. Mouse mode while it's showing:
    pointer + scroll sticks and click triggers (as set in GameClub), D-pad = arrow
    keys, A = Space (press the focused button), B = Esc (No / cancel)."""
    import ctypes
    from ctypes import wintypes
    u32 = ctypes.windll.user32
    _slog(f"helper started (pid {os.getpid()})")
    cfg, cfg_t, check_t = {}, 0.0, 0.0
    was_on, joyx = False, False
    held = {"lt": False, "rt": False}
    keys = {}
    acc = [0.0, 0.0, 0.0, 0.0]
    while True:
        now = time.time()
        if now - check_t > 1.0:
            check_t = now
            if parent_pid and not _pid_alive(parent_pid):
                _slog("helper: service gone -> exit")
                return
            try:
                joyx = joyxoff_running()             # JoyXoff does this itself
            except Exception:  # noqa: BLE001
                joyx = False
        if now - cfg_t > 5.0:
            cfg_t = now
            try:
                with open(cfg_path, encoding="utf-8") as fh:
                    cfg = json.load(fh)
            except (OSError, ValueError):
                pass
        on = not joyx and _input_desktop_name().lower() == "winlogon"
        if on != was_on:
            _slog("secure desktop " + ("showing -> controller on" if on else "gone -> idle"))
            if on:
                try:                                  # make sure we act on that desktop
                    u32.OpenInputDesktop.restype = wintypes.HANDLE
                    hd = u32.OpenInputDesktop(0, False, 0x10000000)   # GENERIC_ALL
                    if hd:
                        u32.SetThreadDesktop(wintypes.HANDLE(hd))
                except Exception:  # noqa: BLE001
                    pass
            else:
                for name, right in (("rt", False), ("lt", True)):
                    if held[name]:
                        mouse_button(False, right=right)
                        held[name] = False
            was_on = on
        if not on:
            time.sleep(0.15)
            continue
        pad = _xinput_pad()
        if pad is None:
            time.sleep(0.05)
            continue
        btn, lt, rt, lx, ly, rx, ry = pad
        if cfg.get("mouse_stick", "Right stick") == "Right stick":
            lx, ly, rx, ry = rx, ry, lx, ly
        lvl = lambda k, d: max(1, min(10, int(cfg.get(k, d) or d)))
        speed, scroll = lvl("mouse_speed", 3), lvl("mouse_scroll", 4)
        width = u32.GetSystemMetrics(0) or 1920
        top_px_s = (200 + 230 * (speed - 1)) * (width / 1920)
        dz, mag = 0.12, math.hypot(lx, ly)
        if mag > dz:
            k = ((mag - dz) / (1 - dz)) ** 1.8 * (top_px_s / 60) / mag
            acc[0] += lx * k
            acc[1] += ly * k
            mx, my = int(acc[0]), int(acc[1])
            if mx or my:
                pt = wintypes.POINT()
                u32.GetCursorPos(ctypes.byref(pt))
                u32.SetCursorPos(pt.x + mx, pt.y + my)
                acc[0] -= mx
                acc[1] -= my
        for i, val, horiz, sign in ((3, ry, False, -1), (2, rx, True, 1)):
            if abs(val) > 0.2:
                acc[i] += sign * (1 if val > 0 else -1) * ((abs(val) - 0.2) / 0.8) ** 1.5 * scroll * 4
                step = int(acc[i])
                if step:
                    mouse_wheel(step, horizontal=horiz)
                    acc[i] -= step
            else:
                acc[i] = 0.0
        swapped = cfg.get("mouse_clicks", "").startswith("LT left")
        left_v, right_v = (lt, rt) if swapped else (rt, lt)
        for name, val, right in (("rt", left_v, False), ("lt", right_v, True)):
            down = val > 0.3 if held[name] else val > 0.5
            if down != held[name]:
                mouse_button(down, right=right)
                held[name] = down
        # D-pad = arrows (repeat while held), A = Space, B = Esc
        for bit, vk, rep in ((0x0004, VK_LEFT, True), (0x0008, VK_RIGHT, True),
                             (0x0001, VK_UP, True), (0x0002, VK_DOWN, True),
                             (0x1000, 0x20, False), (0x2000, 0x1B, False)):
            pressed, t0 = bool(btn & bit), keys.get(vk)
            if not pressed:
                keys.pop(vk, None)
                continue
            if t0 is None:
                keys[vk] = now
                keys[-vk] = now
                send_arrow(vk) if vk in (VK_LEFT, VK_RIGHT, VK_UP, VK_DOWN) else send_vk(vk)
            elif rep and now - t0 > 0.4 and now - keys.get(-vk, 0) > 0.07:
                keys[-vk] = now
                send_arrow(vk)
        time.sleep(1 / 60)


def run_secure_service(cfg_path):
    """Runs as SYSTEM (scheduled task, from boot). Keeps one helper running in the
    signed-in console session on its Winlogon desktop; follows session changes."""
    import ctypes
    from ctypes import wintypes
    k32, a32 = ctypes.windll.kernel32, ctypes.windll.advapi32

    class SI(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("lpReserved", wintypes.LPWSTR),
                    ("lpDesktop", wintypes.LPWSTR), ("lpTitle", wintypes.LPWSTR),
                    ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
                    ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD),
                    ("dwXCountChars", wintypes.DWORD), ("dwYCountChars", wintypes.DWORD),
                    ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                    ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD),
                    ("lpReserved2", ctypes.c_void_p), ("hStdInput", wintypes.HANDLE),
                    ("hStdOutput", wintypes.HANDLE), ("hStdError", wintypes.HANDLE)]

    class PI(ctypes.Structure):
        _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE),
                    ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)]

    def launch(session):
        tok, dup = wintypes.HANDLE(), wintypes.HANDLE()
        if not a32.OpenProcessToken(wintypes.HANDLE(k32.GetCurrentProcess()), 0x01FF,
                                    ctypes.byref(tok)):     # TOKEN_ALL_ACCESS (basic)
            _slog(f"OpenProcessToken failed ({k32.GetLastError()})")
            return None
        try:
            if not a32.DuplicateTokenEx(tok, 0x02000000, None, 2, 1, ctypes.byref(dup)):
                _slog(f"DuplicateTokenEx failed ({k32.GetLastError()})")
                return None
            sid = wintypes.DWORD(session)
            if not a32.SetTokenInformation(dup, 12, ctypes.byref(sid), 4):   # TokenSessionId
                _slog(f"SetTokenInformation failed ({k32.GetLastError()})")
                return None
            exe = sys.executable
            cmd = ctypes.create_unicode_buffer(
                f'"{exe}" --secure-helper --config "{cfg_path}" --parent {os.getpid()}')
            si, pi = SI(), PI()
            si.cb = ctypes.sizeof(SI)
            si.lpDesktop = "winsta0\\winlogon"
            if not a32.CreateProcessAsUserW(dup, None, cmd, None, None, False,
                                            CREATE_NO_WINDOW, None, os.path.dirname(exe),
                                            ctypes.byref(si), ctypes.byref(pi)):
                _slog(f"CreateProcessAsUser failed ({k32.GetLastError()})")
                return None
            k32.CloseHandle(pi.hThread)
            _slog(f"helper launched in session {session} (pid {pi.dwProcessId})")
            return pi
        finally:
            k32.CloseHandle(tok)
            if dup:
                k32.CloseHandle(dup)

    _slog(f"service started (pid {os.getpid()}), config: {cfg_path}")
    helper, helper_session, cfg_t = None, None, 0.0
    while True:
        now = time.time()
        if now - cfg_t > 10.0:                         # option switched off? stop
            cfg_t = now
            try:
                with open(cfg_path, encoding="utf-8") as fh:
                    if not json.load(fh).get("secure_desktop", False):
                        _slog("option is off -> service exit")
                        if helper:
                            k32.TerminateProcess(helper.hProcess, 0)
                        return
            except (OSError, ValueError):
                pass
        k32.WTSGetActiveConsoleSessionId.restype = ctypes.c_uint32
        session = k32.WTSGetActiveConsoleSessionId()
        alive = helper is not None and k32.WaitForSingleObject(helper.hProcess, 0) == 0x102
        if session != 0xFFFFFFFF and (not alive or session != helper_session):
            if alive:
                k32.TerminateProcess(helper.hProcess, 0)
            if helper is not None:
                k32.CloseHandle(helper.hProcess)
            helper, helper_session = launch(session), session
            if helper is None:
                time.sleep(5)
        time.sleep(1.0)


def _arg(name, default=""):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv[:-1] else default


if __name__ == "__main__" and "--secure-service" in sys.argv:
    run_secure_service(_arg("--config", CONFIG_FILE))
    sys.exit()
if __name__ == "__main__" and "--secure-helper" in sys.argv:
    try:
        run_secure_helper(_arg("--config", CONFIG_FILE), int(_arg("--parent", "0") or 0))
    except Exception as exc:  # noqa: BLE001
        _slog(f"helper crashed: {exc!r}")
    sys.exit()

if __name__ == "__main__":
    print(f"{APP_NAME} build: {APP_BUILD}")
    print(f"Running file: {os.path.abspath(__file__)}")
    print(f"Input log:    {App.INPUT_LOG}")
    import atexit
    restore_system_cursor()              # in case a crash left the game pointer hidden
    atexit.register(restore_system_cursor)
    app = App()
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        app.path = sys.argv[1]
        app._scan()
    app.run()