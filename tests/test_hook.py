"""Hook checks for SessionStart and Stop (the other events send real messages)."""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "claude-telegram"


PROMPT = {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": "do it"}]}}


def call(command: str) -> dict:
    tool_use = {"type": "tool_use", "name": "Bash", "input": {"command": command}}
    return {"type": "assistant", "message": {"role": "assistant", "content": [tool_use]}}


def result() -> dict:
    return {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]}}


def say(text: str) -> dict:
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def run(event: str, config: str = "", transcript: list | None = None) -> str:
    home = tempfile.mkdtemp()
    pathlib.Path(home, "config").write_text(config)
    log = pathlib.Path(home, "t.jsonl")
    log.write_text("".join(json.dumps(e) + "\n" for e in transcript or []))
    payload = json.dumps({"hook_event_name": event, "cwd": "/x/app", "stop_hook_active": False,
                          "transcript_path": str(log) if transcript is not None else ""})
    env = {**os.environ, "TG_NOTIFY_HOME": home}
    return subprocess.run([HOOK], input=payload, capture_output=True, text=True, check=True, env=env).stdout


def session_context(config: str = "") -> str:
    return json.loads(run("SessionStart", config))["hookSpecificOutput"]["additionalContext"]


class HookTest(unittest.TestCase):
    def test_session_start_puts_the_format_in_context(self):
        context = session_context()
        self.assertIn((ROOT / "FORMAT.md").read_text(), context)
        self.assertIn("Write in the user's language", context)

    def test_stop_reminds_when_work_sent_nothing(self):
        reply = json.loads(run("Stop", transcript=[PROMPT, call("make build"), result(), say("done")]))
        self.assertEqual(reply["decision"], "block")
        self.assertNotIn("\n", reply["reason"])
        self.assertLess(len(reply["reason"]), 120)

    def test_stop_is_quiet_after_a_summary(self):
        sent = [PROMPT, call("make build"), result(), call("tg-notify <<'EOF'\n✅ **x**\nEOF"), result(), say("ok")]
        self.assertEqual(run("Stop", transcript=sent), "")

    def test_mentions_are_not_sends(self):
        edits = [PROMPT, call("cat ~/.local/bin/tg-notify"), call("python3 - <<'X'\ntg-notify <<'EOF'\nX")]
        self.assertTrue(run("Stop", transcript=edits))
        self.assertEqual(run("Stop", transcript=[PROMPT, call("cd /x && ~/.local/bin/tg-notify --photos a.png")]), "")

    def test_stop_is_quiet_for_a_plain_reply(self):
        self.assertEqual(run("Stop", transcript=[PROMPT, say("short answer")]), "")

    def test_only_the_current_turn_counts(self):
        earlier = [PROMPT, call("tg-notify hi"), result(), say("ok")]
        self.assertTrue(run("Stop", transcript=earlier + [PROMPT, call("ls"), result(), say("x")]))

    def test_off_silences_both(self):
        self.assertEqual(run("Stop", 'HOOK_STOP="off"\n', [PROMPT, call("ls")]), "")
        self.assertEqual(run("SessionStart", 'HOOK_STOP="off"\n'), "")

    def test_language_label_and_own_format(self):
        spec = pathlib.Path(tempfile.mkdtemp(), "f.md")
        spec.write_text("MY FORMAT")
        context = session_context(f'MESSAGE_LANGUAGE="Russian"\nASK_LABEL="Your move"\nFORMAT_FILE="{spec}"\n')
        self.assertIn('Write in Russian; the ask label is "Your move"', context)
        self.assertTrue(context.endswith("MY FORMAT"))


if __name__ == "__main__":
    unittest.main()
