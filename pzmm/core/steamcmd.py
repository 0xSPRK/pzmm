import os
import queue
import re
import subprocess
import threading

from .settings import PZ_APP_ID


class SteamCmdError(Exception):
    pass


class SteamCmdService:
    SUCCESS_RE = re.compile(r"Success\.\s+Downloaded item\s+(\d+)\s+to\s+\"([^\"]+)\"")
    ERROR_RE = re.compile(r"ERROR!\s+Download\s+item\s+(\d+)\s+failed\s*\((.*?)\)")

    def __init__(self, steamcmd_path, download_root, login="anonymous", password=""):
        self.steamcmd_path = steamcmd_path
        self.download_root = download_root
        self.login = login or "anonymous"
        self.password = password or ""
        self._stop = threading.Event()
        self._proc = None
        self._lock = threading.Lock()

    def stop(self):
        self._stop.set()
        with self._lock:
            proc = self._proc
        if proc is not None:
            try:
                proc.kill()
            except Exception:
                pass

    def workshop_content_dir(self):
        if not self.download_root:
            return ""
        return os.path.join(
            self.download_root, "steamapps", "workshop", "content", PZ_APP_ID
        )

    def build_command(self, ids):
        if not self.steamcmd_path:
            raise SteamCmdError("Путь к SteamCMD не задан.")
        cmd = [self.steamcmd_path]
        if self.download_root:
            cmd += ["+force_install_dir", self.download_root]
        if self.login and self.login.lower() != "anonymous":
            cmd += ["+login", self.login]
            if self.password:
                cmd += [self.password]
        else:
            cmd += ["+login", "anonymous"]
        cmd += ["+@ShutdownOnFailedCommand", "1"]
        for i in ids:
            cmd += ["+workshop_download_item", PZ_APP_ID, str(i)]
        cmd += ["+quit"]
        return cmd

    @staticmethod
    def _decode(raw):
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("cp866", errors="replace")

    def download(self, ids, log_cb=None, progress_cb=None, idle_timeout=900.0):
        if not ids:
            return {}
        ids = [str(i) for i in ids]

        if not os.path.isfile(self.steamcmd_path):
            raise SteamCmdError("SteamCMD не найден: %s" % self.steamcmd_path)
        if not self.download_root:
            raise SteamCmdError("Папка загрузок не задана.")
        os.makedirs(self.download_root, exist_ok=True)

        cmd = self.build_command(ids)
        shown = " ".join(cmd)
        if self.password:
            shown = shown.replace(self.password, "***")
        if log_cb:
            log_cb("> " + shown)

        flags = 0
        if os.name == "nt":
            flags = subprocess.CREATE_NO_WINDOW
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=flags,
        )
        with self._lock:
            self._proc = proc

        results = {i: "No result from SteamCMD" for i in ids}
        pending = set(ids)
        q = queue.Queue()

        def _reader():
            try:
                for raw in proc.stdout:
                    q.put(raw)
            finally:
                q.put(None)

        reader = threading.Thread(target=_reader, daemon=True)
        reader.start()

        def _resolved():
            if progress_cb:
                progress_cb(len(ids) - len(pending))

        try:
            while True:
                if self._stop.is_set():
                    proc.kill()
                    break
                try:
                    raw = q.get(timeout=idle_timeout)
                except queue.Empty:
                    proc.kill()
                    raise SteamCmdError("SteamCMD завис — прервано по таймауту.")
                if raw is None:
                    break
                line = self._decode(raw).rstrip()
                if log_cb:
                    log_cb(line)

                m = self.SUCCESS_RE.search(line)
                if m:
                    item = m.group(1)
                    if item in pending:
                        results[item] = "ok"
                        pending.discard(item)
                        _resolved()
                    continue
                m = self.ERROR_RE.search(line)
                if m:
                    item, reason = m.group(1), m.group(2).strip()
                    if item in pending:
                        results[item] = "Download error: %s" % reason
                        pending.discard(item)
                        _resolved()
                    continue
                if "FAILED" in line and "login" in line.lower():
                    results["__login__"] = line.strip()

            if proc.poll() is None:
                proc.wait(timeout=30)
        finally:
            with self._lock:
                self._proc = None
            if proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass

        for item in pending:
            results[item] = "No result from SteamCMD"
        _resolved()

        login_err = results.pop("__login__", None)
        if login_err and all(v != "ok" for v in results.values()):
            for key in list(results):
                results[key] = login_err
        return results
