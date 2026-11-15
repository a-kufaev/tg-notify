"""Hook checks for SessionStart and Stop (the other events send real messages)."""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "claude-telegram"


def run(event: str, config: str = "") -> str:
    home = tempfile.mkdtemp()
    pathlib.Path(home, "config").write_text(config)
    payload = json.dumps({"hook_event_name": event, "cwd": "/x/app", "stop_hook_active": False})
    env = {**os.environ, "TG_NOTIFY_HOME": home}
    return subprocess.run([HOOK], input=payload, capture_output=True, text=True, check=True, env=env).stdout


def session_context(config: str = "") -> str:
    return json.loads(run("SessionStart", config))["hookSpecificOutput"]["additionalContext"]


class HookTest(unittest.TestCase):
    def test_session_start_puts_the_format_in_context(self):
        context = session_context()
        self.assertIn((ROOT / "FORMAT.md").read_text(), context)
        self.assertIn("Write in the user's language", context)

    def test_stop_is_one_short_line(self):
        reply = json.loads(run("Stop"))
        self.assertEqual(reply["decision"], "block")
        self.assertNotIn("\n", reply["reason"])
        self.assertLess(len(reply["reason"]), 120)

    def test_off_silences_both(self):
        self.assertEqual(run("Stop", 'HOOK_STOP="off"\n'), "")
        self.assertEqual(run("SessionStart", 'HOOK_STOP="off"\n'), "")

    def test_language_label_and_own_format(self):
        spec = pathlib.Path(tempfile.mkdtemp(), "f.md")
        spec.write_text("MY FORMAT")
        context = session_context(f'MESSAGE_LANGUAGE="Russian"\nASK_LABEL="Your move"\nFORMAT_FILE="{spec}"\n')
        self.assertIn('Write in Russian; the ask label is "Your move"', context)
        self.assertTrue(context.endswith("MY FORMAT"))


if __name__ == "__main__":
    unittest.main()
