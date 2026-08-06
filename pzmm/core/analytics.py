import os
import html

from PyQt6.QtCore import QThread, pyqtSignal

from .registry import scan_mods
from .localization import tr


class AnalysisWorker(QThread):
    report_ready = pyqtSignal(str)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, game_mods_path):
        super().__init__()
        self.game_mods_path = game_mods_path

    def run(self):
        game_path = self.game_mods_path
        if not game_path or not os.path.exists(game_path):
            self.error.emit(tr("trb_no_mods_path"))
            return

        self.progress.emit(5)
        mods = scan_mods(game_path)

        self.progress.emit(30)
        mods_installed = {}
        dependencies_map = {}
        file_conflicts_map = {}

        for v in mods:
            mod_id = v["id"]
            if v["versions"] == ["Base"]:
                mod_name = v["name"]
            else:
                mod_name = f"{v['name']} [{', '.join(v['versions'])}]"

            mods_installed[mod_id] = mod_name

            for req in v.get("require", []):
                if req not in dependencies_map:
                    dependencies_map[req] = []
                if mod_name not in dependencies_map[req]:
                    dependencies_map[req].append(mod_name)

            for m_path in v.get("media_paths", []):
                for m_root, m_dirs, m_files in os.walk(m_path):
                    for file in m_files:
                        if file.endswith(('.lua', '.txt', '.xml')):
                            f_rel_path = os.path.relpath(os.path.join(m_root, file), m_path)
                            if "client" in f_rel_path or "server" in f_rel_path or "scripts" in f_rel_path:
                                if f_rel_path not in file_conflicts_map:
                                    file_conflicts_map[f_rel_path] = []
                                file_conflicts_map[f_rel_path].append(mod_name)

        self.progress.emit(70)
        log_path = os.path.expanduser(r"~\Zomboid\console.txt")
        errors = 0
        warns = 0
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if "ERROR:" in line or "Exception" in line:
                        errors += 1
                    elif "WARN:" in line:
                        warns += 1

        self.progress.emit(90)
        report = []
        report.append(f"<h2 style='color: #89b4fa; text-align: center;'>{tr('rep_title')}</h2>")
        report.append(f"<h3 style='color: #cba6f7;'>{tr('rep_stat')}</h3>")
        report.append(f"<ul><li>{tr('rep_mods_inst')} <b>{len(mods_installed)}</b></li></ul><br>")

        report.append(f"<h3 style='color: #cba6f7;'>{tr('rep_deps')}</h3>")
        missing_count = 0
        for req_id, needed_by in dependencies_map.items():
            if req_id not in mods_installed:
                missing_count += 1
                report.append(
                    f"<span style='color: #f38ba8;'><b>{tr('rep_miss')}: {html.escape(req_id)}</b></span>"
                )
                report.append(
                    f"<span style='color: gray;'>   {tr('rep_req_by')} {html.escape(', '.join(needed_by))}</span><br>"
                )
        if missing_count == 0:
            report.append(f"<span style='color: #a6e3a1;'>{tr('rep_deps_ok')}</span><br><br>")
        else:
            report.append("<br>")

        report.append(f"<h3 style='color: #cba6f7;'>{tr('rep_conf')}</h3>")
        conflicts_count = 0
        report.append(f"<span style='color: gray;'>{tr('rep_conf_desc')}</span><br>")
        for file_path, mods in file_conflicts_map.items():
            unique_mods = list(set(mods))
            if len(unique_mods) > 1:
                conflicts_count += 1
                report.append(
                    f"<span style='color: #f9e2af;'>{tr('rep_file')} <b>{html.escape(file_path)}</b></span>"
                )
                report.append(
                    f"<span style='color: #eba0ac;'>   {tr('rep_mods')} {html.escape(', '.join(unique_mods))}</span><br>"
                )

        if conflicts_count == 0:
            report.append(f"<span style='color: #a6e3a1;'>{tr('rep_conf_ok')}</span><br><br>")
        else:
            report.append("<br>")

        report.append(f"<h3 style='color: #cba6f7;'>{tr('rep_logs')}</h3>")
        if errors > 0 or warns > 0:
            report.append(f"<span style='color: #f38ba8;'>{tr('rep_errs')} <b>{errors}</b></span><br>")
            report.append(f"<span style='color: #f9e2af;'>{tr('rep_warns')} <b>{warns}</b></span><br>")
        else:
            report.append(f"<span style='color: #a6e3a1;'>{tr('rep_log_ok')}</span>")

        self.progress.emit(100)
        self.report_ready.emit("".join(report))
