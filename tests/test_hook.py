"""Hook checks (Stop only: the other events send real messages)."""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "claude-telegram"


def stop(config: str = "") -> str:
    home = tempfile.mkdtemp()
    pathlib.Path(home, "config").write_text(config)
    event = json.dumps({"hook_event_name": "Stop", "cwd": "/x/app", "stop_hook_active": False})
    env = {**os.environ, "TG_NOTIFY_HOME": home}
    return subprocess.run([HOOK], input=event, capture_output=True, text=True, check=True, env=env).stdout


class StopHookTest(unittest.TestCase):
    def test_blocks_once_with_the_format(self):
        reply = json.loads(stop())
        self.assertEqual(reply["decision"], "block")
        self.assertIn("in the user's language", reply["reason"])
        self.assertIn((ROOT / "FORMAT.md").read_text(), reply["reason"])

    def test_off(self):
        self.assertEqual(stop('HOOK_STOP="off"\n'), "")

    def test_language_and_own_format(self):
        spec = pathlib.Path(tempfile.mkdtemp(), "f.md")
        spec.write_text("MY FORMAT")
        reason = json.loads(stop(f'MESSAGE_LANGUAGE="Russian"\nFORMAT_FILE="{spec}"\n'))["reason"]
        self.assertIn("in Russian", reason)
        self.assertTrue(reason.endswith("MY FORMAT"))


if __name__ == "__main__":
    unittest.main()
