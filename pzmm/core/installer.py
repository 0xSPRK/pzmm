import json
import os
import shutil


def _read_manifest(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"files": []}


def _write_manifest_atomic(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _safe_rel(rel):
    rel = rel.replace("\\", "/")
    if os.path.isabs(rel):
        return None
    if ".." in rel.split("/"):
        return None
    return rel


def _needs_copy(src, dst):
    if not os.path.isfile(dst):
        return True
    try:
        if os.path.getsize(src) != os.path.getsize(dst):
            return True
        if os.path.getmtime(src) != os.path.getmtime(dst):
            return True
    except OSError:
        return True
    return False


def _prune_empty_dirs(root, keep=False):
    if not os.path.isdir(root):
        return
    for entry in os.listdir(root):
        p = os.path.join(root, entry)
        if os.path.isdir(p):
            _prune_empty_dirs(p, keep=False)
    if not keep:
        try:
            os.rmdir(root)
        except OSError:
            pass


def install_item(ws_item_dir, game_mods_dir, manifest_dir, ws_id, log_cb=None):
    """Sync-install a workshop item into the game mods folder.

    Copies files from <ws_item_dir>/mods into game_mods_dir and removes files
    that were installed earlier by this manager but are gone from the source
    (keeps the game mods folder clean after mod updates).
    Returns dict(copied=, removed=, errors=[(rel, err)]).
    """
    mods_src = os.path.join(ws_item_dir, "mods")
    if not os.path.isdir(mods_src):
        raise FileNotFoundError("No 'mods' folder in workshop item: %s" % ws_item_dir)

    manifest_path = os.path.join(manifest_dir, "%s.json" % ws_id)
    previous = set(_read_manifest(manifest_path).get("files", []))

    current = set()
    copied = 0
    removed = 0
    errors = []

    os.makedirs(game_mods_dir, exist_ok=True)

    for sub in os.listdir(mods_src):
        src = os.path.join(mods_src, sub)
        if not os.path.isdir(src):
            continue
        dst = os.path.join(game_mods_dir, sub)
        for root, _dirs, files in os.walk(src):
            for name in files:
                sfile = os.path.join(root, name)
                rel = _safe_rel(os.path.relpath(sfile, mods_src))
                if rel is None:
                    continue
                current.add(rel)
                dfile = os.path.join(dst, os.path.relpath(sfile, src))
                try:
                    if _needs_copy(sfile, dfile):
                        os.makedirs(os.path.dirname(dfile), exist_ok=True)
                        shutil.copy2(sfile, dfile)
                        copied += 1
                except Exception as e:
                    errors.append((rel, str(e)))

    for rel in sorted(previous - current):
        dfile = os.path.join(game_mods_dir, *rel.split("/"))
        try:
            if os.path.isfile(dfile):
                os.remove(dfile)
                removed += 1
        except Exception as e:
            errors.append((rel, str(e)))

    _prune_empty_dirs(game_mods_dir, keep=True)

    _write_manifest_atomic(manifest_path, {"files": sorted(current)})

    if log_cb:
        for rel, err in errors:
            log_cb("%s: %s" % (rel, err))
    return {"copied": copied, "removed": removed, "errors": errors}
