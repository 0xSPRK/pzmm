import os

from PyQt6.QtCore import QThread, pyqtSignal

from .steamcmd import SteamCmdService, SteamCmdError
from .installer import install_item
from .settings import resolve_download_root, resolve_workshop_path, MANIFEST_DIR
from .localization import tr


class DownloadWorker(QThread):
    log_sig = pyqtSignal(str)
    prog_sig = pyqtSignal(int, int)
    fin_sig = pyqtSignal(int, int)

    def __init__(self, ids, settings, parent=None):
        super().__init__(parent)
        self.ids = [str(i) for i in ids]
        self.s = settings
        self._service = None

    def stop(self):
        if self._service:
            self._service.stop()

    def _auto_install(self, mid, gm):
        if not gm:
            self.log_sig.emit("Игровая папка модов не задана")
            return
        ws_item = os.path.join(resolve_workshop_path(self.s), mid)
        try:
            res = install_item(
                ws_item, gm, MANIFEST_DIR, mid,
                log_cb=lambda msg: self.log_sig.emit(msg),
            )
            self.log_sig.emit(
                tr("log_inst_sum", ws=mid,
                   copied=res["copied"], removed=res["removed"])
            )
        except FileNotFoundError as e:
            self.log_sig.emit(tr("log_err_inst", sub=mid, e=e))

    def run(self):
        st = self.s.get("steamcmd_path")
        root = resolve_download_root(self.s)
        gm = self.s.get("game_mods_path")
        auto = self.s.get("auto_install", True)
        tot = len(self.ids)
        self.prog_sig.emit(0, tot)

        service = SteamCmdService(
            st,
            root,
            login=self.s.get("steam_login", "anonymous"),
            password=self.s.get("steam_password", ""),
        )
        self._service = service

        results = {i: "error" for i in self.ids}
        try:
            results.update(service.download(
                self.ids,
                log_cb=lambda line: self.log_sig.emit(line),
                progress_cb=lambda count: self.prog_sig.emit(count, tot),
            ))
        except SteamCmdError as e:
            self.log_sig.emit(tr("log_err_st", e=e))
        except Exception as e:
            self.log_sig.emit(tr("log_err_st", e=e))

        ok = 0
        fail = 0
        for mid, status in results.items():
            if status == "ok":
                ok += 1
                if auto:
                    self._auto_install(mid, gm)
            else:
                fail += 1

        self.log_sig.emit(tr("log_done"))
        self.fin_sig.emit(ok, fail)
