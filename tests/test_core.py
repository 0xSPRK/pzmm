import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pzmm.core import settings as settings_mod
from pzmm.core import steamcmd, installer, mod_parser, registry


class ModParserTest(unittest.TestCase):
    def test_bom_handled(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "mod.info")
            with open(p, "wb") as f:
                f.write(b"\xef\xbb\xbfid=testmod\nname=Test Mod\nrequire=dep1, dep2\n")
            data = mod_parser.parse_mod_info(p)
            self.assertEqual(data["id"], "testmod")
            self.assertEqual(data["name"], "Test Mod")
            self.assertEqual(data["require"], ["dep1", "dep2"])

    def test_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "mod.info")
            with open(p, "w", encoding="utf-8") as f:
                f.write("something\n")
            data = mod_parser.parse_mod_info(p)
            self.assertEqual(data["id"], "")
            self.assertEqual(data["name"], "Unknown Mod")


class SteamCmdTest(unittest.TestCase):
    def test_build_command_anonymous(self):
        svc = steamcmd.SteamCmdService(r"C:\steam\steamcmd.exe", r"C:\dl", "anonymous", "")
        cmd = svc.build_command(["111", "222"])
        self.assertIn(r"+force_install_dir", cmd)
        self.assertIn(r"C:\dl", cmd)
        self.assertIn("+login", cmd)
        self.assertIn("anonymous", cmd)
        self.assertEqual(cmd.count("+workshop_download_item"), 2)
        self.assertEqual(cmd[-1], "+quit")

    def test_build_command_account_password_masked(self):
        svc = steamcmd.SteamCmdService(r"C:\steam\steamcmd.exe", r"C:\dl", "user", "secret")
        cmd = svc.build_command(["111"])
        self.assertIn("user", cmd)
        self.assertIn("secret", cmd)
        shown = " ".join(cmd).replace("secret", "***")
        self.assertNotIn("secret", shown)

    def test_workshop_content_dir(self):
        svc = steamcmd.SteamCmdService(r"C:\steam\steamcmd.exe", r"C:\dl")
        self.assertEqual(
            svc.workshop_content_dir(),
            os.path.join(r"C:\dl", "steamapps", "workshop", "content", "108600"),
        )

    def test_decode_cp866(self):
        svc = steamcmd.SteamCmdService(r"C:\steam\steamcmd.exe", r"C:\dl")
        raw = "тест".encode("cp866")
        self.assertEqual(svc._decode(raw), "тест")

    def test_result_regexes(self):
        self.assertIsNotNone(
            steamcmd.SteamCmdService.SUCCESS_RE.search(
                'Success. Downloaded item 2950902979 to "C:\\dl\\...\\2950902979"'
            )
        )
        m = steamcmd.SteamCmdService.ERROR_RE.search(
            "ERROR! Download item 123 failed (No match)."
        )
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "123")


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self._orig_settings_file = settings_mod.SETTINGS_FILE
        settings_mod.SETTINGS_FILE = os.path.join(
            tempfile.gettempdir(), "pzmm_test_settings.json"
        )
        if os.path.exists(settings_mod.SETTINGS_FILE):
            os.remove(settings_mod.SETTINGS_FILE)

    def tearDown(self):
        settings_mod.SETTINGS_FILE = self._orig_settings_file

    def test_resolve_download_root_from_steamcmd(self):
        with tempfile.TemporaryDirectory() as d:
            exe = os.path.join(d, "steamcmd.exe")
            open(exe, "w").close()
            s = {"steamcmd_path": exe, "download_root": "", "workshop_path": ""}
            self.assertEqual(settings_mod.resolve_download_root(s), d)

    def test_resolve_workshop_path_derived(self):
        s = {"steamcmd_path": "", "download_root": r"C:\dl", "workshop_path": ""}
        self.assertEqual(
            settings_mod.resolve_workshop_path(s),
            os.path.join(r"C:\dl", "steamapps", "workshop", "content", "108600"),
        )

    def test_resolve_workshop_path_explicit(self):
        s = {"steamcmd_path": "", "download_root": r"C:\dl", "workshop_path": r"C:\custom"}
        self.assertEqual(settings_mod.resolve_workshop_path(s), r"C:\custom")

    def test_save_load_roundtrip(self):
        settings_mod.save_settings({"a": 1, "steam_login": "anonymous"})
        self.assertEqual(settings_mod.load_settings()["a"], 1)


class InstallerTest(unittest.TestCase):
    def _make_item(self, base, files):
        mods = os.path.join(base, "mods")
        for rel in files:
            p = os.path.join(mods, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(rel)

    def test_sync_install_and_stale_removal(self):
        with tempfile.TemporaryDirectory() as d:
            item1 = os.path.join(d, "item1")
            item2 = os.path.join(d, "item2")
            game = os.path.join(d, "game")
            man = os.path.join(d, "manifest")
            os.makedirs(item2)
            self._make_item(item1, ["mod1/media/scripts/a.lua", "mod1/mod.info", "mod2/keep.txt"])
            self._make_item(item2, ["mod1/media/scripts/a.lua", "mod1/mod.info"])

            r1 = installer.install_item(item1, game, man, "100")
            self.assertGreater(r1["copied"], 0)
            self.assertEqual(r1["removed"], 0)
            self.assertTrue(os.path.isfile(os.path.join(game, "mod1", "media", "scripts", "a.lua")))
            self.assertTrue(os.path.isfile(os.path.join(game, "mod2", "keep.txt")))

            r2 = installer.install_item(item2, game, man, "100")
            self.assertIn(r2["copied"], (0, 2))
            self.assertGreaterEqual(r2["removed"], 1)
            self.assertFalse(os.path.isfile(os.path.join(game, "mod2", "keep.txt")))
            self.assertTrue(os.path.isfile(os.path.join(game, "mod1", "media", "scripts", "a.lua")))

    def test_no_mods_folder_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                installer.install_item(os.path.join(d, "empty"), os.path.join(d, "game"), os.path.join(d, "man"), "1")


class RegistryTest(unittest.TestCase):
    def test_scan_groups_versions(self):
        with tempfile.TemporaryDirectory() as d:
            pack = os.path.join(d, "Pack")
            v1 = os.path.join(pack, "BaseMod")
            v2 = os.path.join(pack, "AltVersion")
            for base in (pack, v1, v2):
                os.makedirs(base)
                with open(os.path.join(base, "mod.info"), "w", encoding="utf-8") as f:
                    f.write("id=same_mod\nname=Same\n")
            mods = registry.scan_mods(d)
            self.assertEqual(len(mods), 1)
            self.assertEqual(mods[0]["id"], "same_mod")
            self.assertEqual(sorted(mods[0]["versions"]), ["AltVersion", "Base", "BaseMod"])
            self.assertEqual(len(mods[0]["mod_dirs"]), 3)


if __name__ == "__main__":
    unittest.main()
