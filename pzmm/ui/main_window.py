import os
import webbrowser
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QMessageBox, QFrame,
)
from PyQt6.QtWebEngineCore import QWebEngineProfile

from ..core.settings import load_settings, get_data_dir, resolve_download_root
from ..core.localization import tr, load_language
from ..ui.theme import DARK_STYLESHEET
from ..ui.console_dialog import ConsoleDialog
from ..ui.settings_dialog import SettingsDialog
from ..ui.workshop_tab import WorkshopTab
from ..ui.mods_tab import ModsTab
from ..ui.trouble_tab import TroubleTab
from ..core.downloader import DownloadWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("PZMM"))
        self.resize(1200, 750)
        self.setStyleSheet(DARK_STYLESHEET)

        self.console = ConsoleDialog(self)
        self._worker = None

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentStoragePath(
            os.path.join(get_data_dir(), "browser_data")
        )
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )

        cen = QWidget()
        self.setCentralWidget(cen)
        lay = QVBoxLayout(cen)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(12)

        header = QFrame()
        header.setObjectName("AppHeader")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(16, 12, 16, 12)
        h_lay.setSpacing(12)

        icon = QLabel("PZ")
        icon.setObjectName("AppIcon")

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        self.title_lbl = QLabel(tr("app_title"))
        self.title_lbl.setObjectName("AppTitle")
        sub_lbl = QLabel("Версия 1.4")
        sub_lbl.setObjectName("AppSubtitle")
        title_box.addWidget(self.title_lbl)
        title_box.addWidget(sub_lbl)

        self.gh_btn = QPushButton("GitHub")
        self.gh_btn.setObjectName("GhostBtn")
        self.gh_btn.clicked.connect(
            lambda: webbrowser.open("https://github.com/0xSPRK/pzmm")
        )

        self.set_btn = QPushButton(tr("btn_settings"))
        self.set_btn.setObjectName("GhostBtn")
        self.set_btn.clicked.connect(self.open_settings)

        h_lay.addWidget(icon)
        h_lay.addLayout(title_box)
        h_lay.addStretch()
        h_lay.addWidget(self.gh_btn)
        h_lay.addWidget(self.set_btn)
        lay.addWidget(header)

        self.tabs = QTabWidget()
        lay.addWidget(self.tabs)

        self.workshop_tab = WorkshopTab(self.profile)
        self.workshop_tab.download_requested.connect(self.start_download)
        self.tabs.addTab(self.workshop_tab, tr("tab_workshop"))

        self.mods_tab = ModsTab()
        self.tabs.addTab(self.mods_tab, tr("tab_mods"))

        self.trouble_tab = TroubleTab()
        self.tabs.addTab(self.trouble_tab, tr("tab_trouble"))

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(5000)
        self.console.close()
        event.accept()

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec():
            if dlg.lang_changed:
                load_language(dlg.settings.get("language", "ru"))
                self.retranslate_ui()
            self.mods_tab.load_mods()

    def retranslate_ui(self):
        self.setWindowTitle(tr("PZMM"))
        self.title_lbl.setText(tr("app_title"))
        self.set_btn.setText(tr("btn_settings"))
        self.tabs.setTabText(0, tr("tab_workshop"))
        self.tabs.setTabText(1, tr("tab_mods"))
        self.tabs.setTabText(2, tr("tab_trouble"))
        self.workshop_tab.retranslate()
        self.mods_tab.retranslate()
        self.trouble_tab.retranslate()

    def start_download(self, ids, only_install):
        if self._worker and self._worker.isRunning():
            QMessageBox.information(self, tr("msg_err"), tr("msg_busy"))
            return

        s = load_settings()
        st = s.get("steamcmd_path", "")
        if not only_install and (not st or not os.path.exists(st)):
            QMessageBox.warning(self, tr("msg_err"), tr("msg_err_steamcmd"))
            return
        if not only_install and not resolve_download_root(s):
            QMessageBox.warning(self, tr("msg_err"), tr("msg_err_dlroot"))
            return

        self.console.show()
        self.console.txt.clear()
        self._worker = DownloadWorker(ids, s)
        self._worker.log_sig.connect(self.console.add_log)
        self._worker.prog_sig.connect(self.console.update_prog)
        self._worker.fin_sig.connect(self._on_download_finished)
        self._worker.start()

    def _on_download_finished(self, ok, fail):
        self._worker = None
        QMessageBox.information(
            self, tr("msg_done"),
            tr("msg_all_done") + "\n" + tr("msg_dl_summary", ok=ok, fail=fail),
        )
        self.mods_tab.load_mods()
