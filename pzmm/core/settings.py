import sys
import os
import re
import json

PZ_APP_ID = "108600"


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    d = os.path.dirname
    return d(d(d(os.path.abspath(__file__))))


def get_data_dir():
    if os.name == "nt":
        base = os.environ.get("APPDATA")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    if base:
        return os.path.join(base, "pzmm")
    return get_base_dir()


def get_legacy_settings_file():
    return os.path.join(get_base_dir(), "settings.json")


SETTINGS_FILE = os.path.join(get_data_dir(), "settings.json")
MANIFEST_DIR = os.path.join(get_data_dir(), "manifest")


def _defaults():
    return {
        "steamcmd_path": "",
        "download_root": "",
        "workshop_path": "",
        "game_mods_path": os.path.expanduser(r"~\Zomboid\mods"),
        "auto_install": True,
        "language": "ru",
        "steam_login": "anonymous",
        "steam_password": "",
    }


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _migrate_legacy():
    legacy = get_legacy_settings_file()
    if not os.path.exists(legacy) or os.path.exists(SETTINGS_FILE):
        return
    data = _read_json(legacy)
    if data is None:
        return
    s = _defaults()
    s.update(data)
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        save_settings(s)
        os.replace(legacy, os.path.join(get_data_dir(), "settings.legacy.json"))
    except OSError:
        pass


def load_settings():
    _migrate_legacy()
    s = _defaults()
    data = _read_json(SETTINGS_FILE)
    if data:
        s.update(data)
    return s


def save_settings(s):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    tmp = SETTINGS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=4, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, SETTINGS_FILE)


def resolve_download_root(s):
    root = (s.get("download_root") or "").strip()
    if root and os.path.isdir(root):
        return root
    st = (s.get("steamcmd_path") or "").strip()
    if st and os.path.exists(st):
        return os.path.dirname(st)
    return root


def resolve_workshop_path(s):
    root = resolve_download_root(s)
    derived = ""
    if root:
        derived = os.path.join(root, "steamapps", "workshop", "content", PZ_APP_ID)
    ws = (s.get("workshop_path") or "").strip()
    if ws:
        if derived and os.path.isdir(derived):
            return derived
        return ws
    if derived and os.path.isdir(derived):
        return derived
    detected = detect_workshop_path()
    return detected or derived


# ---------- Auto-detection ----------

def _find_steam_dir():
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                path, _ = winreg.QueryValueEx(k, "SteamPath")
            if path and os.path.isdir(path):
                return path
        except OSError:
            pass
    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
        os.path.expandvars(r"%ProgramFiles%\Steam"),
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        r"D:\Steam",
        r"D:\Games\Steam",
    ]
    for c in candidates:
        if c and os.path.isdir(c):
            return c
    return None


def _library_folders(steam_dir):
    folders = []
    vdf = os.path.join(steam_dir, "steamapps", "libraryfolders.vdf")
    if os.path.exists(vdf):
        try:
            with open(vdf, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            for m in re.finditer(r'^\s*"path"\s+"([^"]+)"', text, re.MULTILINE):
                p = m.group(1).replace("\\\\", os.sep).replace("\\", os.sep)
                p = os.path.normpath(p)
                if os.path.isdir(p):
                    folders.append(p)
        except OSError:
            pass
    if os.path.isdir(os.path.join(steam_dir, "steamapps")):
        folders.insert(0, steam_dir)
    seen = set()
    unique = []
    for f in folders:
        key = os.path.normcase(os.path.normpath(f))
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def detect_steamcmd_path():
    if os.name != "nt":
        return ""
    exe = "steamcmd.exe"
    candidates = []
    steam = _find_steam_dir()
    if steam:
        candidates.append(os.path.join(steam, exe))
    candidates += [
        os.path.join(os.path.expandvars(r"%ProgramFiles(x86)%\Steam"), exe),
        os.path.join(os.path.expandvars(r"%ProgramFiles%\Steam"), exe),
        os.path.join(os.path.expanduser("~"), exe),
        r"C:\steamcmd\steamcmd.exe",
        r"D:\steamcmd\steamcmd.exe",
        r"D:\Games\steamcmd\steamcmd.exe",
    ]
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if d:
            candidates.append(os.path.join(d, exe))
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return ""


def detect_workshop_path():
    steam = _find_steam_dir()
    for lib in _library_folders(steam) if steam else []:
        p = os.path.join(lib, "steamapps", "workshop", "content", PZ_APP_ID)
        if os.path.isdir(p):
            return p
    return ""


def detect_game_mods_path():
    user_mods = os.path.expanduser(r"~\Zomboid\mods")
    if os.path.isdir(user_mods):
        return user_mods
    steam = _find_steam_dir()
    for lib in _library_folders(steam) if steam else []:
        game = os.path.join(lib, "steamapps", "common", "ProjectZomboid")
        if os.path.isdir(game):
            return os.path.join(game, "mods")
    return user_mods
