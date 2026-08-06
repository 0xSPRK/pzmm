from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QCheckBox, QComboBox, QFileDialog,
)
from PyQt6.QtCore import Qt

import os

from ..core.settings import (
    load_settings, save_settings, resolve_workshop_path,
    detect_steamcmd_path, detect_workshop_path, detect_game_mods_path,
)
from ..core.localization import tr, get_available_languages


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("set_title"))
        self.resize(640, 360)
        self.settings = load_settings()
        self.lang_changed = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        self.ad_btn = QPushButton(tr("btn_autodetect"))
        self.ad_btn.setObjectName("GhostBtn")
        self.ad_btn.clicked.connect(self.autodetect)
        layout.addWidget(self.ad_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        def add_row(lbl, key, browse):
            row = QHBoxLayout()
            inp = QLineEdit(self.settings.get(key, ""))
            btn = QPushButton("…")
            btn.setFixedWidth(40)
            btn.clicked.connect(lambda: browse(inp))
            row.addWidget(QLabel(lbl))
            row.addWidget(inp)
            row.addWidget(btn)
            layout.addLayout(row)
            return inp

        self.st_inp = add_row(tr("set_steamcmd"), "steamcmd_path", self.br_f)
        self.dl_inp = add_row(tr("set_dl_root"), "download_root", self.br_d)
        self.ws_inp = add_row(tr("set_ws"), "workshop_path", self.br_d)
        self.gm_inp = add_row(tr("set_game"), "game_mods_path", self.br_d)

        self.ws_hint = QLabel(tr("set_ws_auto"))
        self.ws_hint.setStyleSheet("color: gray;")
        layout.addWidget(self.ws_hint)

        lg_row = QHBoxLayout()
        self.login_inp = QLineEdit(self.settings.get("steam_login", "anonymous"))
        lg_row.addWidget(QLabel(tr("set_login")))
        lg_row.addWidget(self.login_inp)
        layout.addLayout(lg_row)

        pw_row = QHBoxLayout()
        self.pass_inp = QLineEdit(self.settings.get("steam_password", ""))
        self.pass_inp.setEchoMode(QLineEdit.EchoMode.Password)
        pw_row.addWidget(QLabel(tr("set_password")))
        pw_row.addWidget(self.pass_inp)
        layout.addLayout(pw_row)

        self.auto_cb = QCheckBox(tr("set_auto"))
        self.auto_cb.setChecked(self.settings.get("auto_install", True))
        layout.addWidget(self.auto_cb)

        lang_lay = QHBoxLayout()
        self.lang_cb = QComboBox()
        self.lang_cb.addItems(get_available_languages())
        self.lang_cb.setCurrentText(self.settings.get("language", "ru"))
        lang_lay.addWidget(QLabel(tr("set_lang")))
        lang_lay.addWidget(self.lang_cb)
        layout.addLayout(lang_lay)

        sv_btn = QPushButton(tr("set_save"))
        sv_btn.setObjectName("SuccessBtn")
        sv_btn.clicked.connect(self.save_close)
        layout.addWidget(sv_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def br_f(self, i):
        p, _ = QFileDialog.getOpenFileName(self, "", "", "Exe (*.exe)")
        if p:
            i.setText(p)

    def autodetect(self):
        if not self.st_inp.text().strip():
            st = detect_steamcmd_path()
            if st:
                self.st_inp.setText(st)
                if not self.dl_inp.text().strip():
                    self.dl_inp.setText(os.path.dirname(st))
        if not self.ws_inp.text().strip():
            ws = detect_workshop_path()
            if ws:
                self.ws_inp.setText(ws)
        if not self.gm_inp.text().strip():
            gm = detect_game_mods_path()
            if gm:
                self.gm_inp.setText(gm)

    def br_d(self, i):
        p = QFileDialog.getExistingDirectory(self, "")
        if p:
            i.setText(p)

    def save_close(self):
        old_lang = self.settings.get("language", "ru")
        new_lang = self.lang_cb.currentText()
        self.lang_changed = old_lang != new_lang

        login = self.login_inp.text().strip()
        if not login:
            login = "anonymous"

        updated = {
            "steamcmd_path": self.st_inp.text().strip(),
            "download_root": self.dl_inp.text().strip(),
            "workshop_path": self.ws_inp.text().strip(),
            "game_mods_path": self.gm_inp.text().strip(),
            "auto_install": self.auto_cb.isChecked(),
            "language": new_lang,
            "steam_login": login,
            "steam_password": self.pass_inp.text(),
        }

        if not updated["workshop_path"]:
            updated["workshop_path"] = resolve_workshop_path(updated)

        self.settings.update(updated)
        save_settings(self.settings)
        self.accept()
