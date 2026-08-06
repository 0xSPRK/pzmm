import os

from .mod_parser import parse_mod_info


def scan_mods(game_mods_path):
    """Scan the game mods folder once and return a list of mod entries.

    One entry per (top-level folder, mod id) group; each entry carries the
    concrete directories that contain mod.info (mod_dirs), the list of
    version suffixes and the media paths for conflict analysis.
    """
    mods_dict = {}
    for root, dirs, files in os.walk(game_mods_path):
        if "mod.info" not in files:
            continue
        info = os.path.join(root, "mod.info")
        data = parse_mod_info(info)
        mod_id = data.get("id")
        if not mod_id:
            continue

        rel_path = os.path.relpath(root, game_mods_path)
        root_folder_name = rel_path.split(os.sep)[0]
        root_fp = os.path.join(game_mods_path, root_folder_name)
        version = "Base" if root == root_fp else os.path.basename(root)

        key = (root_fp, mod_id)
        entry = mods_dict.get(key)
        if entry is None:
            entry = {
                "id": mod_id,
                "name": data.get("name") or "Unknown Mod",
                "require": data.get("require", []),
                "root_fp": root_fp,
                "versions": [],
                "mod_dirs": [],
                "media_paths": [],
            }
            mods_dict[key] = entry
        entry["versions"].append(version)
        entry["mod_dirs"].append(root)

        media = os.path.join(root, "media")
        if os.path.isdir(media):
            entry["media_paths"].append(media)

    return list(mods_dict.values())
