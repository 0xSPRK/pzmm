import os


def parse_mod_info(filepath):
    data = {"id": "", "name": "Unknown Mod", "require": []}
    try:
        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                parts = line.split("=", 1)
                key = parts[0].strip().lower()
                val = parts[1].strip()
                if key == "id":
                    data["id"] = val
                elif key == "name":
                    data["name"] = val
                elif key == "require":
                    if val:
                        data["require"] = [x.strip() for x in val.split(',')]
    except Exception:
        pass
    return data
