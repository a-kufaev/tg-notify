"""Renderer checks: python3 -m unittest discover tests"""
import os
import pathlib
import subprocess
import tempfile
import unittest

RENDER = pathlib.Path(__file__).resolve().parents[1] / "bin" / "tg-notify-render"
EMPTY_HOME = tempfile.mkdtemp()  # no config: the tests see the defaults, not yours


def render(text: str, *flags: str, home: str = EMPTY_HOME) -> str:
    env = {**os.environ, "TG_NOTIFY_HOME": home}
    run = subprocess.run([RENDER, *flags], input=text, capture_output=True, text=True, check=True, env=env)
    return run.stdout.strip()


class RenderTest(unittest.TestCase):
    def test_title_is_bold_and_set_apart(self):
        self.assertEqual(render("✅ **Done**\n- a\n- b"), "<b>✅ Done</b>\n\n• a\n• b")

    def test_blocks_are_split_by_a_blank_line(self):
        self.assertEqual(render("T\ntext\n- a\nmore"), "<b>T</b>\n\ntext\n\n• a\n\nmore")

    def test_colon_and_heading_glue_the_next_block(self):
        self.assertEqual(render("T\nSteps:\n- a\n## Risks\n- b"), "<b>T</b>\n\nSteps:\n• a\n\n<b>Risks</b>\n• b")

    def test_ask_is_quoted_and_marks_the_title(self):
        self.assertEqual(
            render("Roam: x\n- a\n**Action needed:** merge"),
            "<b>❓ Roam: x</b>\n\n• a\n\n<blockquote><b>Action needed:</b> merge</blockquote>",
        )

    def test_status_mark_is_kept(self):
        self.assertTrue(render("⚠️ **CI red**\n> **Нужно от тебя:** look").startswith("<b>⚠️ CI red</b>"))

    def test_details_collapse(self):
        self.assertIn("<blockquote expandable>line 1\nline 2</blockquote>", render("T\n>> line 1\n>> line 2"))

    def test_code_and_snake_case_stay_literal(self):
        out = render("T\n- `a_b_c` and NOTION_DIGEST_TOKEN, _soft_")
        self.assertIn("<code>a_b_c</code> and NOTION_DIGEST_TOKEN, <i>soft</i>", out)

    def test_html_is_escaped(self):
        self.assertIn("a &lt; b &amp; c", render("T\na < b & c"))

    def test_link(self):
        self.assertIn('<a href="https://x.io/a">x</a>', render("T\n[x](https://x.io/a)"))

    def test_plain_keeps_the_layout(self):
        self.assertEqual(render("**T**\n- `a`\n> **Action needed:** b", "--plain"), "❓ T\n\n• a\n\n│ Action needed: b")

    def test_ask_label_from_config(self):
        home = tempfile.mkdtemp()
        pathlib.Path(home, "config").write_text('ASK_LABEL="Your move"\n')
        self.assertIn("<blockquote><b>Your move:</b> x</blockquote>", render("T\n**Your move:** x", home=home))

    def test_literal_backslash_n(self):
        self.assertEqual(render(r"T\n- a"), "<b>T</b>\n\n• a")


if __name__ == "__main__":
    unittest.main()
