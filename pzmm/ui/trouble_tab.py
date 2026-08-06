import os
import shutil
import html

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QMessageBox,
)

from ..core.localization import tr
from ..core.settings import load_settings
from ..core.analytics import AnalysisWorker


class TroubleTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._setup_ui()

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.wait(5000)
            self._worker = None
        event.accept()

    def _setup_ui(self):
        lay = QVBoxLayout(self)

        actions_lay = QHBoxLayout()

        self.btn_analyze = QPushButton(tr("trb_analyze"))
        self.btn_analyze.setObjectName("ActionBtn")
        self.btn_analyze.clicked.connect(self.analyze_logs)

        self.btn_deep_scan = QPushButton(tr("trb_deep_scan"))
        self.btn_deep_scan.setObjectName("PrimaryBtn")
        self.btn_deep_scan.clicked.connect(self.run_deep_analysis)

        self.btn_clear_lua = QPushButton(tr("trb_clear_lua"))
        self.btn_clear_lua.setObjectName("WarnBtn")
        self.btn_clear_lua.clicked.connect(self.clear_lua_cache)

        self.btn_clear_logs = QPushButton(tr("trb_clear_logs"))
        self.btn_clear_logs.setObjectName("DangerBtn")
        self.btn_clear_logs.clicked.connect(self.clear_game_logs)

        actions_lay.addWidget(self.btn_analyze)
        actions_lay.addWidget(self.btn_deep_scan)
        actions_lay.addWidget(self.btn_clear_lua)
        actions_lay.addWidget(self.btn_clear_logs)
        actions_lay.addStretch()

        self.trouble_console = QTextEdit()
        self.trouble_console.setObjectName("Console")
        self.trouble_console.setReadOnly(True)

        self.log_lbl = QLabel(tr("trb_log_title"))
        lay.addLayout(actions_lay)
        lay.addWidget(self.log_lbl)
        lay.addWidget(self.trouble_console)

    def analyze_logs(self):
        self.trouble_console.clear()
        zomboid_dir = os.path.expanduser(r"~\Zomboid")
        console_path = os.path.join(zomboid_dir, "console.txt")

        if not os.path.exists(console_path):
            self.trouble_console.append(
                f"<span style='color: yellow;'>{html.escape(tr('trb_no_log'))}</span>"
            )
            return

        errors_found = []
        try:
            with open(console_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()[-10000:]

            for line in lines:
                if "ERROR:" in line or "Exception" in line or "STACK TRACE" in line or "failed to load" in line:
                    errors_found.append(line.strip())

            if not errors_found:
                self.trouble_console.append(
                    f"<span style='color: #a6e3a1;'>{html.escape(tr('trb_no_errors'))}</span>"
                )
            else:
                self.trouble_console.append(
                    f"<span style='color: #f38ba8; font-weight: bold;'>{html.escape(tr('trb_found_errors', count=len(errors_found)))}</span>"
                )
                unique_errors = list(dict.fromkeys(errors_found))[:50]
                for err in unique_errors:
                    self.trouble_console.append(
                        f"<span style='color: #eba0ac;'>- {html.escape(err)}</span>"
                    )

        except Exception as e:
            self.trouble_console.append(
                f"<span style='color: red;'>{html.escape(tr('trb_err_read', e=e))}</span>"
            )

    def run_deep_analysis(self):
        if self._worker and self._worker.isRunning():
            return
        self.trouble_console.clear()
        self.trouble_console.append(
            f"<span style='color: yellow;'>{html.escape(tr('rep_wait'))}</span>"
        )

        game_path = load_settings().get("game_mods_path")
        if not game_path or not os.path.exists(game_path):
            self.trouble_console.append(
                f"<span style='color: red;'>{html.escape(tr('trb_no_mods_path'))}</span>"
            )
            return

        self._worker = AnalysisWorker(game_path)
        self._worker.report_ready.connect(self._on_report_ready)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_error(self, msg):
        self.trouble_console.append(
            f"<span style='color: red;'>{html.escape(str(msg))}</span>"
        )
        self._worker = None

    def _on_report_ready(self, html_report):
        self.trouble_console.clear()
        self.trouble_console.setHtml(html_report)
        self._worker = None

    def clear_lua_cache(self):
        lua_dir = os.path.expanduser(r"~\Zomboid\Lua")
        if os.path.exists(lua_dir):
            try:
                shutil.rmtree(lua_dir, ignore_errors=True)
                QMessageBox.information(self, tr("msg_done"), tr("trb_lua_ok"))
            except Exception as e:
                QMessageBox.critical(self, tr("msg_err"), str(e))
        else:
            QMessageBox.information(self, tr("msg_done"), tr("trb_lua_empty"))

    def clear_game_logs(self):
        logs_dir = os.path.expanduser(r"~\Zomboid\Logs")
        console_txt = os.path.expanduser(r"~\Zomboid\console.txt")

        cleared = False
        if os.path.exists(logs_dir):
            shutil.rmtree(logs_dir, ignore_errors=True)
            cleared = True
        if os.path.exists(console_txt):
            try:
                os.remove(console_txt)
                cleared = True
            except Exception:
                pass

        if cleared:
            QMessageBox.information(self, tr("msg_done"), tr("trb_logs_ok"))
        else:
            QMessageBox.information(self, tr("msg_done"), tr("trb_logs_empty"))

    def retranslate(self):
        self.btn_analyze.setText(tr("trb_analyze"))
        self.btn_deep_scan.setText(tr("trb_deep_scan"))
        self.btn_clear_lua.setText(tr("trb_clear_lua"))
        self.btn_clear_logs.setText(tr("trb_clear_logs"))
        self.log_lbl.setText(tr("trb_log_title"))
