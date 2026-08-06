import os
import shutil

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QDesktopServices, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView,
)

from ..core.localization import tr
from ..core.settings import load_settings
from ..core.registry import scan_mods


class ModsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_mods()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        top = QHBoxLayout()

        self.rf_btn = QPushButton(tr("btn_refresh"))
        self.rf_btn.setObjectName("ActionBtn")
        self.rf_btn.clicked.connect(self.load_mods)

        self.op_btn = QPushButton(tr("btn_open_folder"))
        self.op_btn.clicked.connect(self._open_folder)

        self.ds_btn = QPushButton(tr("btn_del_sel"))
        self.ds_btn.setObjectName("WarnBtn")
        self.ds_btn.clicked.connect(self._delete_selected)

        self.da_btn = QPushButton(tr("btn_del_all"))
        self.da_btn.setObjectName("DangerBtn")
        self.da_btn.clicked.connect(self._delete_all)

        top.addWidget(self.rf_btn)
        top.addWidget(self.op_btn)
        top.addStretch()
        top.addWidget(self.ds_btn)
        top.addWidget(self.da_btn)

        self.tb = QTableWidget()
        self.tb.setColumnCount(4)
        self.tb.setHorizontalHeaderLabels([
            tr("tbl_name"), tr("tbl_id"), tr("tbl_req"), tr("tbl_status"),
        ])
        self.tb.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tb.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tb.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tb.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tb.horizontalHeader().setFixedHeight(38)
        self.tb.verticalHeader().setVisible(False)
        self.tb.verticalHeader().setDefaultSectionSize(36)
        self.tb.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tb.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tb.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tb.setAlternatingRowColors(True)
        self.tb.setShowGrid(False)
        self.tb.setSortingEnabled(True)

        lay.addLayout(top)
        lay.addWidget(self.tb)

    def load_mods(self):
        self.tb.setSortingEnabled(False)
        self.tb.setRowCount(0)

        p = load_settings().get("game_mods_path")
        if not p or not os.path.exists(p):
            return

        mods = scan_mods(p)
        ids = {m["id"] for m in mods}

        self.tb.setRowCount(len(mods))
        for r, m in enumerate(mods):
            if m["versions"] == ["Base"]:
                display_name = m["name"]
            else:
                display_name = f"{m['name']} [{', '.join(m['versions'])}]"

            n = QTableWidgetItem(display_name)
            n.setData(Qt.ItemDataRole.UserRole, m["mod_dirs"])
            self.tb.setItem(r, 0, n)
            self.tb.setItem(r, 1, QTableWidgetItem(m["id"]))
            self.tb.setItem(r, 2, QTableWidgetItem(
                ", ".join(m["require"]) if m["require"] else tr("txt_none")
            ))

            if not m["require"]:
                st = QTableWidgetItem(tr("stat_ok"))
                st.setForeground(QColor(Qt.GlobalColor.green))
            else:
                ms = [x for x in m["require"] if x not in ids]
                if not ms:
                    st = QTableWidgetItem(tr("stat_all_inst"))
                    st.setForeground(QColor(Qt.GlobalColor.green))
                else:
                    st = QTableWidgetItem(tr("stat_miss", miss=", ".join(ms)))
                    st.setForeground(QColor(Qt.GlobalColor.red))
            self.tb.setItem(r, 3, st)

        self.tb.setSortingEnabled(True)

    def _open_folder(self):
        p = load_settings().get("game_mods_path")
        if p and os.path.exists(p):
            QDesktopServices.openUrl(QUrl.fromLocalFile(p))
        else:
            QMessageBox.warning(self, tr("msg_err"), tr("msg_err_folder"))

    def _delete_selected(self):
        sr = set(i.row() for i in self.tb.selectedItems())
        if not sr:
            return
        if QMessageBox.question(
            self, tr("msg_conf"), tr("msg_conf_del", count=len(sr))
        ) == QMessageBox.StandardButton.Yes:
            for r in sr:
                item = self.tb.item(r, 0)
                if not item:
                    continue
                for p in (item.data(Qt.ItemDataRole.UserRole) or []):
                    if p and os.path.isdir(p):
                        shutil.rmtree(p, ignore_errors=True)
            self.load_mods()

    def _delete_all(self):
        p = load_settings().get("game_mods_path")
        if not p or not os.path.exists(p):
            return
        if QMessageBox.warning(
            self, tr("msg_warn"), tr("msg_warn_del_all"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            for f in os.listdir(p):
                fp = os.path.join(p, f)
                try:
                    if os.path.isdir(fp) and not os.path.islink(fp):
                        shutil.rmtree(fp, ignore_errors=True)
                    elif os.path.isfile(fp):
                        os.remove(fp)
                except OSError:
                    pass
            self.load_mods()

    def retranslate(self):
        self.rf_btn.setText(tr("btn_refresh"))
        self.op_btn.setText(tr("btn_open_folder"))
        self.ds_btn.setText(tr("btn_del_sel"))
        self.da_btn.setText(tr("btn_del_all"))
        self.tb.setHorizontalHeaderLabels([
            tr("tbl_name"), tr("tbl_id"), tr("tbl_req"), tr("tbl_status"),
        ])
