A Telegram message is a phone-screen summary of the result, nothing else. Less text, more signal: the user
opens the chat for details.

```
✅ **Project: outcome in ≤ 8 words**

- a result, a number or a link: one phone line (≤ 60 chars)
- 2–4 bullets; no process, no retelling of the task

## 🧪 Second topic        ← only when there is one
- …

>> logs, long details (shown collapsed)

> **Action needed:** the one decision or step, always last
```

- **Status mark** opens the title: ✅ done · 🔄 interim, still working · ❓ waiting for the user ·
  ⚠️ blocked or failed. A section heading may open with one emoji too; bullets get none.
- **The ask** is a `> ` quote, last, only when a decision or action is pending. A line starting
  `**Action needed:**` or `**Нужно от тебя:**` is quoted even without the `>`.
- **Markdown**: `**bold**`, `_italic_`, `` `code` `` for ids and paths, `[text](url)`, `- ` lists, `> ` quote,
  `>> ` collapsed quote, ``` code blocks. No tables, greetings, "I did". ≤ 1000 chars.
- **Spacing is automatic**: the renderer puts a blank line after the title and between blocks.
- **Send** with a heredoc, never `"…\n…"`: `tg-notify <<'EOF'` … `EOF`.
- **UI work** shows what it looks like: screenshots in the same message,
  `tg-notify --photos a.png b.png -- "text"` (one album, the text as its caption).
