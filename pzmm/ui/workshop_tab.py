import os
import re

from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QListWidget, QSplitter, QMessageBox, QFrame,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

from ..core.localization import tr


class SilentWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass


class WorkshopTab(QWidget):
    download_requested = pyqtSignal(list, bool)

    def __init__(self, profile, parent=None):
        super().__init__(parent)
        self.profile = profile
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        u_lay = QHBoxLayout()

        for b_txt, cb in [
            ("◀", lambda: self.bw.back()),
            ("▶", lambda: self.bw.forward()),
            ("↻", lambda: self.bw.reload()),
        ]:
            b = QPushButton(b_txt)
            b.setObjectName("NavBtn")
            b.clicked.connect(cb)
            u_lay.addWidget(b)

        self.url = QLineEdit("https://steamcommunity.com/app/108600/workshop/")
        self.url.returnPressed.connect(self._navigate)
        self.n_btn = QPushButton(tr("btn_nav_go"))
        self.n_btn.clicked.connect(self._navigate)
        u_lay.addWidget(self.url)
        u_lay.addWidget(self.n_btn)

        spl = QSplitter(Qt.Orientation.Horizontal)
        self.bw = QWebEngineView()
        self.bw.setPage(SilentWebEnginePage(self.profile, self.bw))
        self.bw.setUrl(QUrl(self.url.text()))
        self.bw.urlChanged.connect(lambda q: self.url.setText(q.toString()))
        self.bw.loadFinished.connect(self._inj_js)
        spl.addWidget(self.bw)

        rp = QFrame()
        rp.setObjectName("Card")
        r_lay = QVBoxLayout(rp)
        r_lay.setContentsMargins(14, 14, 14, 14)
        r_lay.setSpacing(10)

        self.ad_btn = QPushButton(tr("btn_add_queue"))
        self.ad_btn.setObjectName("ActionBtn")
        self.ad_btn.clicked.connect(self.add_q)

        self.q_list = QListWidget()

        self.rm_btn = QPushButton(tr("btn_rem_queue"))
        self.rm_btn.clicked.connect(self._rem_q)

        self.dl_btn = QPushButton(tr("btn_dl_queue"))
        self.dl_btn.setObjectName("SuccessBtn")
        self.dl_btn.clicked.connect(self._dl_q)

        self.up_btn = QPushButton(tr("btn_update_all"))
        self.up_btn.setObjectName("WarnBtn")
        self.up_btn.clicked.connect(self._up_all)

        self.q_lbl = QLabel(tr("lbl_queue"))
        self.db_lbl = QLabel(tr("lbl_db"))
        for w in [self.ad_btn, self.q_lbl, self.q_list, self.rm_btn, self.dl_btn, self.db_lbl, self.up_btn]:
            r_lay.addWidget(w)

        spl.addWidget(rp)
        spl.setSizes([850, 300])
        lay.addLayout(u_lay)
        lay.addWidget(spl)

    def _navigate(self):
        self.bw.setUrl(QUrl(self.url.text()))

    def _inj_js(self, ok):
        if ok:
            page = self.bw.page()
            if page:
                page.runJavaScript(
                    "var b=document.getElementById('cookie_prefs_popup_background'),"
                    "p=document.getElementById('cookie_prefs_popup');"
                    "if(b)b.style.display='none';if(p)p.style.display='none';"
                    "document.body.style.overflow='auto';"
                )

    def add_q(self):
        url = self.bw.url().toString() or self.url.text()
        m = re.search(r'(?:sharedfiles/filedetails/)?\?[^"\']*id=(\d+)', url)
        if not m:
            m = re.search(r'id=(\d+)', url)
        if m:
            item = m.group(1)
            if not self.q_list.findItems(item, Qt.MatchFlag.MatchExactly):
                self.q_list.addItem(item)
        else:
            QMessageBox.warning(self, tr("msg_err"), tr("msg_err_id"))

    def _rem_q(self):
        for i in self.q_list.selectedItems():
            self.q_list.takeItem(self.q_list.row(i))

    def _dl_q(self):
        if self.q_list.count() == 0:
            return
        ids = [self.q_list.item(i).text() for i in range(self.q_list.count())]
        self.q_list.clear()
        self._request_download(ids, False)

    def _up_all(self):
        from ..core.settings import load_settings, resolve_workshop_path
        p = resolve_workshop_path(load_settings())
        if p and os.path.exists(p):
            ids = [
                d for d in os.listdir(p)
                if os.path.isdir(os.path.join(p, d)) and d.isdigit()
            ]
            if ids:
                self._request_download(ids, False)
            else:
                QMessageBox.information(self, tr("msg_done"), tr("msg_err_ws"))
        else:
            QMessageBox.warning(self, tr("msg_err"), tr("msg_err_ws"))

    def _request_download(self, ids, only_install):
        self.download_requested.emit(ids, only_install)

    def retranslate(self):
        self.n_btn.setText(tr("btn_nav_go"))
        self.ad_btn.setText(tr("btn_add_queue"))
        self.rm_btn.setText(tr("btn_rem_queue"))
        self.dl_btn.setText(tr("btn_dl_queue"))
        self.up_btn.setText(tr("btn_update_all"))
        self.q_lbl.setText(tr("lbl_queue"))
        self.db_lbl.setText(tr("lbl_db"))
