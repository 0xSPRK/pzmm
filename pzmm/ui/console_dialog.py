from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit,
)
from PyQt6.QtCore import Qt

from ..core.localization import tr


class ConsoleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("cons_title"))
        self.resize(720, 460)
        self.setObjectName("ConsoleDialog")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)
        self.lbl = QLabel(tr("cons_wait"))
        self.bar = QProgressBar()
        self.txt = QTextEdit()
        self.txt.setObjectName("Console")
        self.txt.setReadOnly(True)
        lay.addWidget(self.lbl)
        lay.addWidget(self.bar)
        lay.addWidget(self.txt)

    def update_prog(self, c, t):
        self.lbl.setText(tr("cons_prog", cur=c, tot=t))
        self.bar.setValue(int((c / t) * 100) if t > 0 else 0)

    def add_log(self, t):
        self.txt.append(t)
        sb = self.txt.verticalScrollBar()
        sb.setValue(sb.maximum())
