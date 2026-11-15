# tg-notify

Results from your scripts and AI agents, in your own Telegram, readable on a phone.

- **`tg-notify`**: a command that sends text, screenshots or files to your chat through your bot.
- **A renderer** that turns light Markdown into a clean message: bold title, spaced blocks, the ask in a quote.
- **A [Claude Code](https://claude.com/claude-code) hook**: every agent turn ends with a short summary in
  Telegram, questions and permission prompts arrive there too, each with a link back to the session.

```
✅ Billing: flaky test fixed, CI restarted

• a1b2c3d in main: baseline taken after the first event
• 10/10 local runs under load

┃ Action needed: approve the merge
```

## Quick start

Needs macOS or Linux with `zsh`, `python3` 3.9+ and `curl` (all preinstalled on a Mac).

```sh
git clone https://github.com/a-kufaev/tg-notify ~/Develop/tg-notify
~/Develop/tg-notify/install.sh
tg-notify --setup
```

1. `install.sh` links the command into `~/.local/bin`, creates `~/.config/tg-notify/config` and, if you use
   Claude Code, wires the hook. It ends with a checklist of what is ready and what is left.
2. `tg-notify --setup` asks for a bot token (get one from [@BotFather](https://t.me/BotFather): `/newbot`),
   asks you to press Start in the bot's chat, and sends a test message.

Another machine: the same three commands, with the same token or another bot.

## Sending

```sh
tg-notify <<'MSG'
✅ **Backup: done, 42 GB**

- 3 volumes, 18 min
MSG
```

| Command | Sends |
|---|---|
| `tg-notify "text"` or `tg-notify <<'MSG' … MSG` | a message. Use the heredoc for several lines |
| `tg-notify --photos a.png b.png -- "text"` | up to 10 images as one album, the text as its caption |
| `tg-notify --photo shot.png "caption"` | one image, up to 10 MB |
| `tg-notify --file build.log "caption"` | any file, up to 50 MB |
| `tg-notify --chat <id> [--thread <topic>] …` | to another chat or forum topic the bot is in |
| `tg-notify --format` | nothing: prints the message format |

Without a bot set up it prints a warning and exits 0, so a cron job never fails because of a notification.
Links never unfold into preview cards.

## Message format

[FORMAT.md](FORMAT.md) is the one place the format is defined:

- the title opens with a status: ✅ done · 🔄 interim · ❓ waiting for you · ⚠️ blocked or failed;
- 2–4 bullets, one phone line each;
- `## heading` for a second topic, `>>` lines for details shown collapsed;
- the ask last, as a `>` quote.

The renderer does the spacing on its own: a blank line after the title and between blocks, and a line
starting `**Action needed:**` becomes a quote even without `>`. If Telegram rejects the markup, the message
goes out as plain text with the same layout.

Markdown it understands: `**bold**`, `_italic_`, `~~strike~~`, `` `code` ``, `[text](https://url)`, `- ` and
`1. ` lists, `> ` quote, `>> ` collapsed quote, ``` code blocks.

## Claude Code

`install.sh` wires `hooks/claude-telegram` into `~/.claude/settings.json` (a backup goes to
`settings.json.bak`):

| When | What you get |
|---|---|
| a turn ends | the agent is handed FORMAT.md and sends a summary, unless the turn was a short reply |
| the agent asks a question | the question and its options |
| the agent needs a permission | `⏸ project: waiting for permission` |

In a Remote Control session every message ends with a link to that session, so you can answer from the
phone. Each turn-end summary costs the agent one short extra step; `HOOK_STOP="off"` turns it off.

## Settings

`~/.config/tg-notify/config`, created from [config.example](config.example). Changes apply to the next
message, nothing to restart.

| Key | Default | What |
|---|---|---|
| `HOOK_STOP` | `on` | turn-end summaries |
| `HOOK_QUESTION`, `HOOK_PERMISSION` | `on` | forward questions, permission prompts |
| `MESSAGE_LANGUAGE` | the user's language | language of the summaries, e.g. `Russian` |
| `FORMAT_FILE` | `FORMAT.md` | your own format file |
| `ASK_LABEL` | none | your ask label, quoted like `Action needed` |
| `QUESTION_TITLE`, `PERMISSION_TITLE` | `question`, `waiting for permission` | titles of forwarded messages |
| `REPLY_LABEL`, `OPEN_LABEL` | `Reply in chat`, `Open Claude Code` | the link at the end |
| `SETUP_TEXT` | `✅ tg-notify connected` | the `--setup` test message |

The same folder holds `token` and `chat_id` (readable only by you). `TG_NOTIFY_HOME` points to another
folder.

## Updating and changing it

Everything is a symlink into the repo, so a change in the repo is live at once.

| You want to | Do | Live from |
|---|---|---|
| get the latest version | `git pull` | the next message |
| change the format | edit `FORMAT.md`, or set `FORMAT_FILE` to your own file so `git pull` never conflicts | the next turn end, in every session, running ones too |
| change how messages look | edit `bin/tg-notify-render`, add a case to `tests/test_render.py`, run the tests | the next message |
| change what the hook sends | edit `hooks/claude-telegram`, run the tests | the next hook event |
| change which events are wired | edit `wire_hook` in `install.sh`, run `./install.sh` | new sessions |
| tune labels, language, on/off | `~/.config/tg-notify/config` | the next message |

Check before sending:

```sh
python3 -m unittest discover tests        # renderer and hook
tg-notify-render < message.md             # the HTML Telegram will get, nothing is sent
tg-notify-render --plain < message.md     # the plain-text fallback
```

`./install.sh` is safe to run any time: it repairs missing links and settings and prints the checklist.

## Troubleshooting

| Symptom | Cause, fix |
|---|---|
| nothing arrives | run `tg-notify test` in a terminal and read the warning; usually `tg-notify --setup` is needed |
| `--setup`: no message from you | press Start in the bot's chat first. If you did, something else reads the bot's updates (a webhook, another script): stop it for the setup |
| the agent sends nothing | `HOOK_STOP` is off, or the hook is not wired: run `./install.sh` and check its list |
| raw `**` in a message | Telegram rejected the HTML, and the plain fallback is from an old version: `git pull` |
| a summary in the wrong language | set `MESSAGE_LANGUAGE` |

## Uninstall

```sh
~/Develop/tg-notify/install.sh --uninstall
```

Removes the links and the hook entries. Your token, chat and config stay in `~/.config/tg-notify`.

## Files

| Path | Role |
|---|---|
| `bin/tg-notify` | the command: send, setup |
| `bin/tg-notify-render` | Markdown → Telegram HTML or plain text; layout rules in its header |
| `hooks/claude-telegram` | the Claude Code hook |
| `lib/tg_notify_config.py` | reads the config for the Python parts |
| `FORMAT.md` | how a message reads |
| `config.example` | every setting, with comments |
| `install.sh` | install, repair, uninstall |
| `tests/` | renderer and hook tests |

MIT license.
