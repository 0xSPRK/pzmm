DARK_STYLESHEET = """
/* ---------- Base ---------- */
QMainWindow { background-color: #0d0f17; }
QDialog {
    background-color: #131722;
    border: 1px solid #2a2d3d;
}
QWidget {
    background-color: #161a26;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Segoe UI Variable Text', 'Inter', 'Roboto', sans-serif;
    font-size: 13px;
}
QLabel { background-color: transparent; }

/* ---------- Buttons ---------- */
QPushButton {
    background-color: #232840;
    color: #cdd6f4;
    border: 1px solid #343a58;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}
QPushButton:hover { background-color: #2c3250; border-color: #4a5178; }
QPushButton:pressed { background-color: #1c2136; }
QPushButton:disabled { background-color: #1a1f30; color: #5b6074; border-color: #282c40; }
QPushButton:focus { border: 1px solid #89b4fa; }

QPushButton#NavBtn {
    background-color: #1d2133;
    border: 1px solid #343a58;
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 15px;
}
QPushButton#NavBtn:hover { background-color: #2c3250; }

QPushButton#GhostBtn {
    background-color: transparent;
    color: #a6adc8;
    border: 1px solid #343a58;
    border-radius: 8px;
    padding: 8px 16px;
}
QPushButton#GhostBtn:hover { border-color: #89b4fa; color: #ffffff; background-color: #232840; }

QPushButton#ActionBtn {
    background-color: #89b4fa;
    color: #0d0f17;
    border: none;
}
QPushButton#ActionBtn:hover { background-color: #a3c4ff; }
QPushButton#ActionBtn:pressed { background-color: #6f96dc; }

QPushButton#SuccessBtn {
    background-color: #a6e3a1;
    color: #0d0f17;
    border: none;
}
QPushButton#SuccessBtn:hover { background-color: #b9eeb4; }
QPushButton#SuccessBtn:pressed { background-color: #8ec98a; }

QPushButton#WarnBtn {
    background-color: #f9e2af;
    color: #0d0f17;
    border: none;
}
QPushButton#WarnBtn:hover { background-color: #fce9c2; }
QPushButton#WarnBtn:pressed { background-color: #ddc78c; }

QPushButton#DangerBtn {
    background-color: #f38ba8;
    color: #0d0f17;
    border: none;
}
QPushButton#DangerBtn:hover { background-color: #f8a2ba; }
QPushButton#DangerBtn:pressed { background-color: #d97a94; }

QPushButton#PrimaryBtn {
    background-color: #cba6f7;
    color: #0d0f17;
    border: none;
}
QPushButton#PrimaryBtn:hover { background-color: #d8baff; }
QPushButton#PrimaryBtn:pressed { background-color: #b08de0; }

/* ---------- Inputs ---------- */
QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {
    background-color: #0e1120;
    color: #cdd6f4;
    border: 1px solid #343a58;
    border-radius: 8px;
    padding: 7px 10px;
    selection-background-color: #6f96dc;
    selection-color: #ffffff;
}
QLineEdit:hover, QComboBox:hover, QTextEdit:hover, QPlainTextEdit:hover { border-color: #4a5178; }
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus { border: 1px solid #89b4fa; }

QComboBox::drop-down { border: none; width: 26px; }
QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #cdd6f4;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #1c2136;
    color: #cdd6f4;
    border: 1px solid #343a58;
    border-radius: 8px;
    padding: 4px;
    selection-background-color: #3a4a7a;
    selection-color: #ffffff;
}

QCheckBox { spacing: 9px; }
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 2px solid #4a5178;
    background-color: #0e1120;
}
QCheckBox::indicator:hover { border-color: #89b4fa; }
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

/* ---------- Tabs ---------- */
QTabWidget::pane {
    border: 1px solid #2a2d3d;
    border-radius: 8px;
    background-color: #131722;
    top: -1px;
}
QTabBar { background-color: transparent; }
QTabBar::tab {
    background-color: transparent;
    color: #9aa2bd;
    padding: 10px 24px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: none;
}
QTabBar::tab:hover { color: #cdd6f4; background-color: #1c2136; }
QTabBar::tab:selected {
    color: #ffffff;
    background-color: #1e2233;
    font-weight: 700;
    border-bottom: 2px solid #89b4fa;
}

/* ---------- Tables & Lists ---------- */
QTableWidget, QListWidget, QTreeWidget {
    background-color: #11141f;
    alternate-background-color: #171b29;
    color: #cdd6f4;
    border: 1px solid #2a2d3d;
    border-radius: 8px;
    gridline-color: transparent;
}
QTableWidget::item, QListWidget::item, QTreeWidget::item {
    padding: 7px 8px;
    border: none;
}
QTableWidget::item:hover, QListWidget::item:hover, QTreeWidget::item:hover { background-color: #1f2436; }
QTableWidget::item:selected, QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #3a4a7a;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #1a1f30;
    color: #9aa2bd;
    border: none;
    border-bottom: 1px solid #2a2d3d;
    padding: 10px 8px;
    font-weight: 700;
}
QHeaderView::section:hover { color: #cdd6f4; }

/* ---------- Scrollbars ---------- */
QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 4px;
}
QScrollBar::handle:vertical {
    background: #333a58;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #4a5178; }
QScrollBar:horizontal {
    background: transparent;
    height: 12px;
    margin: 4px;
}
QScrollBar::handle:horizontal {
    background: #333a58;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #4a5178; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

/* ---------- Progress ---------- */
QProgressBar {
    background-color: #11141f;
    border: 1px solid #2a2d3d;
    border-radius: 6px;
    text-align: center;
    color: #cdd6f4;
    font-weight: 600;
    min-height: 18px;
}
QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 5px;
}

/* ---------- Splitter / Misc ---------- */
QSplitter::handle { background-color: transparent; }
QSplitter::handle:hover { background-color: rgba(137, 180, 250, 40); }

QToolTip {
    background-color: #262b42;
    color: #cdd6f4;
    border: 1px solid #4a5178;
    border-radius: 6px;
    padding: 6px 10px;
}

QMenu {
    background-color: #1c2136;
    color: #cdd6f4;
    border: 1px solid #343a58;
    border-radius: 8px;
    padding: 6px;
}
QMenu::item { padding: 7px 24px; border-radius: 6px; }
QMenu::item:selected { background-color: #3a4a7a; color: #ffffff; }
QMenu::separator { height: 1px; background-color: #2a2d3d; margin: 4px 8px; }

/* ---------- App chrome ---------- */
QFrame#AppHeader {
    background-color: #1a2140;
    border: 1px solid #2f3550;
    border-radius: 8px;
}
QLabel#AppIcon {
    background-color: #89b4fa;
    color: #0d0f17;
    font-size: 20px;
    font-weight: 800;
    border-radius: 8px;
    padding: 8px 12px;
}
QLabel#AppTitle { font-size: 19px; font-weight: 700; color: #ffffff; }
QLabel#AppSubtitle { font-size: 12px; color: #9aa2bd; }

QFrame#Card {
    background-color: #1a1f30;
    border: 1px solid #2a2d3d;
    border-radius: 8px;
}

QTextEdit#Console {
    background-color: #0b0e17;
    color: #a6e3a1;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    border: 1px solid #2a2d3d;
    border-radius: 8px;
    padding: 8px;
}
"""
